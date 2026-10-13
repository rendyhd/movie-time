"""Revision 3: bowed leaf ending in a translating shoe, beside a captive track.

Revision 2 physically worked for Blu-ray but its curved material jammed at the
tail slot under DVD travel. This design never feeds the leaf through a guide.
Four circular flexure arcs have fixed material lengths in the prescribed motion
family. The rigid shoe moves with their endpoint. This is a clearance model,
not an elastic/contact/friction simulation or proof of automatic alignment.
"""
from pathlib import Path
import sys, json, hashlib
import numpy as np
from scipy.optimize import brentq
import cadquery as cq
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'model'))
import build_model as base

OUT = ROOT/'output/spring_guide_v3'
AXIS, FRONT, REST_REAR = 202.15, 25.0, 91.0
# Extra height grows downward, keeping the whole upper surface at Z=29 for
# support-free inverted printing and the existing 8 mm mounting stack.
AMPLITUDE, THICKNESS, Z, HEIGHT = 27.0, 1.0, 19.0, 10.0
LAND = 11.06
HALF_SPAN = (REST_REAR-FRONT-LAND)/2
ANGLE = 2*np.arctan(AMPLITUDE/HALF_SPAN)
RADIUS = (AMPLITUDE**2+HALF_SPAN**2)/(4*AMPLITUDE)
ARC_LENGTH = RADIUS*ANGLE
REST_LENGTH = 4*ARC_LENGTH+LAND
MAX_TRAVEL = REST_LENGTH-(REST_REAR-FRONT)
MOUNTS = [(205.0,19.5), (214.0,19.5)]
TRACK_FRONT, TRACK_REAR = REST_REAR-6.0, 130.0
SHOE_FRONT, SHOE_REAR = REST_REAR-1.0, REST_REAR+7.0
# Coordinates in XZ, swept parallel to Y. Both mating slopes are 45 degrees.
SHOE_XZ = [(204.4,23.0),(209.3,23.0),(209.3,24.2),
           (207.9,25.6),(207.9,29.0),(205.8,29.0),
           (205.8,25.6),(204.4,24.2)]
LEFT_RAIL_XZ = [(203.0,22.6),(204.0,22.6),(204.0,24.6),
                (205.2,25.8),(205.2,26.6),(203.0,26.6)]
RIGHT_RAIL_XZ = [(210.7,22.6),(209.7,22.6),(209.7,24.6),
                 (208.5,25.8),(208.5,26.6),(210.7,26.6)]


def amplitude_at(theta):
    return 0.0 if abs(theta)<1e-10 else 2*ARC_LENGTH/theta*(1-np.cos(theta))


def angle_for(amplitude):
    if amplitude <= 1e-9: return 0.0
    if amplitude >= AMPLITUDE: return float(ANGLE)
    return brentq(lambda theta: amplitude_at(theta)-amplitude, 1e-9, ANGLE)


def profile(amplitude=AMPLITUDE, samples=48):
    """Each arc retains its own length, not just the total strip length.

    Arc tangent rotates 0 -> -theta -> 0, then a fixed straight contact land,
    then 0 -> theta -> 0. The rear end is free to translate with its shoe.
    """
    theta=angle_for(amplitude)
    x,y=AXIS,FRONT
    points=[(x,y)]
    tangents=[0.0]
    for index,(start,end) in enumerate([(0,-theta),(-theta,0),(0,theta),(theta,0)]):
        if index==2:
            y+=LAND; points.append((x,y)); tangents.append(0.0)
        for u in np.linspace(0,1,samples+1)[1:]:
            t=start+(end-start)*u
            if abs(end-start)<1e-10:
                px,py=x+ARC_LENGTH*u*np.sin(start),y+ARC_LENGTH*u*np.cos(start)
            else:
                k=(end-start)/ARC_LENGTH
                px=x+(np.cos(start)-np.cos(t))/k
                py=y+(np.sin(t)-np.sin(start))/k
            points.append((float(px),float(py))); tangents.append(float(t))
        x,y=points[-1]
    return np.asarray(points),np.asarray(tangents)


def end_y(amplitude): return float(profile(amplitude,1)[0][-1,1])


def shoe(travel=0):
    s=base.y_poly(0,SHOE_FRONT+travel,0,SHOE_XZ,SHOE_REAR-SHOE_FRONT)
    # Break the entry edges to help the rigid foot enter from the rear.
    s=cq.Workplane(obj=s).edges('not |Y').chamfer(0.2).val()
    # Arm passes ABOVE the fixed rails, with 0.6 mm vertical clearance.
    arm=base.rounded_box(AXIS-.5,REST_REAR+travel,27.2,207.9-(AXIS-.5),4,1.8,0.35)
    # A short straight terminal web connects to the flexure endpoint; this web
    # stays beside the track and is never drawn through its throat.
    web=base.box(AXIS-.5,REST_REAR-0.1+travel,21,1.0,4.1,8)
    return base.fuse(s,arm,web)


def spring(amplitude=AMPLITUDE):
    p,t=profile(amplitude)
    # Normal offsets maintain 1 mm thickness even on the steep entry arcs.
    normal=np.column_stack((np.cos(t),-np.sin(t)))
    left=p-THICKNESS/2*normal;right=p+THICKNESS/2*normal
    outline=np.vstack((left,right[::-1])).tolist()
    leaf=cq.Workplane('XY',origin=(0,0,Z)).polyline(outline).close().extrude(HEIGHT).val()
    root=base.rounded_box(200.5,14,25,18.7,11,4,1.2)
    neck=base.box(AXIS-.5,24.5,Z,1,0.6,HEIGHT)
    s=base.fuse(root,neck,leaf,shoe(p[-1,1]-REST_REAR))
    for x,y in MOUNTS: s=base.cut(s,base.cylinder(x,y,24.9,1.15,4.2))
    return s.clean()


def carrier():
    root=base.rounded_box(200.5,14,21,18.7,10,4,1.2)
    s=base.fuse(root,base.box(207.5,23.5,21,3.2,1.8,4),
                # Low spine lets the spring's mounting block pass above it
                # while the shoe is threaded in from the rear, off the fixture.
                base.box(207.5,25.3,21,3.2,TRACK_FRONT-25.3,3.6),
                base.box(203,TRACK_FRONT,21,7.7,TRACK_REAR-TRACK_FRONT,1.6),
                base.y_poly(0,TRACK_FRONT,0,LEFT_RAIL_XZ,TRACK_REAR-TRACK_FRONT),
                base.y_poly(0,TRACK_FRONT,0,RIGHT_RAIL_XZ,TRACK_REAR-TRACK_FRONT))
    for x,y in MOUNTS: s=base.cut(s,base.cylinder(x,y,20.9,1.15,4.2))
    return s.clean()


def lid():
    # Reserve a continuous side opening for the moving leaf and shoe arm.
    s=cq.importers.importStep(str(ROOT/'output/spring_guide/step/02_lid_with_spring.step')).val()
    return base.cut(s,base.box(199.5,24,18.5,4.0,110,11.1))


def overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    if any(getattr(aa,k+'max')<=getattr(bb,k+'min') or getattr(bb,k+'max')<=getattr(aa,k+'min') for k in 'xyz'):
        return 0.0
    return max(0.0,a.intersect(b).Volume())


def read_step(p): return cq.importers.importStep(str(p)).val()


def check(parts):
    frame=parts['19_shoe_track_PETG'];new_lid=parts['02_lid_sliding_shoe']
    shell={p.stem:read_step(p) for p in (ROOT/'output/step').glob('0*.step') if not p.stem.startswith('02')}
    shell['new_lid']=new_lid
    fixture={n:read_step(ROOT/'output/spring_guide/step'/f'{n}.step') for n in ('14_spring_test_bed','15_spring_test_mount')}
    obstacles=dict(shell,**fixture,**base.electronic_envelopes())
    failures=[];fixed=[]
    for n,s in obstacles.items():
        vol=overlap(frame,s)
        if vol>.025:fixed.append({'object':'track','part':n,'volume_mm3':round(vol,4)})
    for n,s in dict(shell,**base.electronic_envelopes()).items():
        if n=='new_lid':continue
        vol=overlap(new_lid,s)
        if vol>.025:fixed.append({'object':'new_lid','part':n,'volume_mm3':round(vol,4)})
    failures.extend(fixed)
    checks=[]
    for a in (27,24,23.4,20,16,12,8,4,3.4,1.4,0):
        s=spring(a);p,_=profile(a);travel=p[-1,1]-REST_REAR
        hits=[]
        for n,o in dict(obstacles,track=frame).items():
            vol=overlap(s,o)
            if vol>.025:hits.append({'part':n,'volume_mm3':round(vol,4)})
        checks.append({'amplitude_mm':a,'shoe_travel_mm':round(float(travel),4),'collisions':hits})
        failures.extend(hits)
        print('Clearance pose',a,'travel',round(travel,3),'hits',hits,flush=True)
    # Straight full-depth insertion clearance at the narrowest possible spring
    # shape for each case position. This does not simulate the contact dynamics.
    cases=[]
    for label,width,height in [('Blu-ray',170,14),('Blu-ray large',172,15),('DVD',190,14)]:
        for left in sorted(set([8.05,(208-width)/2,199.95-width])):
            amplitude=max(0,min(AMPLITUDE,AXIS-left-width-THICKNESS/2-.05))
            moving=spring(amplitude)
            hits=[]
            for leading in (25,45,65,85,108):
                case=base.box(left,leading-135,18.01,width,134.98,height)
                for n,o in dict(shell,**fixture,track=frame,spring=moving).items():
                    vol=overlap(case,o)
                    if vol>.03:hits.append({'leading_y_mm':leading,'part':n,'volume_mm3':round(vol,4)})
            cases.append({'case':label,'left_mm':left,'amplitude_mm':round(amplitude,3),'collisions':hits})
            failures.extend(hits)
    # Real rigid-foot travel sweep, independent of the assumed leaf shape.
    track_sweep=[]
    for travel in np.linspace(0,MAX_TRAVEL+0.5,57):
        foot=shoe(float(travel));vol=overlap(foot,frame)
        assert foot.BoundingBox().ymax<TRACK_REAR
        assert vol<.01,('shoe-track collision',travel,vol)
        track_sweep.append(round(float(travel),4))
    # Assembly is a real rigid translation of the PRINTED resting part. The
    # mounting block must pass over the carrier spine while entering the track.
    for travel in np.linspace(0,TRACK_REAR-SHOE_FRONT+1,21):
        translated=parts['18_spring_with_shoe_PETG'].translate((0,float(travel),0))
        vol=overlap(translated,frame)
        assert vol<.02,('off-fixture shoe threading collision',travel,vol)
    rear_stop_margins=[]
    for a in np.linspace(0,AMPLITUDE,301):
        p,t=profile(a,80)
        left=p-.5*THICKNESS*np.column_stack((np.cos(t),-np.sin(t)))
        if left[-1,1]>=108:
            x=float(np.interp(108,left[:,1],left[:,0]))
            rear_stop_margins.append(x-200)
    assert min(rear_stop_margins)>.4
    # The straightened length gives a geometric upper bound on endpoint travel
    # for the unextended neutral axis, regardless of its detailed bent shape.
    guide={'rest_leaf_length_mm':REST_LENGTH,'maximum_inextensible_end_travel_mm':MAX_TRAVEL,
           'leaf_height_mm':HEIGHT,'leaf_thickness_mm':THICKNESS,
           'leaf_to_deck_vertical_clearance_mm':Z-18,
           'minimum_sampled_bow_to_rear_stop_clearance_mm':min(rear_stop_margins),
           'assembly_slide_clearance_poses':21,
           'height_only_bending_stiffness_ratio_vs_8mm':HEIGHT/8,
           'track_y_mm':[TRACK_FRONT,TRACK_REAR],
           'shoe_y_at_rest_mm':[SHOE_FRONT,SHOE_REAR],
           'shoe_y_at_full_flat_mm':[SHOE_FRONT+MAX_TRAVEL,SHOE_REAR+MAX_TRAVEL],
           'rear_track_margin_at_full_flat_mm':TRACK_REAR-SHOE_REAR-MAX_TRAVEL,
           'body_rear_clearance_mm':141.6-TRACK_REAR,
           'shoe_side_clearance_each_mm':.4,'shoe_floor_clearance_mm':.4,
           'shoe_stem_side_clearance_each_mm':.6,'arm_above_rail_clearance_mm':.6,
           'rest_flexure_radius_mm':RADIUS,
           'idealized_outer_fiber_strain_full_flat_percent':100*THICKNESS/(2*RADIUS),
           'contact_land_length_mm':LAND,
           'contact_land_y_at_rest_mm':[FRONT+HALF_SPAN,FRONT+HALF_SPAN+LAND],
           'contact_land_y_at_full_flat_mm':[FRONT+2*ARC_LENGTH,FRONT+2*ARC_LENGTH+LAND],
           'curved_leaf_enters_track':False,
           'neutral_axis_extension_assumed':False,
           'rigid_shoe_sweep_poses':len(track_sweep),
           'rigid_shoe_sweep_extra_travel_mm':.5}
    report={'revision':3,'all_geometry_checks_passed':not failures,'fixed_collisions':fixed,
            'deflected_clearance_poses':checks,'case_clearance_checks':cases,'guide_geometry':guide,
            'method':'Four fixed-length circular arc segments plus fixed-length contact land; each arc changes curvature while preserving its own material length. Endpoint and rigid shoe translate; no curved strip feeds through a slot. Rigid shoe independently swept through its entire straight-line travel plus 0.5 mm. These are geometric checks, not a mechanical simulation.',
            'limitations':['No elastic equilibrium/contact/friction calculation.','PETG strain, force, creep, wear and actual printed sliding remain unverified.','Case insertion checks use pre-deflected poses; they do not prove that a child can produce them or that the case self-aligns.'],
            'physical_test_of_revision_3':(OUT/'validation/physical_test.json').exists(),
            'physical_test_record':json.loads((OUT/'validation/physical_test.json').read_text()) if (OUT/'validation/physical_test.json').exists() else None,
            'automatic_alignment_verified':False,
            'existing_fixture_reused':True,'existing_mounting_screws_reused':True,
            'fixture_step_sha256':{n:hashlib.sha256((ROOT/'output/spring_guide/step'/f'{n}.step').read_bytes()).hexdigest() for n in fixture}}
    (OUT/'validation/mechanics.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not failures,failures
    print('Revision 3 geometry checks passed.',flush=True)


def run():
    for f in ('stl','step','plates','preview','validation'):(OUT/f).mkdir(parents=True,exist_ok=True)
    parts={'18_spring_with_shoe_PETG':spring(),'19_shoe_track_PETG':carrier(),'02_lid_sliding_shoe':lid()}
    records={}
    for name,s in parts.items():
        assert s.isValid() and len(s.Solids())==1,(name,s.isValid(),len(s.Solids()))
        oriented=base.on_bed(s) if name.startswith('19') else base.invert(s)
        cq.exporters.export(s,str(OUT/'step'/f'{name}.step'))
        path=OUT/'stl'/f'{name}.stl'
        cq.exporters.export(oriented,str(path),tolerance=.035,angularTolerance=.10)
        mesh=trimesh.load_mesh(path)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1,name
        assert np.all(mesh.extents<=256),name
        records[name]={'size_mm':np.round(mesh.extents,3).tolist(),'volume_cm3':round(mesh.volume/1000,3),
                       'watertight':True,'single_body':True,'fits_A1':True}
        print(name,records[name],flush=True)
    (OUT/'validation/meshes.json').write_text(json.dumps(records,indent=2)+'\n')
    check(parts)


if __name__=='__main__':run()
