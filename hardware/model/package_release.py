"""Package current validated models. Keeps earlier release ZIPs intact."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
version=sys.argv[1] if len(sys.argv)>1 else 'v2_1'
assert version.replace('_','').replace('-','').isalnum()
summary_path=OUT/'validation/summary.json'
summary=json.loads(summary_path.read_text()) if summary_path.exists() else {}
summary.update({'release':version,'bambu_studio_version':'2.7.1.62',
                'printer':'Bambu Lab A1 0.4 nozzle','plates':{},'physically_printed':False,'nfc_tested_on_hardware':False})
for p in sorted((OUT/'plates').glob('*.3mf')):
    with zipfile.ZipFile(p) as z:
        r=ET.fromstring(z.read('Metadata/slice_info.config'))
        m={i.attrib['key']:i.attrib['value'] for i in r.findall('.//plate/metadata')}
        settings=json.loads(z.read('Metadata/project_settings.config'))
        assert settings['printer_model']=='Bambu Lab A1'
        assert m['outside']=='false' and m['support_used']=='false'
        assert z.read('Metadata/plate_1.gcode').strip()
        assert all(o.attrib.get('skipped')=='false' for o in r.findall('.//object'))
        summary['plates'][p.stem]={
            'estimated_seconds':int(m['prediction']),'estimated_grams':float(m['weight']),
            'outside_bed':False,'supports_used':False,
            'warnings':[w.attrib['msg'] for w in r.findall('.//warning')],
            'objects':[o.attrib['name'] for o in r.findall('.//object')]}
summary['final_parts_estimated_grams']=round(sum(v['estimated_grams'] for k,v in summary['plates'].items() if not k.startswith('01')),2)
summary['final_parts_estimated_seconds']=sum(v['estimated_seconds'] for k,v in summary['plates'].items() if not k.startswith('01'))
summary_path.write_text(json.dumps(summary,indent=2)+'\n')
files=[ROOT/'README.md',ROOT/'ASSEMBLY.md',ROOT/'requirements.txt']
for d in ('model','firmware','output/stl','output/step','output/plates','output/preview','output/validation'):
    files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='SHA256.json')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
checksums=OUT/'validation/SHA256.json';checksums.write_text(json.dumps(manifest,indent=2)+'\n')
files.append(checksums)
archive=OUT/f'Movie_Time_A1_{version}.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:z.write(p,Path(f'Movie_Time_A1_{version}')/p.relative_to(ROOT))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('Packaged',archive,'—',len(files),'files;',archive.stat().st_size,'bytes')
print('Final parts:',summary['final_parts_estimated_grams'],'g /',summary['final_parts_estimated_seconds'],'seconds')
