"""One replacement plate plus the two updated plates in the full package."""
from pathlib import Path
import json,sys,subprocess,shutil,importlib.util
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/final_version';BUILD=ROOT/'build/button_fit_fix/slicer'
spec=importlib.util.spec_from_file_location('final_plates',ROOT/'model/final_version/prepare_plates.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

def run(optional_only=False,holder_update=False):
    BUILD.mkdir(parents=True,exist_ok=True)
    machine=helper.helper.profile('machine','Bambu Lab A1 0.4 nozzle')
    process=helper.helper.profile('process','0.20mm Standard @BBL A1')
    process.update({'name':'Movie Time measured switches PLA','from':'User','is_custom_defined':'1',
                    'wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5',
                    'sparse_infill_density':'15%','sparse_infill_pattern':'gyroid',
                    'enable_support':'0','brim_type':'no_brim','brim_width':'0','skirt_loops':'0',
                    'elefant_foot_compensation':'0.15','outer_wall_speed':['40'],
                    'initial_layer_speed':['25'],'initial_layer_infill_speed':['40'],
                    'enable_prime_tower':'0','curr_bed_type':'Textured PEI Plate'})
    for n,data in [('machine',machine),('process',process)]:
        (BUILD/(n+'.json')).write_text(json.dumps(data))
    caps=['04_button_play','05_button_pause','06_button_stop']
    hardware=['07_switch_carrier','08_switch_retainer']
    reports=json.loads((OUT/'validation/slicer.json').read_text())
    for name,names in [('Holder_Reach_Fix_PLA',hardware),('Buttons_Fit_Fix_PLA',caps+hardware),
                       ('04_Deck_and_Hardware_PLA',['03_case_deck']+hardware+['09_led_lens']),
                       ('05_Buttons_PLA',caps),
                       ('Button_and_case_fit_PLA',['10_button_fit_test','11_case_fit_test']+caps+hardware)]:
        if optional_only and name!='Button_and_case_fit_PLA':continue
        if holder_update and name=='05_Buttons_PLA':continue
        filament=helper.helper.profile('filament','Generic PLA @BBL A1')
        filament['filament_colour']=['#8EAA80' if name=='05_Buttons_PLA' else '#DDD2B8']
        f=BUILD/(name+'_filament.json');f.write_text(json.dumps(filament))
        folder=BUILD/name;folder.mkdir(exist_ok=True)
        cmd=[helper.helper.BAMBU,'--debug','2','--load-settings',str(BUILD/'machine.json')+';'+str(BUILD/'process.json'),
             '--load-filaments',str(f),'--arrange','1','--orient','0','--ensure-on-bed','--slice','0',
             '--outputdir',str(folder),'--export-3mf',name+'.3mf']
        cmd += [str((ROOT/'output' if n.startswith(('10','11')) else OUT)/'stl'/f'{n}.stl') for n in names]
        with (folder/'slice.log').open('w') as log:
            result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=folder)
        assert result.returncode==0,(name,result.returncode)
        directory=ROOT/'output' if name in ('Buttons_Fit_Fix_PLA','Holder_Reach_Fix_PLA') else (OUT/'optional' if name=='Button_and_case_fit_PLA' else OUT/'plates')
        directory.mkdir(exist_ok=True)
        destination=directory/(name+'.3mf')
        shutil.copy2(folder/destination.name,destination)
        r=helper.inspect(destination,'PLA')
        if name=='Holder_Reach_Fix_PLA':
            (OUT/'validation/holder_plate.json').write_text(json.dumps(r,indent=2)+'\n')
        elif name=='Buttons_Fit_Fix_PLA':
            (OUT/'validation/button_plate.json').write_text(json.dumps(r,indent=2)+'\n')
        elif name=='Button_and_case_fit_PLA':
            (OUT/'validation/button_fit_plate.json').write_text(json.dumps(r,indent=2)+'\n')
        else:reports[name]=r
        print(r,flush=True)
    (OUT/'validation/slicer.json').write_text(json.dumps(reports,indent=2)+'\n')

if __name__=='__main__':run(optional_only='--optional-only' in sys.argv,holder_update='--holder-update' in sys.argv)
