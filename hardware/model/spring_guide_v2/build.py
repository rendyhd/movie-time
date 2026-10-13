"""Middle-contact bow spring with a guided sliding tail.

The first prototype's free end caught behind a Blu-ray case in the user's test.
This revision keeps both ends outside the case path and puts a straight contact
land halfway along the inserted case. The old fixture and screws are reused.
Deflected shapes check geometry only, not elastic forces or physical alignment.
"""
from pathlib import Path
import sys
import json
import hashlib
import numpy as np
import cadquery as cq
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model'))
import build_model as base

OUT=ROOT/'output/spring_guide_v2'
Z,HEIGHT=21.0,8.0
AXIS=202.0
FRONT,REAR=25.0,104.0
SPAN=REAR-FRONT
AMPLITUDE=31.0
THICKNESS=1.0
TAIL=8.0
MOUNTS=[(205.0,19.5),(214.0,19.5)]


def bow_factor(s):
    # Straight contact land from 43% to 57% of the fixed 79 mm span.
    q=np.clip(np.minimum(s,1-s)/0.43,0,1)
    return q*q*(3-2*q)


def arc_length(amplitude):
    s=np.linspace(0,1,4001)
    return float(np.hypot(np.diff(amplitude*bow_factor(s)),np.diff(SPAN*s)).sum())


REST_LENGTH=arc_length(AMPLITUDE)+TAIL


def profile(amplitude=AMPLITUDE):
    s=np.unique(np.round(np.r_[np.linspace(0,1,201),0.43,0.57],9))
    pts=[(AXIS,24.5)]
    pts += [(float(AXIS-amplitude*bow_factor(t)),float(FRONT+SPAN*t)) for t in s]
    tail_length=REST_LENGTH-arc_length(amplitude)
    pts.append((AXIS,REAR+tail_length))
    return pts,tail_length


def spring(amplitude=AMPLITUDE,edge_breaks=True):
    points,tail_length=profile(amplitude)
    outline=[(x-THICKNESS/2,y) for x,y in points]
    outline += [(x+THICKNESS/2,y) for x,y in reversed(points)]
    beam=cq.Workplane('XY',origin=(0,0,Z)).polyline(outline).close().extrude(HEIGHT).val()
    # Upper half of the old 8 mm mounting block. The carrier supplies its lower
    # half, preserving the existing screw length and the fixture's mounting face.
    root=base.rounded_box(200.5,14,25,18.7,11,4,1.2)
    shape=base.fuse(root,beam)
    for x,y in MOUNTS:shape=base.cut(shape,base.cylinder(x,y,24.9,1.15,4.2))
    if edge_breaks:shape=cq.Workplane(obj=shape).edges('>Z or <Z').chamfer(0.2).val()
    return shape


def carrier():
    root=base.rounded_box(200.5,14,21,18.7,10,4,1.2)
    # Backed by the old fixture's existing guard wall at X=211. This rail has
    # 0.3 mm nominal clearance to that wall and requires no new mounting holes.
    shape=base.fuse(root,base.box(207.5,23.5,21,3.2,1.8,4),
                    base.box(207.5,25.3,21,3.2,108.7,8),
                    base.box(202.8,104.5,21,7.9,29.5,8.5),
                    base.box(200.3,104.5,21,0.9,29.5,8.5))
    # Roof bridges are over a 1.6 mm channel and print without supports. The
    # spring is inserted after printing; this is not a print-in-place joint.
    for y in (106.0,123.0):
        shape=base.fuse(shape,base.box(200.3,y,29.5,10.4,5,2))
    for x,y in MOUNTS:shape=base.cut(shape,base.cylinder(x,y,20.9,1.15,4.2))
    return shape.clean()


def lid():
    shape=cq.importers.importStep(str(ROOT/'output/spring_guide/step/02_lid_with_spring.step')).val()
    # Higher pocket for the slider roof; original spring lid is not compatible.
    return base.cut(shape,base.box(199.5,24,20.5,4.5,115,11.5))


def allowed_amplitude(right,leading_edge):
    limit_s=np.clip((leading_edge-FRONT)/SPAN,0,1)
    g=float(bow_factor(min(limit_s,0.5)))
    if g<1e-9:return AMPLITUDE
    return min(AMPLITUDE,max(0,(AXIS-right-THICKNESS/2-0.05)/g))


def read_step(path):return cq.importers.importStep(str(path)).val()


def run():
    for folder in ('stl','step','plates','preview','validation'):(OUT/folder).mkdir(parents=True,exist_ok=True)
    parts={'16_middle_contact_spring_PETG':spring(),
           '17_sliding_tail_carrier_PETG':carrier(),
           '02_lid_middle_contact':lid()}
    records={}
    for name,shape in parts.items():
        assert shape.isValid() and len(shape.Solids())==1,name
        oriented=base.on_bed(shape) if name.startswith('17') else base.invert(shape)
        cq.exporters.export(shape,str(OUT/'step'/f'{name}.step'))
        dest=OUT/'stl'/f'{name}.stl'
        cq.exporters.export(oriented,str(dest),tolerance=0.035,angularTolerance=0.1)
        mesh=trimesh.load_mesh(dest)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1,name
        assert np.all(mesh.extents <= 256),name
        records[name]={'size_mm':np.round(mesh.extents,3).tolist(),'volume_cm3':round(float(mesh.volume)/1000,3),
                       'watertight':True,'single_body':True,'fits_A1':True}
        print(name,records[name],flush=True)
    (OUT/'validation/meshes.json').write_text(json.dumps(records,indent=2)+'\n')
    check(parts)


def overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    if any(getattr(aa,axis+'max')<=getattr(bb,axis+'min') or getattr(bb,axis+'max')<=getattr(aa,axis+'min') for axis in ('x','y','z')):
        return 0.0
    return a.intersect(b).Volume()


def check(parts):
    frame=parts['17_sliding_tail_carrier_PETG']
    new_lid=parts['02_lid_middle_contact']
    existing={p.stem:read_step(p) for p in (ROOT/'output/step').glob('0*.step') if not p.stem.startswith('02')}
    fixture={n:read_step(ROOT/'output/spring_guide/step'/f'{n}.step') for n in ('14_spring_test_bed','15_spring_test_mount')}
    shell=dict(existing,lid=new_lid)
    failures=[]; fixed=[]
    for n,s in dict(shell,**fixture,**base.electronic_envelopes()).items():
        vol=overlap(frame,s)
        if vol>0.02:fixed.append({'object':'carrier','part':n,'volume_mm3':round(vol,4)})
    for n,s in dict(existing,**base.electronic_envelopes()).items():
        vol=overlap(new_lid,s)
        if vol>0.02:fixed.append({'object':'new lid','part':n,'volume_mm3':round(vol,4)})
    failures.extend(fixed)
    # Check all deflections, including fully flattened, against the slider,
    # fixture, shell and electronics. The round endpoint has been removed.
    shape_checks=[]
    for amplitude in (31,27,23.4,18,12,6,3.4,1.5,0):
        shape=spring(amplitude,False)
        pts,tail=profile(amplitude)
        hits=[]
        for n,s in dict(shell,**fixture,**base.electronic_envelopes(),carrier=frame).items():
            vol=overlap(shape,s)
            if vol>0.02:hits.append({'part':n,'volume_mm3':round(vol,4)})
        shape_checks.append({'amplitude_mm':amplitude,'tail_end_y_mm':round(REAR+tail,3),'collisions':hits})
        failures.extend(hits)
    stages=[]
    for label,width,height in [('Blu-ray',170,14),('Blu-ray large',172,15),('DVD',190,14)]:
        for left in sorted(set([8.05,(208-width)/2,199.95-width])):
            for front in (25,32,40,48,59,70,85,100,108):
                amplitude=allowed_amplitude(left+width,front)
                shape=spring(amplitude,False)
                case=base.box(left,front-135,18.01,width,134.98,height)
                hits=[]
                for n,s in dict(shell,**fixture,carrier=frame,bow_spring=shape).items():
                    vol=overlap(case,s)
                    if vol>0.03:hits.append({'part':n,'volume_mm3':round(vol,4)})
                stages.append({'case':label,'left_mm':left,'leading_y_mm':front,
                               'amplitude_mm':round(amplitude,4),'collisions':hits})
                failures.extend(hits)
            print('Checked',label,'left',left,flush=True)
    # Constant active span makes the straight contact land stay halfway along
    # insertion. Its normal is purely sideways; there is no rear-facing end pad.
    land=[FRONT+0.43*SPAN,FRONT+0.57*SPAN]
    guide_report={'contact_land_y_mm':land,'fully_inserted_case_leading_y_mm':108,
                  'case_to_contact_rear_margin_mm':108-land[1],
                  'tail_axis_x_mm':AXIS,'minimum_tail_clearance_from_case_right_mm':AXIS-THICKNESS/2-200,
                  'unloaded_tail_end_y_mm':REAR+TAIL,
                  'fully_flat_tail_end_y_mm':REAR+REST_LENGTH-SPAN,
                  'total_neutral_centerline_length_mm':REST_LENGTH,
                  'max_centerline_length_error_mm':max(abs(arc_length(a)+profile(a)[1]-REST_LENGTH) for a in np.linspace(0,AMPLITUDE,50))}
    assert guide_report['fully_flat_tail_end_y_mm']<141.6
    report={'revision':2,'previous_physical_test':'User reported round tip catching behind Blu-ray case and pushing it out when not initially left-aligned.',
            'all_geometry_checks_passed':not failures,'fixed_collisions':fixed,
            'deflected_shape_checks':shape_checks,'insertion_stages':stages,'guide_geometry':guide_report,
            'method':'Prescribed bowed-strip shape with constant 79 mm span and straight middle land; changing arc length is taken up by a sliding tail. Rigid-body clearance and centerline length checks only; forces, friction, material stress and actual sliding are not simulated.',
            'physical_test_of_revision_2':(OUT/'validation/physical_test.json').exists(),
            'physical_test_record':json.loads((OUT/'validation/physical_test.json').read_text()) if (OUT/'validation/physical_test.json').exists() else None,
            'automatic_alignment_verified':False,
            'existing_fixture_reused':True,'existing_mounting_screws_reused':True,
            'fixture_step_sha256':{n:hashlib.sha256((ROOT/'output/spring_guide/step'/f'{n}.step').read_bytes()).hexdigest() for n in fixture}}
    (OUT/'validation/mechanics.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not failures,failures
    print('Middle-contact guide geometry checks passed.',flush=True)


if __name__=='__main__':run()
