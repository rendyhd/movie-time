"""Five clearly named final A1 plates. Slice only the two changed parts."""
from pathlib import Path
import json,shutil,subprocess,zipfile,importlib.util,sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/final_version'
BUILD=ROOT/'build/final_version/slicer'
spec=importlib.util.spec_from_file_location('profiles',ROOT/'model/spring_guide/prepare_plates.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)


def inspect(path,material):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        tree=ET.fromstring(z.read('Metadata/slice_info.config'))
        m={i.attrib['key']:i.attrib['value'] for i in tree.findall('.//plate/metadata')}
        s=json.loads(z.read('Metadata/project_settings.config'))
        assert s['printer_model']=='Bambu Lab A1' and s['filament_type']==[material]
        if material=='PETG':
            assert s['sparse_infill_density']=='100%' and s['sparse_infill_pattern']=='zig-zag'
        assert m['outside']=='false' and m['support_used']=='false'
        assert all(o.attrib.get('skipped')=='false' for o in tree.findall('.//object'))
        assert z.read('Metadata/plate_1.gcode').strip()
        (OUT/'preview'/f'{path.stem}_plate.png').write_bytes(z.read('Metadata/plate_1.png'))
        return {'file':path.name,'material':material,'estimated_grams':float(m['weight']),
                'estimated_seconds':int(m['prediction']),'supports_used':False,'outside_bed':False,
                'objects':[i.attrib['name'] for i in tree.findall('.//object')],
                'warnings':[i.attrib['msg'] for i in tree.findall('.//warning')]}


def run(spring_only=False):
    BUILD.mkdir(parents=True,exist_ok=True)
    report_path=OUT/'validation/slicer.json'
    reports=json.loads(report_path.read_text()) if spring_only and report_path.exists() else {}
    machine=helper.profile('machine','Bambu Lab A1 0.4 nozzle')
    (BUILD/'machine.json').write_text(json.dumps(machine))
    for name,part,material in [('01_Spring_PETG','12_single_leaf_PETG','PETG'),
                               ('02_Cute_Lid_PLA','02_cute_lid_single_leaf','PLA')]:
        if spring_only and material!='PETG':continue
        process=helper.profile('process','0.20mm Standard @BBL A1')
        process.update({'name':'Movie Time final '+material,'from':'User','is_custom_defined':'1',
                        'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5',
                        'sparse_infill_density':'100%' if material=='PETG' else '15%',
                        'sparse_infill_pattern':'zig-zag' if material=='PETG' else 'gyroid',
                        'brim_type':'no_brim','brim_width':'0','skirt_loops':'0','enable_support':'0',
                        'elefant_foot_compensation':'0.15','outer_wall_speed':['35' if material=='PETG' else '60'],
                        'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],
                        'enable_prime_tower':'0','curr_bed_type':'Textured PEI Plate'})
        filament=helper.profile('filament','Generic '+material+' @BBL A1')
        filament['filament_colour']=['#79A081' if material=='PETG' else '#DDD2B8']
        p=BUILD/(name+'_process.json');p.write_text(json.dumps(process))
        f=BUILD/(name+'_filament.json');f.write_text(json.dumps(filament))
        folder=BUILD/name;folder.mkdir(exist_ok=True)
        cmd=[helper.BAMBU,'--debug','2','--load-settings',str(BUILD/'machine.json')+';'+str(p),
             '--load-filaments',str(f),'--arrange','1','--orient','0','--ensure-on-bed',
             '--slice','0','--outputdir',str(folder),'--export-3mf',name+'.3mf',str(OUT/'stl'/f'{part}.stl')]
        print('Slicing',name,flush=True)
        with (folder/'slice.log').open('w') as log:
            r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=folder)
        assert r.returncode==0,(name,r.returncode)
        dest=OUT/'plates'/f'{name}.3mf';shutil.copy2(folder/dest.name,dest)
        reports[name]=inspect(dest,material)
        print(reports[name],flush=True)
    for new,old in [('03_Base_PLA','02_base')]:
        if spring_only:continue
        dest=OUT/'plates'/f'{new}.3mf'
        shutil.copy2(ROOT/'output/plates'/f'{old}.3mf',dest)
        reports[new]=inspect(dest,'PLA')
        reports[new]['unchanged_from']=f'output/plates/{old}.3mf'
    (OUT/'validation/slicer.json').write_text(json.dumps(reports,indent=2)+'\n')
    if not spring_only:
        subprocess.run([sys.executable,str(ROOT/'model/button_fit_fix/prepare_plates.py')],check=True)
    print('All five final plates verified.',flush=True)


if __name__=='__main__':run(spring_only='--spring-only' in sys.argv)
