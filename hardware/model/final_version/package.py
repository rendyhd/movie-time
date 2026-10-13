"""Complete final print package with five print files at its top level."""
from pathlib import Path
import json,zipfile,shutil,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/final_version'
BUNDLE=ROOT/'output/Movie_Time_Final'


def copy(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)


def run():
    BUNDLE.mkdir(parents=True,exist_ok=True)
    reports=json.loads((OUT/'validation/slicer.json').read_text())
    motion=json.loads((OUT/'validation/motion.json').read_text())
    geometry=json.loads((OUT/'validation/geometry.json').read_text())
    buttons=json.loads((OUT/'validation/buttons.json').read_text())
    assert motion['all_contact_solves_converged'] and geometry['all_solid_clearance_checks_passed'] and buttons['all_solid_checks_passed']
    for p in sorted((OUT/'plates').glob('*.3mf')):copy(p,BUNDLE/p.name)
    assert len(list(BUNDLE.glob('*.3mf')))==5
    copy(OUT/'plates/01_Spring_PETG.3mf',ROOT/'output/Spring_PETG_Reinforced.3mf')
    guide=(ROOT/'FINAL_VERSION.md').read_text()
    guide=guide.replace('`output/Movie_Time_Final_A1.zip`','`Movie_Time_Final_A1.zip`')
    guide=guide.replace('Individual projects are also in `output/final_version/plates/`.','Open the top-level `.3mf` files directly in Bambu Studio.')
    guide=guide.replace('output/final_version/preview/','reference/preview/')
    guide=guide.replace('[Spring_PETG_Reinforced.3mf](output/Spring_PETG_Reinforced.3mf)',
                        '[01_Spring_PETG.3mf](01_Spring_PETG.3mf)')
    guide=guide.replace('output/Holder_Reach_Fix_PLA.3mf','reference/optional/Holder_Reach_Fix_PLA.3mf')
    guide=guide.replace('output/Buttons_Fit_Fix_PLA.3mf','reference/optional/Buttons_Fit_Fix_PLA.3mf')
    guide=guide.replace('output/pdf/Movie_Time_Assembly_and_Wiring.pdf','Assembly_and_Wiring_Guide.pdf')
    guide=guide.replace('(ASSEMBLY.md)','(Assembly_and_wiring.md)')
    guide=guide.replace('[ASSEMBLY.md](ASSEMBLY.md)','[Assembly_and_wiring.md](Assembly_and_wiring.md)')
    (BUNDLE/'README.md').write_text(guide)
    assembly=(ROOT/'ASSEMBLY.md').read_text()
    assembly=assembly.replace('[FINAL_VERSION.md](FINAL_VERSION.md)','[README.md](README.md)')
    assembly=assembly.replace('`output/final_version/plates/`','the top level of this package')
    assembly=assembly.replace('output/preview/','reference/preview/')
    assembly=assembly.replace('output/final_version/preview/','reference/preview/')
    assembly=assembly.replace('output/Holder_Reach_Fix_PLA.3mf','reference/optional/Holder_Reach_Fix_PLA.3mf')
    assembly=assembly.replace('output/Buttons_Fit_Fix_PLA.3mf','reference/optional/Buttons_Fit_Fix_PLA.3mf')
    assembly=assembly.replace('output/final_version/optional/','reference/optional/')
    assembly=assembly.replace('output/pdf/Movie_Time_Assembly_and_Wiring.pdf','Assembly_and_Wiring_Guide.pdf')
    assembly=assembly.replace('The complete print package is [Movie_Time_Final_A1.zip](output/Movie_Time_Final_A1.zip).',
                              'All five .3mf projects are at the top level of this package.')
    assembly=assembly.replace('`output/plates/01_fit_tests.3mf`','`reference/optional/Button_and_case_fit_PLA.3mf`')
    (BUNDLE/'Assembly_and_wiring.md').write_text(assembly)
    copy(ROOT/'output/pdf/Movie_Time_Assembly_and_Wiring.pdf',BUNDLE/'Assembly_and_Wiring_Guide.pdf')
    for folder in ('stl','step','preview','validation'):
        for p in (OUT/folder).iterdir():
            if p.is_file() and p.name!='SHA256.json':copy(p,BUNDLE/'reference'/folder/p.name)
    for name in ('electronics.png','button_wiring.png','tag_placement.png','exploded.png'):
        copy(ROOT/'output/preview'/name,BUNDLE/'reference/preview'/name)
    for p in (ROOT/'firmware').glob('*.yaml'):copy(p,BUNDLE/'firmware'/p.name)
    copy(OUT/'optional/Button_and_case_fit_PLA.3mf',BUNDLE/'reference/optional/Button_and_case_fit_PLA.3mf')
    copy(ROOT/'output/Buttons_Fit_Fix_PLA.3mf',BUNDLE/'reference/optional/Buttons_Fit_Fix_PLA.3mf')
    copy(ROOT/'output/Holder_Reach_Fix_PLA.3mf',BUNDLE/'reference/optional/Holder_Reach_Fix_PLA.3mf')
    copy(ROOT/'output/spring_guide/plates/01_test_fixture_PLA.3mf',BUNDLE/'reference/optional/Existing_spring_fixture_PLA.3mf')
    # The existing unchanged parts are copied byte-for-byte, not regenerated.
    unchanged={}
    for new,old in [('03_Base_PLA','02_base')]:
        a=(OUT/'plates'/f'{new}.3mf').read_bytes();b=(ROOT/'output/plates'/f'{old}.3mf').read_bytes()
        assert a==b,new
        unchanged[new]=hashlib.sha256(a).hexdigest()
    with zipfile.ZipFile(ROOT/'output/Movie_Time_Final_A1_original.zip') as original:
        for folder,name in [('','02_Cute_Lid_PLA.3mf'),
                            ('reference/stl/','02_cute_lid_single_leaf.stl'),
                            ('reference/step/','02_cute_lid_single_leaf.step')]:
            original_bytes=original.read('Movie_Time_Final/'+folder+name)
            current=BUNDLE/(folder+name)
            assert current.read_bytes()==original_bytes,('lid changed unexpectedly',name)
        unchanged['02_Cute_Lid_PLA']=hashlib.sha256((BUNDLE/'02_Cute_Lid_PLA.3mf').read_bytes()).hexdigest()
    prior=ROOT/'output/before_button_reach_fix/final_version'
    assert (prior/'plates/01_Spring_PETG.3mf').read_bytes()==(OUT/'plates/01_Spring_PETG.3mf').read_bytes()
    unchanged['01_Spring_PETG']=hashlib.sha256((OUT/'plates/01_Spring_PETG.3mf').read_bytes()).hexdigest()
    for name in buttons['unchanged_step_sha256']:
        for folder,ext in [('step','step'),('stl','stl')]:
            assert (prior/folder/f'{name}.{ext}').read_bytes()==(OUT/folder/f'{name}.{ext}').read_bytes(),name
    summary={'release':'Movie Time Final — forward switch holder for measured actuator reach','printer':'Bambu Lab A1 0.4 mm',
             'new_printed_parts':['switch carrier','switch retainer'],
             'unchanged_printed_parts':['play/pause/stop caps','cute lid','base','deck','LED lens','reinforced PETG spring'],
             'spring_parts_count':1,'sliding_joints_count':0,
             'all_final_plates_sliced':True,'all_final_plates_support_free':True,
             'final_parts_estimated_grams':round(sum(r['estimated_grams'] for r in reports.values()),2),
             'final_parts_estimated_seconds':sum(r['estimated_seconds'] for r in reports.values()),
             'contact_motion_poses':len(motion['contact_motion_checks']),
             'rigid_solid_motion_poses':len(geometry['case_motion_poses']),
             'physically_tested':False,'automatic_alignment_verified':False,'nfc_read_verified':False,
             'previous_revision_physical_test':json.loads((OUT/'validation/previous_physical_test.json').read_text()),
             'force_tuning':json.loads((OUT/'validation/force_tuning.json').read_text()),
             'reinforced_joint':json.loads((OUT/'validation/root_joint.json').read_text()),
             'buttons':buttons,'replacement_holder_plate':json.loads((OUT/'validation/holder_plate.json').read_text()),
             'previous_button_measurements':json.loads((OUT/'validation/button_reach_physical_report.json').read_text()),
             'replacement_button_plate':json.loads((OUT/'validation/button_plate.json').read_text()),
             'assembly_audit':json.loads((OUT/'validation/assembly_audit.json').read_text()),
             'wiring_audit':json.loads((OUT/'validation/wiring_audit.json').read_text()),
             'unchanged_plate_sha256':unchanged}
    (OUT/'validation/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    copy(OUT/'validation/summary.json',BUNDLE/'reference/validation/summary.json')
    files=[p for p in BUNDLE.rglob('*') if p.is_file() and p.name!='SHA256.json']
    manifest={str(p.relative_to(BUNDLE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    (BUNDLE/'reference/validation/SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=ROOT/'output/Movie_Time_Final_A1.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(BUNDLE.rglob('*')):
            if p.is_file():z.write(p,Path('Movie_Time_Final')/p.relative_to(BUNDLE))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    local=[ROOT/'FINAL_VERSION.md',ROOT/'README.md',ROOT/'ASSEMBLY.md']
    local+=list((ROOT/'model/final_version').glob('*.py'))
    local+=list((ROOT/'model/button_fit_fix').glob('*.py'))
    local+=list((ROOT/'model/assembly_guide').glob('*.py'))
    local+=[ROOT/'model/build_model.py',ROOT/'model/parameters.json']
    local+=[p for p in OUT.rglob('*') if p.is_file() and p.name!='SHA256.json']
    (OUT/'validation/SHA256.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(local)},indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    print('Package',archive,'bytes',archive.stat().st_size,flush=True)


if __name__=='__main__':run()
