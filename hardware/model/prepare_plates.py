"""Create and slice A1 projects using the installed Bambu Studio CLI.

Resolve bundled profile inheritance before giving settings to the CLI.
Never connect to a printer or start a print. Intermediate G-code stays in build/.
"""
from pathlib import Path
import json
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import sys
import shutil

ROOT=Path(__file__).resolve().parents[1]
PROFILES=Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
BAMBU='/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
BUILD=ROOT/'build/slicer';BUILD.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'output'

def profile(kind,name):
    src=json.loads((PROFILES/kind/(name+'.json')).read_text())
    dst=profile(kind,src['inherits']) if src.get('inherits') else {}
    for inc in src.get('include',[]):dst.update(profile(kind,inc))
    dst.update(src)
    dst.pop('inherits',None);dst.pop('include',None)
    return dst

machine=profile('machine','Bambu Lab A1 0.4 nozzle')
process=profile('process','0.20mm Standard @BBL A1')
process.update({'name':'Movie Time - A1 PLA 0.20','from':'User','is_custom_defined':'1',
                'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5',
                'sparse_infill_density':'15%','sparse_infill_pattern':'gyroid',
                'brim_type':'no_brim','brim_width':'0','skirt_loops':'0',
                'enable_support':'0','elefant_foot_compensation':'0.15',
                'outer_wall_speed':['60'],'initial_layer_speed':['30'],
                'initial_layer_infill_speed':['50'],'enable_prime_tower':'0',
                'curr_bed_type':'Textured PEI Plate'})
filament=profile('filament','Generic PLA @BBL A1')
filament['filament_colour']=['#DDD2B8']
for name,data in [('machine',machine),('process',process),('filament',filament)]:
    (BUILD/(name+'.json')).write_text(json.dumps(data,indent=2))

PLATES={
 '01_fit_tests': ['10_button_fit_test','11_case_fit_test','04_button_play','05_button_pause','06_button_stop','07_switch_carrier','08_switch_retainer'],
 '02_base': ['01_base'],
 '03_lid': ['02_lid'],
 '04_case_deck_and_hardware': ['03_case_deck','07_switch_carrier','08_switch_retainer','09_led_lens'],
 '05_sage_buttons': ['04_button_play','05_button_pause','06_button_stop'],
}
report_path=OUT/'validation'/'slicer_report.json'
reports=json.loads(report_path.read_text()) if report_path.exists() else {}
selection=set(sys.argv[1:])
for name,parts in PLATES.items():
    if selection and name not in selection:continue
    print('Preparing and slicing',name,flush=True)
    cfg=dict(filament)
    if name=='05_sage_buttons':cfg['filament_colour']=['#8EAA80']
    f=BUILD/(name+'_filament.json');f.write_text(json.dumps(cfg))
    dest=OUT/'plates'/(name+'.3mf')
    directory=BUILD/name;directory.mkdir(exist_ok=True)
    cmd=[BAMBU,'--debug','2','--load-settings',str(BUILD/'machine.json')+';'+str(BUILD/'process.json'),
         '--load-filaments',str(f),'--arrange','1','--orient','0','--ensure-on-bed',
         '--slice','0','--outputdir',str(directory),'--export-3mf',dest.name]
    cmd += [str(OUT/'stl'/(p+'.stl')) for p in parts]
    log=BUILD/(name+'.log')
    with log.open('w') as stream:
        result=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,cwd=directory)
    if (directory/dest.name).exists():shutil.copy2(directory/dest.name,dest)
    reports[name]={'exit_code':result.returncode,'project_exists':dest.exists(),'parts':parts}
    print(name,reports[name],flush=True)
    if result.returncode:
        print(log.read_text()[-7000:],flush=True)
        raise RuntimeError('Bambu Studio failed: '+name)
    if dest.exists():
        with zipfile.ZipFile(dest) as archive:
            reports[name]['archive_files']=archive.namelist()
    for candidate in directory.rglob('*.json'):
        if candidate.stat().st_size<150000:
            try: reports[name][candidate.name]=json.loads(candidate.read_text())
            except (UnicodeDecodeError,json.JSONDecodeError):pass
    (OUT/'validation'/'slicer_report.json').write_text(json.dumps(reports,indent=2)+'\n')
