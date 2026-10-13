"""Bundle the spring prototype and its unchanged baseline enclosure files."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/spring_guide'
mechanics=json.loads((OUT/'validation/mechanics.json').read_text())
slicing=json.loads((OUT/'validation/slicer.json').read_text())
assert mechanics['all_checks_passed']
assert len(slicing)==3
assert (OUT/'preview/spring_mechanism.png').exists()
unchanged=[]
with zipfile.ZipFile(ROOT/'output/Movie_Time_A1_v2_1.zip') as old:
    for directory in ('stl','step','plates'):
        for path in (ROOT/'output'/directory).glob('*'):
            rel=str(path.relative_to(ROOT))
            assert old.read('Movie_Time_A1_v2_1/'+rel)==path.read_bytes(),rel
            unchanged.append(rel)
summary={
    'release':'spring_guide_prototype',
    'printer':'Bambu Lab A1 0.4 nozzle',
    'baseline_print_artifacts_unchanged':unchanged,
    'retrofit':'Replacement lid + one PETG spring + two M2 x 12 mm screws',
    'test_fixture':'PLA bed and bridge; one additional M2 x 16 mm fixture screw',
    'cad_insertion_positions_checked':len(mechanics['insertion_stages']),
    'all_geometry_checks_passed':True,
    'physically_printed':False,
    'spring_force_and_self_alignment_verified':False,
    'nfc_verified':False,
    'print_estimates':slicing,
}
test_record=OUT/'validation/physical_test.json'
if test_record.exists():
    physical=json.loads(test_record.read_text())
    summary.update({'physically_printed':physical['physically_printed_and_tested'],
                    'self_alignment_test_result':physical['outcome'],
                    'superseded_by':'spring_guide_v2'})
(OUT/'validation/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
paths=[ROOT/p for p in ('README.md','ASSEMBLY.md','SPRING_GUIDE.md','requirements.txt')]
for directory in ('model','firmware','output/stl','output/step','output/plates',
                  'output/preview','output/validation','output/spring_guide'):
    paths += [p for p in (ROOT/directory).rglob('*') if p.is_file()
              and '__pycache__' not in p.parts and p.name!='SHA256.json' and p.suffix!='.zip']
paths=sorted(set(paths))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
dest=ROOT/'output/Movie_Time_A1_spring_prototype.zip'
prefix='Movie_Time_A1_spring_prototype/'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in paths:archive.write(p,prefix+str(p.relative_to(ROOT)))
    archive.writestr(prefix+'SHA256.json',json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(dest) as archive:
    assert archive.testzip() is None
    for relative,digest in manifest.items():
        assert hashlib.sha256(archive.read(prefix+relative)).hexdigest()==digest
print('Packaged',dest,len(paths)+1,'files;',dest.stat().st_size,'bytes')
