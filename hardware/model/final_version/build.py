"""Final single-leaf revision: one PETG part and matching cute PLA lid.

STLs are oriented for printing, STEP files are in assembly coordinates.
The root is the original 8 mm block, reusing the original fixture and screws.
"""
from pathlib import Path
import sys,json,shutil,hashlib
import numpy as np
import cadquery as cq
import trimesh
from leaf_motion import (OUT,ROOT,natural_profile,THICKNESS,HEIGHT,Z,X0,Y0,
                         TIP_RADIUS,LENGTH,RADIUS,ANGLE,ROOT_THICKNESS,
                         ROOT_TAPER_LENGTH,thickness_at)

sys.path.insert(0,str(ROOT/'model'))
import build_model as base
MOUNTS=[(205.,19.5),(214.,19.5)]


def root_block():
    s=base.rounded_box(200.5,14,21,18.7,11,8,1.2)
    for x,y in MOUNTS:s=base.cut(s,base.cylinder(x,y,20.9,1.15,8.2))
    return s


def original_beveled_spring():
    """Retain the proven span and its small contact-edge bevels exactly."""
    p,t=natural_profile(2)
    normal=np.column_stack((np.cos(t),-np.sin(t)))
    left=p-TIP_RADIUS*normal;right=p+TIP_RADIUS*normal
    cap=p[-1]+TIP_RADIUS*np.array([np.sin(t[-1]),np.cos(t[-1])])
    w=cq.Workplane('XY',origin=(0,0,Z)).moveTo(*left[0])
    w=w.threePointArc(tuple(left[1]),tuple(left[2])).threePointArc(tuple(left[3]),tuple(left[4]))
    w=w.threePointArc(tuple(cap),tuple(right[4]))
    w=w.threePointArc(tuple(right[3]),tuple(right[2])).threePointArc(tuple(right[1]),tuple(right[0]))
    leaf=w.close().extrude(HEIGHT).val()
    neck=base.box(X0-TIP_RADIUS,24.5,Z,THICKNESS,.5,HEIGHT)
    return cq.Workplane(obj=base.fuse(root_block(),leaf,neck)).edges('>Z or <Z').chamfer(.15).val()


def reinforced_fin():
    p,t=natural_profile(2)
    normal=np.column_stack((np.cos(t),-np.sin(t)))
    left=p-TIP_RADIUS*normal;right=p+TIP_RADIUS*normal
    cap=p[-1]+TIP_RADIUS*np.array([np.sin(t[-1]),np.cos(t[-1])])
    distances=np.linspace(0,ROOT_TAPER_LENGTH,25)
    angles=-distances/RADIUS
    centre=np.column_stack((X0+RADIUS*(np.cos(angles)-1),Y0-RADIUS*np.sin(angles)))
    normals=np.column_stack((np.cos(angles),-np.sin(angles)))
    half=thickness_at(distances)[:,None]/2
    taper_left=centre-half*normals;taper_right=centre+half*normals
    middle_angle=(-ROOT_TAPER_LENGTH/RADIUS-ANGLE)/2
    middle=np.array([X0+RADIUS*(np.cos(middle_angle)-1),Y0-RADIUS*np.sin(middle_angle)])
    middle_normal=np.array([np.cos(middle_angle),-np.sin(middle_angle)])
    end_tangent=(float(np.sin(angles[-1])),float(np.cos(angles[-1])))
    w=cq.Workplane('XY',origin=(0,0,Z)).moveTo(X0-ROOT_THICKNESS/2,22.5).lineTo(*taper_left[0])
    w=w.spline([tuple(v) for v in taper_left[1:]],includeCurrent=True,tangents=[(0,1),end_tangent])
    w=w.threePointArc(tuple(middle-TIP_RADIUS*middle_normal),tuple(left[2])).threePointArc(tuple(left[3]),tuple(left[4]))
    w=w.threePointArc(tuple(cap),tuple(right[4]))
    w=w.threePointArc(tuple(right[3]),tuple(right[2])).threePointArc(tuple(middle+TIP_RADIUS*middle_normal),tuple(taper_right[-1]))
    w=w.spline([tuple(v) for v in taper_right[-2::-1]],includeCurrent=True,
               tangents=[tuple(-v for v in end_tangent),(0,-1)])
    w=w.lineTo(X0+ROOT_THICKNESS/2,22.5).close()
    leaf=w.extrude(HEIGHT).val()
    # The fin continues 2.5 mm into the mounting block. A 45-degree underside
    # blend replaces the former 0.5 mm thin projection and abrupt height step.
    wedge=cq.Workplane('YZ',origin=(199,0,0)).polyline([
        (22.4,18.9),(24.6,18.9),(22.4,21.1)]).close().extrude(7).val()
    return base.cut(leaf,wedge)


def spring(edge_breaks=True,round_joint=True):
    s=base.fuse(root_block(),reinforced_fin())
    if round_joint:
        # Concave shoulder edges only; do not fillet the screw holes or flexing
        # span. The wider attachment is blended into the mounting-block face.
        for side,radius in [('right',1.2),('left',.4)]:
            candidates=[]
            for edge in s.Edges():
                c=edge.Center();bb=edge.BoundingBox()
                near=(203.0<c.x<203.4 and 24.9<c.y<25.1) if side=='right' else (200.6<c.x<201.0 and 24.2<c.y<24.9)
                if edge.geomType()=='LINE' and near and bb.zlen>7:
                    candidates.append(edge)
            assert len(candidates)==1,(side,[(e.Center().toTuple(),e.Length()) for e in candidates])
            s=s.fillet(radius,candidates).clean()
    if edge_breaks:
        # Local reinforcement is added to the existing beveled part. This
        # preserves the original contact surface beyond the attachment and
        # avoids propagating a bevel through the small concave root fillets.
        attachment=s.intersect(base.box(195,13,18,30,14.5,12))
        s=base.fuse(original_beveled_spring(),attachment)
    return s


def lid():
    s=cq.importers.importStep(str(ROOT/'output/step/02_lid.step')).val()
    # Open sweep pocket, no rear guide, track, spring carrier or moving shoe.
    s=base.cut(s,base.box(199.5,13.5,18.5,4,75.5,11))
    # Fixed screen keeps the flexible leaf away from the button/electronics wires.
    s=base.fuse(s,base.box(211,27,18,2.4,62,17.6))
    for x,y in MOUNTS:
        s=base.fuse(s,base.cylinder(x,y,29,3,6.6))
        s=base.cut(s,base.cylinder(x,y,28.9,.95,4.8))
    funnel=cq.Workplane('XY',origin=(0,0,17.9)).polyline([
        (5.,-.1),(8.01,-.1),(8.01,12.),(5.,0.)]).close().extrude(16.9).val()
    s=base.cut(s,funnel,base.box(8.,-.1,17.9,4.,12.1,16.9))
    return s


def shape_from_points(p):
    # Use the solved rod path, with normal offsets and rounded free edge.
    tangent=np.gradient(p,axis=0)
    tangent/=np.linalg.norm(tangent,axis=1)[:,None]
    n=np.column_stack((tangent[:,1],-tangent[:,0]))
    arclength=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    half=thickness_at(arclength)[:,None]/2
    left=p-half*n;right=p+half*n
    outline=np.vstack((left,right[::-1])).tolist()
    s=cq.Workplane('XY',origin=(0,0,Z)).polyline(outline).close().extrude(HEIGHT).val()
    cap=base.cylinder(*p[-1],Z,TIP_RADIUS,HEIGHT)
    return base.fuse(s,cap,root_block())


def read(path):return cq.importers.importStep(str(path)).val()


def overlap(a,b):
    aa,bb=a.BoundingBox(),b.BoundingBox()
    if any(getattr(aa,c+'max')<=getattr(bb,c+'min') or getattr(bb,c+'max')<=getattr(aa,c+'min') for c in 'xyz'):return 0.
    return max(0.,a.intersect(b).Volume())


def check(parts):
    fixed={k:v for k,v in parts.items() if k!='12_single_leaf_PETG'}
    fixture={n:read(ROOT/'output/spring_guide/step'/f'{n}.step') for n in ('14_spring_test_bed','15_spring_test_mount')}
    electronics=base.electronic_envelopes()
    failures=[]
    for n,s in dict(fixed,**fixture,**electronics).items():
        vol=overlap(parts['12_single_leaf_PETG'],s)
        if vol>.03:failures.append({'object':'unloaded spring','part':n,'volume_mm3':vol})
    for n,s in dict(fixed,**electronics).items():
        if n=='02_cute_lid_single_leaf':continue
        vol=overlap(parts['02_cute_lid_single_leaf'],s)
        if vol>.03:failures.append({'object':'new lid','part':n,'volume_mm3':vol})
    poses=np.load(OUT/'validation/motion_poses.npz')
    motion=[]
    # Geometry checks use solved contact paths at key insertion stages.
    for right in (178.05,180.05,189.,190.,198.05,199.,199.95):
        for leading in (35,47,59,71,83,108):
            p=poses[f'{right}_{leading}'];s=shape_from_points(p)
            hits=[]
            for n,o in dict(fixed,**fixture,**electronics).items():
                vol=overlap(s,o)
                if vol>.04:hits.append({'part':n,'volume_mm3':round(vol,5)})
            # A conservative left face at X=8.05, rear stop at Y=108, and 15 mm
            # height cover the thick Blu-ray and both nominal case thicknesses.
            case=base.box(8.05,leading-135,18.01,right-8.05,134.98,15)
            for n,o in dict(fixed,**fixture,spring=s).items():
                vol=overlap(case,o)
                if vol>.04:hits.append({'case_against':n,'volume_mm3':round(vol,5)})
            motion.append({'case_right_mm':right,'leading_y_mm':leading,'collisions':hits})
            failures.extend(hits)
        print('Solid clearances checked',right,flush=True)
    # Verify button motion against the final lid, since it carries the mounts.
    for button in ('04_button_play','05_button_pause','06_button_stop'):
        for travel in (.2,.45,.64):
            vol=overlap(parts[button].translate((0,travel,0)),parts['02_cute_lid_single_leaf'])
            if vol>.02:failures.append({'button':button,'travel_mm':travel,'volume_mm3':vol})
    report={'all_solid_clearance_checks_passed':not failures,'failures':failures,
            'case_motion_poses':motion,'body_mm':[250,144,38],'slot_mm':[192,16.8],
            'case_depth_mm':135,'insertion_depth_mm':108,'spine_exposed_mm':27,
            'existing_fixture_reused':True,'spring_mounting_block_height_mm':8,
            'spring_mount_screws':'2 x M2 x 12 mm, from below',
            'physical_test_status':'not yet physically tested',
            'fixture_hashes':{n:hashlib.sha256((ROOT/'output/spring_guide/step'/f'{n}.step').read_bytes()).hexdigest() for n in fixture}}
    (OUT/'validation/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not failures,failures
    print('Final single-leaf solid checks passed.',flush=True)


def run(spring_only=False):
    for f in ('stl','step','plates','preview','validation'):(OUT/f).mkdir(parents=True,exist_ok=True)
    if spring_only:
        parts={p.stem:read(p) for p in (OUT/'step').glob('0*.step')}
        parts['12_single_leaf_PETG']=spring()
        meshes=json.loads((OUT/'validation/meshes.json').read_text())
        changed=('12_single_leaf_PETG',)
    else:
        parts={p.stem:read(p) for p in (ROOT/'output/step').glob('0*.step') if not p.stem.startswith('02')}
        for n in parts:
            for folder,ext in [('stl','stl'),('step','step')]:
                shutil.copy2(ROOT/'output'/folder/f'{n}.{ext}',OUT/folder/f'{n}.{ext}')
        parts.update({'02_cute_lid_single_leaf':lid(),'12_single_leaf_PETG':spring()})
        parts['07_switch_carrier']=base.carrier_frame();parts['08_switch_retainer']=base.retainer()
        for index,kind,x in zip((4,5,6),('play','pause','stop'),base.BX):
            parts[f'{index:02d}_button_{kind}']=base.button(kind).translate((x,0,base.BZ))
        meshes={}
        changed=('02_cute_lid_single_leaf','12_single_leaf_PETG','04_button_play','05_button_pause',
                 '06_button_stop','07_switch_carrier','08_switch_retainer')
    for name in changed:
        s=parts[name]
        assert s.isValid() and len(s.Solids())==1,(name,s.isValid(),len(s.Solids()))
        cq.exporters.export(s,str(OUT/'step'/f'{name}.step'))
        path=OUT/'stl'/f'{name}.stl'
        if name=='07_switch_carrier':printed=base.on_bed(s.rotate((0,0,0),(1,0,0),-90))
        elif name=='08_switch_retainer' or 'button_' in name:printed=base.front_down(s)
        else:printed=base.invert(s)
        cq.exporters.export(printed,str(path),tolerance=.035,angularTolerance=.1)
        m=trimesh.load_mesh(path)
        assert m.is_watertight and m.is_winding_consistent and m.body_count==1,name
        assert np.all(m.extents<=256),name
        meshes[name]={'size_mm':m.extents.round(3).tolist(),'volume_cm3':round(float(m.volume)/1000,3),
                      'watertight':True,'single_body':True,'fits_A1':True}
        print(name,meshes[name],flush=True)
    (OUT/'validation/meshes.json').write_text(json.dumps(meshes,indent=2)+'\n')
    assembly=cq.Assembly(name='Movie_Time_Final_Single_Leaf')
    # Resting leaf is valid in the empty assembled enclosure.
    for n,s in parts.items():
        assembly.add(s,name=n,color=cq.Color(.48,.62,.46) if 'button_' in n or 'leaf_PETG' in n else cq.Color(.86,.82,.72))
    assembly.export(str(OUT/'step/Movie_Time_final_assembled.step'))
    check(parts)


if __name__=='__main__':run(spring_only='--spring-only' in sys.argv)
