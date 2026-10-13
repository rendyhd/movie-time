"""Replaceable PETG side guide and adult-operated fit jig, units mm.

Keeps the existing base/deck/buttons; exports an alternative lid separately.
The displaced leaf is a beam approximation for checking space, not an FEA or
proof of force, fatigue life, automatic alignment or suitability for a child.
"""
from pathlib import Path
import sys
import json
import math
import hashlib
import cadquery as cq
import trimesh
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'model'))
import build_model as old

OUT = ROOT / 'output/spring_guide'
Z, HEIGHT = 21.0, 8.0
Y0, Y1 = 25.0, 102.0
X0, X1 = 201.1, 168.6
LENGTH = Y1 - Y0
TIP_RADIUS = 2.0
MOUNTS = [(205.0, 19.5), (214.0, 19.5)]


def beam_points(deflection=0.0, contact_y=Y1):
    """Curved stress-free beam; lateral displacement from an end/point load."""
    active = max(0.1, min(LENGTH, contact_y - Y0))
    result = []
    for y in np.linspace(Y0 - 1, Y1, 101):
        length = max(0, y - Y0)
        s = length / LENGTH
        q = length / active
        displacement = (q*q*(3-q)/2 if q <= 1 else 1 + 1.5*(q-1)) * deflection
        result.append((X0 - (X0-X1)*s**3 + displacement, float(y)))
    return result


def leaf(thickness=2.0, deflection=0.0, contact_y=Y1, edge_breaks=True):
    points = beam_points(deflection, contact_y)
    # XY outline keeps every layer continuous along the flexible leaf.
    outline = [(x-thickness/2, y) for x,y in points]
    outline += [(x+thickness/2, y) for x,y in reversed(points)]
    beam = cq.Workplane('XY', origin=(0,0,Z)).polyline(outline).close().extrude(HEIGHT).val()
    x,y = points[-1]
    tip = old.cylinder(x,y,Z,TIP_RADIUS,HEIGHT)
    mount = old.rounded_box(200.5,14,Z,18.7,11,HEIGHT,1.2)
    shape = old.fuse(mount,beam,tip)
    for x,y in MOUNTS:
        shape = old.cut(shape,old.cylinder(x,y,Z-0.1,1.15,HEIGHT+0.2))
    # Small edge breaks on both flat faces keep the sleeve away from sharp rims.
    if edge_breaks:
        shape = cq.Workplane(obj=shape).edges('>Z or <Z').chamfer(0.25).val()
    return shape


def revised_lid():
    lid = cq.importers.importStep(str(ROOT/'output/step/02_lid.step')).val()
    # Leaf passes through the original fixed right guide wall into a closed bay.
    lid = old.cut(lid,old.box(199.5,13.5,20.5,4,93.5,9.0))
    # New inner wall shields the spring from the electronics and loose wiring.
    lid = old.fuse(lid,old.box(211.0,27,18.0,2.4,80.0,17.6))
    for x,y in MOUNTS:
        lid = old.fuse(lid,old.cylinder(x,y,29,3.0,6.6))
        lid = old.cut(lid,old.cylinder(x,y,28.9,0.95,4.8))
    # A short lead-in on the left helps the case find its reference edge.
    funnel = cq.Workplane('XY',origin=(0,0,17.9)).polyline([
        (5.0,-0.1),(8.01,-0.1),(8.01,12.0),(5.0,0.0)
    ]).close().extrude(16.9).val()
    lid = old.cut(lid,funnel)
    # Clear the old rounded cavity corner: its small bulge was harmless at the
    # old 1 mm side clearance but would obstruct a spring-loaded case at X=8.
    lid = old.cut(lid,old.box(8.0,-0.1,17.9,4.0,12.1,16.9))
    return lid


def test_bed():
    # Open frame, with the same sliding plane, left reference and rear stop.
    floor = old.box(5.6,0,15.6,2.4,112,2.4)
    floor = old.fuse(floor,old.box(210.5,0,15.6,14.5,112,2.4))
    for y,depth in ((0,10),(49,7),(101,11)):
        floor = old.fuse(floor,old.box(5.6,y,15.6,219.4,depth,2.4))
    floor = old.fuse(floor,old.box(5.6,0,18,2.4,110.4,14),
                    old.box(8,108,18,192,2.4,14),
                    old.box(211,27,18,2.4,80,13),
                    old.box(219.9,14,18,4.6,11,11))
    floor = old.cut(floor,old.cylinder(222.2,19.5,17.9,0.95,11.2))
    funnel = cq.Workplane('XY',origin=(0,0,17.9)).polyline([
        (5.5,-0.1),(8.01,-0.1),(8.01,12),(5.5,0)
    ]).close().extrude(14.2).val()
    return old.cut(floor,funnel)


def test_mount():
    shape = old.rounded_box(200.0,13.0,29.0,25.0,13.0,5.0,1.2)
    for x,y in MOUNTS:
        shape = old.cut(shape,old.cylinder(x,y,28.9,0.95,4.6))
    return old.cut(shape,old.cylinder(222.2,19.5,28.9,1.15,5.2))


def required_deflection(case_right, leading_y):
    if leading_y <= Y0:
        return 0.0, Y1
    contact_y = min(Y1, leading_y)
    active = contact_y - Y0
    displacement = 0.0
    # Ignore the rounded tip until its front reaches the case. Once reached,
    # use its full radius conservatively, even during initial partial contact.
    tip_entered = leading_y >= Y1 - TIP_RADIUS
    if tip_entered:
        contact_y = Y1
        active = LENGTH
    points=beam_points()
    exact_y=min(Y1,leading_y)
    points.append((X0-(X0-X1)*((exact_y-Y0)/LENGTH)**3,exact_y))
    for x,y in points:
        if y > leading_y or y <= Y0:
            continue
        q = (y-Y0)/active
        gain = q*q*(3-q)/2 if q <= 1 else 1+1.5*(q-1)
        displacement = max(displacement, (case_right+1.05-x)/gain)
    if tip_entered:
        displacement = max(displacement,case_right+TIP_RADIUS+0.05-X1)
    return max(0,displacement),contact_y


def run():
    for sub in ('stl','step','validation','preview','plates'):
        (OUT/sub).mkdir(parents=True,exist_ok=True)
    parts = {
        '02_lid_with_spring':revised_lid(),
        '12_spring_standard_PETG':leaf(2.0),
        '13_spring_soft_PETG':leaf(1.6),
        '14_spring_test_bed':test_bed(),
        '15_spring_test_mount':test_mount(),
    }
    mesh_report = {}
    for name,shape in parts.items():
        assert shape.isValid() and len(shape.Solids()) == 1, name
        print_shape = old.invert(shape) if name.startswith('02') else old.on_bed(shape)
        cq.exporters.export(shape,str(OUT/'step'/f'{name}.step'))
        path = OUT/'stl'/f'{name}.stl'
        cq.exporters.export(print_shape,str(path),tolerance=0.035,angularTolerance=0.1)
        mesh = trimesh.load_mesh(path)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1,name
        assert max(mesh.extents) < 256,name
        mesh_report[name] = {'size_mm':np.round(mesh.extents,3).tolist(),
                             'volume_cm3':round(mesh.volume/1000,3),
                             'watertight':True,'single_body':True,'fits_A1':True}
        print(name,mesh_report[name],flush=True)
    (OUT/'validation/meshes.json').write_text(json.dumps(mesh_report,indent=2)+'\n')
    check(parts)


def check(parts):
    old_parts = {p.stem:cq.importers.importStep(str(p)).val()
                 for p in (ROOT/'output/step').glob('0*.step') if not p.stem.startswith('02')}
    lid = parts['02_lid_with_spring']
    guide = parts['12_spring_standard_PETG']
    obstacles = dict(old_parts, lid=lid)
    fixed_collisions = []
    env = old.electronic_envelopes()
    for name,shape in dict(old_parts,**env).items():
        volume = lid.intersect(shape).Volume()
        if volume > 0.02:
            fixed_collisions.append({'part':name,'volume_mm3':volume})
    for name,shape in dict(obstacles,**env).items():
        volume = guide.intersect(shape).Volume()
        if volume > 0.02:
            fixed_collisions.append({'spring_against':name,'volume_mm3':volume})
    stages = []
    failures = list(fixed_collisions)
    for label,width,thickness in [('DVD',190,14),('Blu-ray',170,14),('Blu-ray allowance',172,15)]:
        for left in sorted(set([8.05, (208-width)/2, 199.95-width])):
            for front in (30,45,60,80,100,108):
                right = left+width
                deflection, contact_y = required_deflection(right,front)
                moving = leaf(2.0,deflection,contact_y,edge_breaks=False)
                case = old.box(left,front-135,18.01,width,134.98,thickness)
                hits=[]
                for name,shape in obstacles.items():
                    for obj,s in [('case',case),('spring',moving)]:
                        volume = s.intersect(shape).Volume()
                        if volume > 0.03:
                            hits.append({'object':obj,'part':name,'volume_mm3':round(volume,4)})
                volume = case.intersect(moving).Volume()
                if volume > 0.03:
                    hits.append({'object':'case','part':'deflected spring','volume_mm3':round(volume,4)})
                stages.append({'case':label,'left_mm':left,'leading_edge_y_mm':front,
                               'point_deflection_mm':round(deflection,3),
                               'load_y_mm':contact_y,'collisions':hits})
                if hits:failures.append(stages[-1])
            print('Checked',label,'left',left,flush=True)
    # Jig uses the same spring placement, and its removable bridge prints flat.
    jig = [parts['14_spring_test_bed'],parts['15_spring_test_mount'],guide]
    jig_hits=[]
    for a in range(len(jig)):
        for b in range(a+1,len(jig)):
            vol=jig[a].intersect(jig[b]).Volume()
            if vol>0.02:jig_hits.append([a,b,vol])
    failures.extend(jig_hits)
    report={'status':'prototype_requires_physical_test','fixed_collisions':fixed_collisions,
            'jig_collisions':jig_hits,'insertion_stages':stages,'all_checks_passed':not failures,
            'method':'Cubic unloaded centerline; point-load Euler-Bernoulli displacement used only to check available space. Large deflection, friction, material creep and fatigue are not validated by this model.',
            'case_left_reference_mm':8.0,'tip_diameter_mm':4.0,
            'spring_material':'unfilled PETG','spring_height_mm':HEIGHT,
            'spring_thickness_options_mm':[2.0,1.6],
            'mount_fasteners':'2 x M2 x 12 mm pan head',
            'physical_force_verified':False,'self_alignment_verified':False,
            'cycle_life_verified':False,'nfc_tested':False,
            'sources':['https://www.prusa3d.com/product/prusament-petg-clear-1kg/']}
    (OUT/'validation/mechanics.json').write_text(json.dumps(report,indent=2)+'\n')
    assert not failures,failures
    print('Spring space and insertion checks passed.',flush=True)


if __name__ == '__main__':
    run()
