"""Check DVD/Blu-ray insertion against the actual assembly STEP solids.

Run independently after a build; does not regenerate or change print geometry.
Dimensions are spine length x insertion depth x closed-case thickness in mm.
"""
from pathlib import Path
import hashlib
import json
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
P = json.loads((ROOT / 'model/parameters.json').read_text())


def check_case_fit():
    parts = {p.stem: cq.importers.importStep(str(p)).val()
             for p in sorted((OUT / 'step').glob('0*.step'))}
    assert len(parts) == 9, 'Expected all nine assembled print parts'
    slot_left = P['slot_left']
    slot_width = P['case_spine'] + 2 * P['case_side_clearance']
    slot_right = slot_left + slot_width
    slot_height = P['slot_top'] - P['deck_height']
    stop = P['case_depth'] * P['insertion_fraction']
    profiles = [
        ('Standard DVD', P['case_spine'], P['case_depth'], P['case_thickness']),
        ('Blu-ray 11 mm', 170, 135, 11),
        ('Blu-ray 12.5 mm', 170, 135, 12.5),
        ('Blu-ray 14 mm', 170, 135, 14),
        ('Blu-ray allowance envelope (not a brand specification)', 172, 135, 15),
    ]
    report = {
        'slot_mm': [slot_width, round(slot_height, 3)],
        'insertion_depth_mm': stop,
        'method': 'Solid intersection of full straight insertion sweeps with all nine assembled STEP parts; 0.01 mm offset at deck and rear stop excludes intended contact.',
        'sources': [
            'https://www.omc-medien.de/verpackungen/blu-ray-verpackungen',
            'https://www.vantiva.com/app/uploads/2023/02/EDS021Issue5BDCaseBookletInsertInlaySpecs.pdf',
        ],
        'profiles': [],
        'physical_fit_verified': False,
        'nfc_reading_verified': False,
        'nfc_instruction': 'Keep the case aligned to the LEFT of the slot and seated against the rear stop. Tag center: 25 mm from left short edge, 104 mm from spine, on underside. These coordinates assume a 135 mm deep case. Bench-test each case format before permanent placement.',
        'step_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted((OUT / 'step').glob('0*.step'))},
    }
    failures = []
    for label, width, depth, thickness in profiles:
        entry = {'name': label, 'case_mm': [width, depth, thickness],
                 'height_clearance_mm': round(slot_height - thickness, 3),
                 'total_side_clearance_mm': round(slot_width - width, 3),
                 'spine_projection_mm': round(depth - stop, 3),
                 'insertion_fraction': round(stop / depth, 4), 'sweeps': {}}
        assert thickness < slot_height and width < slot_width
        positions = {'left': slot_left + P['case_side_clearance'],
                     'center': slot_left + (slot_width - width) / 2,
                     'right': slot_right - P['case_side_clearance'] - width}
        for alignment, x in positions.items():
            sweep = cq.Workplane('XY').box(width, depth + stop - 0.01, thickness,
                                          centered=False).translate((x, -depth, P['deck_height'] + 0.01)).val()
            collisions = []
            for name, shape in parts.items():
                volume = sweep.intersect(shape).Volume()
                if volume > 0.02:
                    collisions.append({'part': name, 'volume_mm3': round(volume, 4)})
            entry['sweeps'][alignment] = {
                'collisions': collisions,
                'tag_center_offset_from_reader_x_mm': round(x + 25 - P['pn532_centre'][0], 3),
            }
            if collisions:
                failures.append([label, alignment, collisions])
        report['profiles'].append(entry)
        print(label, entry['case_mm'], 'clearance', entry['height_clearance_mm'], 'mm', flush=True)
    report['all_insertion_sweeps_clear'] = not failures
    (OUT / 'validation/case_compatibility.json').write_text(json.dumps(report, indent=2) + '\n')
    assert not failures, failures
    print('All 15 DVD/Blu-ray insertion sweeps passed; hardware NFC test still required.', flush=True)


if __name__ == '__main__':
    check_case_fit()
