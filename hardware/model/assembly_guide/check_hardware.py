"""Check nominal fastener stacks against the released STEP parts, without edits."""
from pathlib import Path
import sys,json
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/final_version'
sys.path.insert(0,str(ROOT/'model'));import build_model as m

def overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    if any(getattr(aa,c+'max')<=getattr(bb,c+'min') or getattr(bb,c+'max')<=getattr(aa,c+'min') for c in 'xyz'):return 0.
    return max(0.,a.intersect(b).Volume())

def cyl(point,r,length,direction):
    return cq.Solid.makeCylinder(r,length,cq.Vector(*point),cq.Vector(*direction))

def run():
    parts={p.stem:cq.importers.importStep(str(p)).val() for p in (OUT/'step').glob('0*.step')}
    parts['12_single_leaf_PETG']=cq.importers.importStep(str(OUT/'step/12_single_leaf_PETG.step')).val()
    allparts=dict(parts,**m.electronic_envelopes())
    specs=[]
    for x,y in m.P['lid_screws']:
        specs.append(dict(code='A',size='M3 x 25 pan head',seat=[x,y,1.4],axis=[0,0,1],length=25,
                          radius=1.5,head_radius=2.8,head_height=2.4,host='02_cute_lid_single_leaf',
                          receiver_entry=18.,pilot_end=29.5,tip=26.4,engagement=8.4))
    for x,y in m.P['deck_screws']:
        # Ideal 90 degree head, 5.6 mm maximum diameter; actual head must end
        # flush/recessed in the 6.4 mm countersink. Length includes the head.
        specs.append(dict(code='B',size='M3 x 8 90-degree countersunk',seat=[x,y,17.6],axis=[0,0,-1],length=8,
                          radius=1.5,head_radius=2.8,head_height=1.3,host='01_base',
                          receiver_entry=15.6,pilot_end=8.,tip=9.6,engagement=6.0))
    for x in (215.25,228.75):
        specs.append(dict(code='C',size='M2 x 14 pan head',seat=[x,8.8,20.],axis=[0,0,1],length=14,
                          radius=1.,head_radius=2.,head_height=1.6,host='02_cute_lid_single_leaf',
                          receiver_entry=30.,pilot_end=36.,tip=34.,engagement=4.0))
    for x in (204.8,244.):
        specs.append(dict(code='D',size='M2 x 6 pan head',seat=[x,12.4,32.1],axis=[0,-1,0],length=6,
                          radius=1.,head_radius=2.,head_height=1.6,host='07_switch_carrier',
                          receiver_entry=10.6,pilot_end=None,tip=6.4,engagement=4.2))
    for x in (205.,214.):
        specs.append(dict(code='E',size='M2 x 12 pan head',seat=[x,19.5,21.],axis=[0,0,1],length=12,
                          radius=1.,head_radius=2.,head_height=1.6,host='02_cute_lid_single_leaf',
                          receiver_entry=29.,pilot_end=33.7,tip=33.,engagement=4.0))
    rows=[];failures=[]
    for s in specs:
        p=cq.Vector(*s['seat']);axis=cq.Vector(*s['axis'])
        shaft=cyl(p.toTuple(),s['radius'],s['length'],axis.toTuple())
        if s['code']=='B':
            head=cq.Solid.makeCone(s['head_radius'],s['radius'],s['head_height'],p,axis)
        else:
            head=cyl((p-axis*s['head_height']).toTuple(),s['head_radius'],s['head_height'],axis.toTuple())
        screw=shaft.fuse(head).clean()
        hits=[]
        for name,part in allparts.items():
            if name==s['host']:continue # Intended metric-thread engagement in plastic pilot.
            v=overlap(screw,part)
            if v>.03:hits.append({'part':name,'volume_mm3':v})
        tip=p+axis*s['length'];host=parts[s['host']]
        assert not host.isInside(tip.toTuple(),1e-5),('tip reaches solid',s)
        clearance=None
        if s['pilot_end'] is not None:
            clearance=abs(s['pilot_end']-s['tip'])
            assert clearance>=.69,s
            axis_index=1 if s['axis'][1] else 2
            boundary=list(tip.toTuple());boundary[axis_index]=s['pilot_end']+.02*s['axis'][axis_index]
            assert host.isInside(tuple(boundary),1e-5),('pilot end mismatch',s,boundary)
        if hits:failures.extend(hits)
        rows.append(dict(s,blind_end_clearance_mm=clearance,unrelated_part_collisions=hits))
    # Alternative for the user's existing M2 x 16 screws: 2 mm spacers under
    # the heads shift the seat down and preserve the same 34 mm tip position.
    for x in (215.25,228.75):
        spacer=cyl((x,8.8,18),2.,2,(0,0,1)).cut(cyl((x,8.8,17.9),1.1,2.2,(0,0,1)))
        head=cyl((x,8.8,16.4),2.,1.6,(0,0,1))
        shaft=cyl((x,8.8,18),1.,16,(0,0,1))
        alternative=spacer.fuse(head,shaft)
        for name,part in allparts.items():
            if name=='02_cute_lid_single_leaf':continue
            assert overlap(alternative,part)<.03,('16 mm + spacer',name)
    assert not failures,failures
    report={'all_nominal_screw_checks_passed':True,'screw_count_in_player':14,'screws':rows,
            'correction':{'location':'C - switch carrier to lid','old_screw':'M2 x 16 without spacer',
                          'old_tip_z_mm':36.,'blind_pilot_end_z_mm':36.,'old_blind_end_margin_mm':0.,
                          'recommended':'M2 x 14','alternative':'M2 x 16 with a 2 mm spacer under each head, OD <= 4 mm',
                          'alternative_clearance_checked':True},
            'nfc_tag_center_from_case_left_mm':m.P['pn532_centre'][0]-m.SL,
            'nfc_tag_center_from_spine_mm':m.P['pn532_centre'][1]+27,
            'limitations':['Nominal screw envelopes, not a thread-strength test.',
                           'Confirm actual head dimensions and seat deck heads flush or recessed.',
                           'Printed tolerances, tightening torque and switch operation require physical checks.']}
    (OUT/'validation/assembly_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='screws'},indent=2))

if __name__=='__main__':run()
