"""Update only caps, switch carrier and rear plate for the measured switches."""
from pathlib import Path
import sys,json,hashlib
import cadquery as cq
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/final_version'
sys.path.insert(0,str(ROOT/'model'))
import build_model as m

NAMES=['04_button_play','05_button_pause','06_button_stop','07_switch_carrier','08_switch_retainer']

def read(path):return cq.importers.importStep(str(path)).val()

def overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    if any(getattr(aa,c+'max')<=getattr(bb,c+'min') or getattr(bb,c+'max')<=getattr(aa,c+'min') for c in 'xyz'):return 0.
    return max(0.,a.intersect(b).Volume())

def run(holder_only=False):
    parts={p.stem:read(p) for p in (OUT/'step').glob('0*.step')}
    parts['12_single_leaf_PETG']=read(OUT/'step/12_single_leaf_PETG.step')
    changed=NAMES[3:] if holder_only else NAMES
    unchanged={n:hashlib.sha256((OUT/'step'/f'{n}.step').read_bytes()).hexdigest()
               for n in parts if n not in changed}
    parts['07_switch_carrier']=m.carrier_frame();parts['08_switch_retainer']=m.retainer()
    for name,kind,x in zip(NAMES[:3],('play','pause','stop'),m.BX):
        if not holder_only:parts[name]=m.button(kind).translate((x,0,m.BZ))
    failures=[];checks=[]
    env=m.electronic_envelopes()
    for name in NAMES:
        for other,o in dict(parts,**env).items():
            if other==name:continue
            v=overlap(parts[name],o)
            if v>.02:failures.append((name,other,v))
    reach=[]
    for name,kind in zip(NAMES[:3],('play','pause','stop')):
        for travel in (0,.09,.1,.2,.45,.6,.69):
            s=parts[name].translate((0,travel,0))
            for other in ('02_cute_lid_single_leaf','07_switch_carrier','08_switch_retainer'):
                v=overlap(s,parts[other])
                if v>.02:failures.append((name,travel,other,v))
            checks.append({'cap':name,'travel_mm':travel,'plastic_collision':False})
        stop=overlap(parts[name].translate((0,.72,0)),parts['07_switch_carrier'])
        assert stop>.05,(name,'hard stop absent',stop)
        # Explicitly check actual pin reach, not just absence of collisions.
        # The contact face is calibrated from the user's installed measurement.
        act=env[kind+'_switch_plunger'];cap=parts[name]
        face=act.BoundingBox().ymin;pin_end=cap.BoundingBox().ymax
        gap=face-pin_end
        assert .09<gap<.11,(name,'unpressed gap',gap)
        assert overlap(cap.translate((0,gap-.01,0)),act)<.001
        assert overlap(cap.translate((0,gap+.01,0)),act)>.05
        assert overlap(cap.translate((0,.3,0)),act)>1.3
        assert overlap(cap.translate((0,.69,0)),env[kind+'_switch_body'])<.001
        pin_length=pin_end-3.4
        recess=face-parts['07_switch_carrier'].BoundingBox().ymin
        assert abs(pin_length-2.8)<1e-6 and abs(recess-2.2)<1e-6
        assert abs(pin_length-recess-.6)<1e-6
        reach.append({'cap':name,'pin_length_mm':round(pin_length,3),
                      'predicted_recess_after_0_8_mm_forward_shift_mm':round(recess,3),'contact_after_cap_travel_mm':round(gap,3),
                      'measured_actuator_travel_mm':.5,'full_press_at_cap_travel_mm':.6,
                      'hard_stop_margin_after_full_press_mm':.1,'contact_checked':True})
    # Each nominal switch body is positively captured axially by the front
    # shoulder and the rear plate. Verify both directions, not just a pocket.
    retention=[]
    for kind in ('play','pause','stop'):
        s=env[kind+'_switch_body']
        forward=overlap(s.translate((0,-.05,0)),parts['07_switch_carrier'])
        backward=overlap(s.translate((0,.05,0)),parts['08_switch_retainer'])
        assert min(forward,backward)>.05,(kind,forward,backward)
        retention.append({'switch':kind,'front_shoulder_retains_body':True,'rear_plate_retains_body':True})
    # Same measured body and actuator through the actual coupon opening.
    coupon=read(ROOT/'output/step/10_button_fit_test.step')
    for name in changed:
        assert overlap(parts[name],coupon)<.02,(name,'existing coupon')
    assert not failures,failures
    meshes=json.loads((OUT/'validation/meshes.json').read_text())
    prior_meshes=json.loads((ROOT/'output/before_button_reach_fix/final_version/validation/meshes.json').read_text())
    if holder_only:
        for name in NAMES[:3]:meshes[name]=prior_meshes[name]
    for name in changed:
        s=parts[name]
        assert s.isValid() and len(s.Solids())==1,name
        printed=m.on_bed(s.rotate((0,0,0),(1,0,0),-90)) if name=='07_switch_carrier' else m.front_down(s)
        cq.exporters.export(s,str(OUT/'step'/f'{name}.step'))
        cq.exporters.export(printed,str(OUT/'stl'/f'{name}.stl'),tolerance=.025,angularTolerance=.1)
        mesh=trimesh.load_mesh(OUT/'stl'/f'{name}.stl')
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1,name
        assert np.all(mesh.extents<256),name
        meshes[name]={'size_mm':mesh.extents.round(3).tolist(),'volume_cm3':round(float(mesh.volume)/1000,3),
                      'watertight':True,'single_body':True,'fits_A1':True}
        print(name,meshes[name],flush=True)
    (OUT/'validation/meshes.json').write_text(json.dumps(meshes,indent=2)+'\n')
    assembly=cq.Assembly(name='Movie_Time_Measured_Switches')
    for name,s in parts.items():assembly.add(s,name=name)
    assembly.export(str(OUT/'step/Movie_Time_final_assembled.step'))
    report={'revision':'Switch holder moves seats 0.8 mm forward; existing 2.8 mm pin caps retained',
            'changed_parts':changed,'measured_body_mm':[6,6,4],
            'measured_actuator_diameter_mm':3.5,'measured_actuator_projection_mm':1.,
            'pocket_mm':[6.2,6.2,4.0],'cap_pressing_pin_diameter_mm':3.,
            'guide_bore_diameter_mm':4.2,'cap_pin_length_mm':2.8,
            'previous_measured_unpressed_recess_mm':3.,'previous_measured_pressed_recess_mm':3.5,
            'switch_seat_forward_shift_mm':.8,'predicted_new_unpressed_recess_mm':2.2,
            'predicted_new_pressed_recess_mm':2.7,'reach_checks':reach,
            'rest_gap_mm':.1,'cap_hard_stop_travel_mm':.7,
            'measured_actuator_travel_mm':.5,'geometric_full_press_margin_mm':.1,
            'cap_visible_projection_mm':1.4,'switch_retention':retention,
            'existing_front_panel_and_coupon_reused':True,
            'existing_screws_reused':['2 x M2 x 14 mm carrier, or M2 x 16 with 2 mm spacers','2 x M2 x 6 mm retainer'],
            'all_solid_checks_passed':True,'motion_checks':checks,'failures':failures,
            'unchanged_step_sha256':unchanged,'physically_tested':False,
            'limitations':['Actuator travel inferred from user measurements: 3.5 minus 3.0 mm. Operating force is not measured.',
                           'Installed contact face uses the previous measured recess, translated 0.8 mm with the new seats. The difference from the old nominal switch envelope remains unexplained; the actuator well is a motion envelope, not an internal switch model.',
                           'Printed fit, switch click and return must be checked with the actual switches.',
                           'Lead reliefs are retained; soldered lead fit has not been physically checked.']}
    (OUT/'validation/buttons.json').write_text(json.dumps(report,indent=2)+'\n')
    # Keep the final assembly's overall clearance record current after replacing
    # the switches and carrier beside the already released PETG leaf.
    sys.path.insert(0,str(ROOT/'model/final_version'))
    import build as final_build
    final_build.check(parts)
    print('Measured-switch fit and retention checks passed.',flush=True)

if __name__=='__main__':run(holder_only='--holder-only' in sys.argv)
