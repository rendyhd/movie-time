"""One A1 PETG project containing the two replacement test parts."""
from pathlib import Path
import sys
import json
import subprocess
import shutil
import zipfile
import xml.etree.ElementTree as ET
import importlib.util

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('spring_profiles',ROOT/'model/spring_guide/prepare_plates.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
OUT=ROOT/'output/spring_guide_v2'
BUILD=ROOT/'build/spring_guide_v2/slicer';BUILD.mkdir(parents=True,exist_ok=True)


def run():
    material=helper.profile('filament','Generic PETG @BBL A1')
    material['filament_colour']=['#79A081']
    machine=helper.profile('machine','Bambu Lab A1 0.4 nozzle')
    process=helper.profile('process','0.20mm Standard @BBL A1')
    process.update({'name':'Movie Time middle-contact test PETG','from':'User','is_custom_defined':'1',
                    'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5',
                    'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag',
                    'brim_type':'no_brim','brim_width':'0','skirt_loops':'0','enable_support':'0',
                    'elefant_foot_compensation':'0.15','outer_wall_speed':['35'],
                    'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],
                    'enable_prime_tower':'0','curr_bed_type':'Textured PEI Plate'})
    for name,data in [('machine',machine),('process',process),('filament',material)]:
        (BUILD/(name+'.json')).write_text(json.dumps(data,indent=2))
    name='01_middle_contact_test_PETG'
    parts=['16_middle_contact_spring_PETG','17_sliding_tail_carrier_PETG']
    cmd=[helper.BAMBU,'--debug','2','--load-settings',str(BUILD/'machine.json')+';'+str(BUILD/'process.json'),
         '--load-filaments',str(BUILD/'filament.json'),'--arrange','1','--orient','0','--ensure-on-bed',
         '--slice','0','--outputdir',str(BUILD),'--export-3mf',name+'.3mf']
    cmd += [str(OUT/'stl'/(part+'.stl')) for part in parts]
    with (BUILD/'slice.log').open('w') as log:
        result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=BUILD)
    assert result.returncode==0,result.returncode
    dest=OUT/'plates'/(name+'.3mf');shutil.copy2(BUILD/dest.name,dest)
    with zipfile.ZipFile(dest) as archive:
        tree=ET.fromstring(archive.read('Metadata/slice_info.config'))
        meta={i.attrib['key']:i.attrib['value'] for i in tree.findall('.//plate/metadata')}
        settings=json.loads(archive.read('Metadata/project_settings.config'))
        assert settings['printer_model']=='Bambu Lab A1' and settings['filament_type']==['PETG']
        assert settings['sparse_infill_density']=='100%' and settings['sparse_infill_pattern']=='zig-zag'
        assert meta['outside']=='false' and meta['support_used']=='false'
        assert all(o.attrib.get('skipped')=='false' for o in tree.findall('.//object'))
        report={'project':dest.name,'parts':parts,'material':'PETG','scale_percent':100,
                'estimated_grams':float(meta['weight']),'estimated_seconds':int(meta['prediction']),
                'supports_used':False,'outside_bed':False,'warnings':[i.attrib['msg'] for i in tree.findall('.//warning')]}
    (OUT/'validation/slicer.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':run()
