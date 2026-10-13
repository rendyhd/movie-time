"""Slice the spring retrofit and its test fixture for A1; never starts a print."""
from pathlib import Path
import json
import subprocess
import shutil
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/spring_guide'
BUILD=ROOT/'build/spring_guide/slicer'
BUILD.mkdir(parents=True,exist_ok=True)
PROFILES=Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
BAMBU='/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'


def profile(kind,name):
    src=json.loads((PROFILES/kind/(name+'.json')).read_text())
    result=profile(kind,src['inherits']) if src.get('inherits') else {}
    for inc in src.get('include',[]):result.update(profile(kind,inc))
    result.update(src)
    result.pop('inherits',None);result.pop('include',None)
    return result


def run():
    machine=profile('machine','Bambu Lab A1 0.4 nozzle')
    (BUILD/'machine.json').write_text(json.dumps(machine))
    plates={
        '01_test_fixture_PLA':(['14_spring_test_bed','15_spring_test_mount'],'PLA'),
        '02_springs_PETG':(['12_spring_standard_PETG','13_spring_soft_PETG'],'PETG'),
        '03_replacement_lid_PLA':(['02_lid_with_spring'],'PLA'),
    }
    reports={}
    for name,(parts,material) in plates.items():
        print('Slicing',name,flush=True)
        process=profile('process','0.20mm Standard @BBL A1')
        process.update({'name':'Movie Time spring guide '+material,'from':'User','is_custom_defined':'1',
                        'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5',
                        'sparse_infill_density':'100%' if material=='PETG' else '15%',
                        'sparse_infill_pattern':'zig-zag' if material=='PETG' else 'gyroid',
                        'brim_type':'no_brim','brim_width':'0','skirt_loops':'0',
                        'enable_support':'0','elefant_foot_compensation':'0.15',
                        'outer_wall_speed':['35' if material=='PETG' else '60'],
                        'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],
                        'enable_prime_tower':'0','curr_bed_type':'Textured PEI Plate'})
        filament=profile('filament','Generic '+material+' @BBL A1')
        filament['filament_colour']=['#79A081' if material=='PETG' else '#DDD2B8']
        p=BUILD/(name+'_process.json');p.write_text(json.dumps(process))
        f=BUILD/(name+'_filament.json');f.write_text(json.dumps(filament))
        folder=BUILD/name;folder.mkdir(exist_ok=True)
        cmd=[BAMBU,'--debug','2','--load-settings',str(BUILD/'machine.json')+';'+str(p),
             '--load-filaments',str(f),'--arrange','1','--orient','0','--ensure-on-bed',
             '--slice','0','--outputdir',str(folder),'--export-3mf',name+'.3mf']
        cmd += [str(OUT/'stl'/(part+'.stl')) for part in parts]
        with (BUILD/(name+'.log')).open('w') as log:
            run=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=folder)
        assert run.returncode==0,(name,run.returncode)
        dest=OUT/'plates'/(name+'.3mf');shutil.copy2(folder/dest.name,dest)
        with zipfile.ZipFile(dest) as archive:
            tree=ET.fromstring(archive.read('Metadata/slice_info.config'))
            meta={i.attrib['key']:i.attrib['value'] for i in tree.findall('.//plate/metadata')}
            settings=json.loads(archive.read('Metadata/project_settings.config'))
            assert settings['printer_model']=='Bambu Lab A1'
            assert settings['filament_type']==[material]
            if material=='PETG':
                assert settings['sparse_infill_density']=='100%'
                assert settings['sparse_infill_pattern']=='zig-zag'
            assert meta['outside']=='false' and meta['support_used']=='false'
            assert all(o.attrib.get('skipped')=='false' for o in tree.findall('.//object'))
            reports[name]={'material':material,'parts':parts,'estimated_grams':float(meta['weight']),
                           'estimated_seconds':int(meta['prediction']),'outside_bed':False,'supports_used':False,
                           'warnings':[i.attrib['msg'] for i in tree.findall('.//warning')]}
        print(reports[name],flush=True)
    (OUT/'validation/slicer.json').write_text(json.dumps(reports,indent=2)+'\n')


if __name__=='__main__':run()
