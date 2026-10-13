"""Movie Time v2. Units: mm. Original parametric CadQuery enclosure.

Coordinates in assembly: X left-to-right, Y front-to-back, Z up.
DVD: long spine parallel to X, spine at Y=-27, opening edge at Y=108.
STLs are individually oriented on Z=0 for printing. STEP is assembled.
Run from project root: .venv/bin/python model/build_model.py
"""
from pathlib import Path
import json
import math
import cadquery as cq
import trimesh
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
P = json.loads((Path(__file__).parent / 'parameters.json').read_text())
W, D, H, T = [P[k] for k in ('body_width','body_depth','body_height','wall')]
DECK = P['deck_height']
DZ = DECK - P['deck_thickness']
STOP = P['case_depth'] * P['insertion_fraction']
SL = P['slot_left']
SR = SL + P['case_spine'] + 2*P['case_side_clearance']
BX = P['button_centres']
BZ = P['button_z']

def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z)).val()

def cylinder(x,y,z,r,h,axis=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*axis))

def rounded_box(x,y,z,dx,dy,dz,r):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).edges('|Z').fillet(r).translate((x,y,z)).val()

def fuse(shape, *others):
    for other in others:
        shape = shape.fuse(other)
    return shape.clean()

def cut(shape,*others):
    for other in others:
        shape=shape.cut(other)
    return shape.clean()

def y_cyl(x,y,z,r,length):
    return cylinder(x,y,z,r,length,(0,1,0))

def y_poly(x,y,z,points,length):
    # XZ workplane extrudes towards -Y.
    return cq.Workplane('XZ',origin=(x,y+length,z)).polyline(points).close().extrude(length).val()

def base():
    s=rounded_box(0,0,0,W,D,DECK,P['corner_radius'])
    s=cut(s,rounded_box(T,T,T,W-2*T,D-2*T,DECK+1,P['corner_radius']-T))
    # Case deck perimeter seats, all below the sliding surface.
    for b in [(T,T,T,SL+2-T,STOP-T,DZ-T),
              (SR-2,T,T,4.4,STOP-T,DZ-T),
              (SL,T,T,SR-SL,2.8,DZ-T)]:
        s=fuse(s,box(*b))
    # Full insertion stop. Wire tunnels remain wholly below the deck.
    stop=box(SL,STOP,T,SR-SL,2.4,31.0)
    for x in (65,180):
        stop=cut(stop,box(x,STOP-0.1,3.4,8,2.6,7))
    s=fuse(s,stop)
    for x,y in P['deck_screws']:
        s=fuse(s,cylinder(x,y,T,3.6,DZ-T))
        s=cut(s,cylinder(x,y,8.0,1.35,DZ-8+0.1))
    # Four screw columns outside the case's insertion envelope.
    for x,y in P['lid_screws']:
        s=fuse(s,cylinder(x,y,T,3.6,DECK-T))
        s=cut(s,cylinder(x,y,-0.1,1.65,DECK+0.2),cylinder(x,y,-0.1,3.15,1.5))
    # PN532 corner pads: component side down, antenna side up.
    px,py=P['pn532_centre']; pw,ph=P['pn532_board']
    for x in (px-pw/2,px+pw/2-2.6):
        for y in (py-ph/2,py+ph/2-3.0):
            s=fuse(s,box(x,y,T,2.6,3.0,P['pn532_pcb_bottom']-T))
    # Nylon strap slots outside the PN532. No metal mounting hardware by antenna.
    for y in (65.0,90.0):
        for x in (10.4,57.5):
            s=cut(s,box(x,y-1.7,-0.1,1.6,3.4,T+0.2))
    # D1 Mini landing rails, 30 mm clear width, rear USB-facing.
    for x in (205.5,237.5):
        s=fuse(s,box(x,102,T,1.6,37,3.6))
    for y in (104.0,131.0):
        for x in (208.0,233.0):
            s=fuse(s,box(x,y,T,2.0,4.0,2.6))
    # Board and USB strain-relief cable-tie slots.
    for x,y,dx,dy in [(203,111,1.6,3.4),(239.5,111,1.6,3.4),
                      (214,139,3.4,1.6),(231,139,3.4,1.6)]:
        s=cut(s,box(x,y,-0.1,dx,dy,T+0.2))
    # Generous open USB access, independent of clone port exact Z position.
    s=cut(s,box(211,139.5,3.0,25,5,DECK-3+0.2))
    # 24 mm universal buzzer zone, bottom sound grille, secure with foam tape.
    for dx,dy in [(-5,-3),(0,-3),(5,-3),(-5,3),(0,3),(5,3)]:
        s=cut(s,cylinder(224+dx,48+dy,-0.1,1.25,T+0.2))
    for x in (211,235):
        s=cut(s,box(x,46.3,-0.1,1.6,3.4,T+0.2))
    # LED on front, below the button row. Rails accept a cut WS2812 strip pixel.
    for x in (202,217):
        s=fuse(s,box(x,2.4,T,1.4,7.6,13.6))
    s=cut(s,y_cyl(210,-0.1,10,1.7,T+0.2))
    # Low wire-routing fences, with accessible open tops.
    for x,y,dx,dy in [(65,113,127,1.2),(65,123,127,1.2),
                      (200.8,28,1.2,62),(209,76,27,1.2),
                      (70,69,20,1.2),(70,79,20,1.2)]:
        s=fuse(s,box(x,y,T,dx,dy,2.4))
    for x,y in [(92,117),(161,117),(205,88),(200,35),(83,74)]:
        for dx in (-3,3):
            s=cut(s,box(x+dx,y-1.6,-0.1,1.4,3.2,T+0.2))
    # Alignment pins in rear wall; clear holes in lid.
    for x in (50,180):
        s=fuse(s,cylinder(x,D-1.3,DECK,0.85,1.8))
    return s.clean()

def carrier_frame():
    # The measured switch is 6 x 6 x 4 mm, plus a 1 mm actuator.
    # Three guide tubes accept the narrow cap pins and stop the rear flanges.
    # Switch retention comes from the rear plate, not an interference fit.
    front=P['switch_body_front_y'];back=front+P['switch_body_depth']
    pocket=P['switch_body_width'];guide=P['button_guide_front_y']
    frame_front=P.get('switch_carrier_front_y',6.8)
    shift=frame_front-6.8
    s=box(202.8,frame_front,20.0,43.2,back-frame_front,15.6)
    for x in BX:
        s=fuse(s,y_cyl(x,guide,BZ,4.2,frame_front-guide+.05))
        s=cut(s,box(x-pocket/2,front,BZ-pocket/2,pocket,back-front+.1,pocket),
                 y_cyl(x,guide-.1,BZ,2.1,front-guide+.2))
        # Lead reliefs extend to 8.2 mm total width at the body back.
        for dz in (-2.25,2.25):
            s=cut(s,box(x-4.2,8.5+shift,BZ+dz-0.9,8.4,back-8.5-shift+.1,1.8))
    for x in (204.8,244.0):
        s=cut(s,y_cyl(x,frame_front-.1,32.1,0.95,back-frame_front+.2))
    for x in (215.25,228.75):
        # Open clearance at the nearer front edge; avoid a tangent zero-width
        # web where the old 2.8 mm pocket met the relocated frame.
        s=cut(s,cylinder(x,8.8,19.9,1.15,16),cylinder(x,8.8,30,2.9,6))
    return s

def top_artwork():
    """Shallow, rounded line art. The lid still prints top-face down.

    Eyes, smile, blush cheeks and three tiny cinema-night accents.
    Cut depth 0.6 leaves 1.8 mm of the original roof beneath every mark.
    Shapes are centered on the enclosure and face the person loading a case.
    """
    depth=P.get('top_engraving_depth',0.6)
    assert 0 < depth <= T-1.6, 'Keep at least 1.6 mm of roof below engraving'
    z=H-depth
    shapes=[]
    cx=W/2

    def stroke(points,width=1.6):
        # Round-ended planar capsule segments; robust and printable at 0.4 nozzle.
        solid=None
        for a,b in zip(points,points[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1]
            length=math.hypot(dx,dy)
            if length < 1e-7:
                continue
            seg=box(0,-width/2,z,length,width,depth+0.1).rotate((0,0,0),(0,0,1),math.degrees(math.atan2(dy,dx))).translate((a[0],a[1],0))
            seg=fuse(seg,cylinder(a[0],a[1],z,width/2,depth+0.1),cylinder(b[0],b[1],z,width/2,depth+0.1))
            solid=seg if solid is None else fuse(solid,seg)
        shapes.append(solid)

    # Resting eyelids curve gently down toward the front of the player.
    for eye_x in (cx-18,cx+18):
        stroke([(eye_x+6.0*t,76.0+3.7*t*t) for t in np.linspace(-1,1,19)])
    # Two little adjoining arcs make a contented, cat-like smile.
    points=[]
    for mouth_x in (cx-2.8,cx+2.8):
        points.extend([(mouth_x+2.8*t,62.2+2.3*t*t) for t in np.linspace(-1,1,15)])
    stroke(points,1.4)
    for cheek_x in (cx-32,cx+32):
        shapes.append(cq.Workplane('XY',origin=(cheek_x,68,z)).ellipse(4.5,1.9).extrude(depth+0.1).val())
    # A small heart above the face; its point faces the DVD slot.
    heart=[(0,-4),(-4.2,0.4),(-4.4,2),(-3.6,3.5),(-2,4),(0,2.4),
           (2,4),(3.6,3.5),(4.4,2),(4.2,0.4)]
    shapes.append(cq.Workplane('XY',origin=(cx,98,z)).polyline(heart).close().extrude(depth+0.1).val())
    for sx,sy,size in ((cx-45,95,3.6),(cx+46,91,4.6)):
        star=[(0,size),(1.05,1.05),(size,0),(1.05,-1.05),(0,-size),
              (-1.05,-1.05),(-size,0),(-1.05,1.05)]
        shapes.append(cq.Workplane('XY',origin=(sx,sy,z)).polyline(star).close().extrude(depth+0.1).val())
    return cq.Compound.makeCompound(shapes)

def lid():
    outer=rounded_box(0,0,DECK,W,D,H-DECK,P['corner_radius'])
    outer=cq.Workplane(obj=outer).edges('>Z').fillet(2.0).val()
    s=cut(outer,rounded_box(T,T,DECK-0.1,W-2*T,D-2*T,H-DECK-T+0.1,P['corner_radius']-T))
    # Guide walls and screw columns meet the underside of the roof.
    s=fuse(s,box(T,T,DECK,SL-T,STOP-T,H-T-DECK),
             box(SR,T,DECK,2.4,STOP-T,H-T-DECK))
    for x,y in P['lid_screws']:
        s=fuse(s,cylinder(x,y,DECK,3.6,H-T-DECK))
        s=cut(s,cylinder(x,y,DECK-0.1,1.35,11.6))
    s=cut(s,box(SL,-0.1,DECK-0.1,SR-SL,T+0.2,P['slot_top']-DECK+0.1))
    # Separate button caps enter from inside, retained by their rear flanges.
    for x in BX:
        s=cut(s,y_cyl(x,-0.2,BZ,P['button_hole_diameter']/2,T+0.4))
        s=cut(s,y_cyl(x,2.4,BZ,6.95,1.85))
        # Hidden rails capture a flange key: the visible button stays circular.
        for dx in (-2.5,1.3):
            s=fuse(s,box(x+dx,2.4,BZ+6.8,1.2,2.3,H-T-(BZ+6.8)))
    # Removable carrier: caps must be inserted before the carrier is installed.
    for x in (215.25,228.75):
        s=fuse(s,cylinder(x,8.8,30,2.5,H-T-30))
        s=cut(s,cylinder(x,8.8,29.9,0.95,6.1))
    for x in (50,180):
        s=cut(s,cylinder(x,D-1.3,DECK-0.1,1.2,2.2))
    if P.get('top_decoration',True):
        s=cut(s,top_artwork())
    return s.clean()

def deck():
    s=box(SL+0.3,T+0.25,DZ,SR-SL-0.6,STOP-T-0.45,P['deck_thickness'])
    px,py=P['pn532_centre']
    # Thin roof over antenna, smooth upper surface, no hole into the case slot.
    s=cut(s,box(px-24,py-23,DZ-0.1,48,46,P['deck_thickness']-P['nfc_membrane']+0.1))
    for y in (20,43,100):
        s=fuse(s,box(SL+2.2,y,DZ-2.8,SR-SL-4.4,1.8,2.8))
    s=fuse(s,box(108,6,DZ-2.8,1.8,96,2.8))
    for x,y in P['deck_screws']:
        s=cut(s,cylinder(x,y,DZ-3.0,3.85,3.0))
        s=cut(s,cylinder(x,y,DZ-3,1.65,7),
              cq.Solid.makeCone(1.65,3.2,1.55,cq.Vector(x,y,DECK-1.55)))
    return s.clean()

def button(kind):
    # Model at X=0, Z=0, assembled axis +Y. Engraved front at Y=-1.4.
    s=y_cyl(0,-1.4,0,P['button_diameter']/2,3.8)
    s=fuse(s,y_cyl(0,2.4,0,6.6,1.0),
             box(-0.95,2.4,5.0,1.9,1.0,3.4),
             y_cyl(0,3.4,0,P['button_pin_diameter']/2,P['button_stem_tip_y']-3.4))
    if kind=='play':
        icon=y_poly(0,-1.5,0,[(-1.8,-2.5),(-1.8,2.5),(2.5,0)],0.65)
    elif kind=='pause':
        icon=fuse(box(-2.2,-1.5,-2.5,1.35,0.65,5),box(0.85,-1.5,-2.5,1.35,0.65,5))
    else:
        icon=box(-2.1,-1.5,-2.1,4.2,0.65,4.2)
    return cut(s,icon)

def retainer():
    back=P['switch_body_front_y']+P['switch_body_depth']
    thick=P.get('switch_retainer_thickness',1.8)
    s=box(203.0,back,20.4,43.0,thick,13.6)
    for x in BX:
        for dz in (-2.25,2.25):
            s=cut(s,box(x-4.4,back-.1,BZ+dz-1.0,8.8,thick+.2,2.0))
    for x in (204.8,244.0):
        s=cut(s,y_cyl(x,back-.1,32.1,1.15,thick+.2))
    for x in (215.25,228.75):
        s=cut(s,cylinder(x,8.8,29.8,2.8,4.4))
    return s

def lens():
    return fuse(y_cyl(210,-0.2,10,1.5,2.8),y_cyl(210,2.4,10,2.75,1.0))

def electronic_envelopes():
    px,py=P['pn532_centre']; pw,ph=P['pn532_board']
    result={
        'PN532_PCB':box(px-pw/2,py-ph/2,12.6,pw,ph,1.6),
        'PN532_components':box(px-17,py-16,7.2,34,32,5.4),
        'D1_Mini_PCB':box(209.2,104.0,5.0,25.6,34.2,1.6),
        'D1_Mini_components':box(210.0,105.0,6.6,24,27,5.5),
        'USB_connector':box(218,133,6.6,9,9,4),
        'Buzzer_envelope':cylinder(224,48,2.4,10,10),
        'WS2812_PCB':box(204.5,4.5,3.0,11,1.0,14),
        'WS2812_pixel':box(207.5,3.5,7.5,5,1,5),
    }
    for x,kind in zip(BX,('play','pause','stop')):
        front=P['switch_body_front_y'];height=P['switch_actuator_height']
        result[f'{kind}_switch_body']=box(x-3,front,BZ-3,6,P['switch_body_depth'],6)
        # Clearance envelope ahead of the body, calibrated to the measured
        # installed contact face. The earlier nominal exposed height did not
        # reproduce the user's installed recess. Do not silently replace the
        # reported 1 mm component height: retain it in parameters as supplied.
        face=(P['button_guide_front_y']+P['switch_installed_actuator_recess']
              if 'switch_installed_actuator_recess' in P else front-height)
        assert face<front
        if 'switch_measured_travel' in P:
            # The envelope's solid box does not represent the moving actuator
            # well. Reserve its swept diameter using the measured installed
            # contact face and full travel, including the portion inside the
            # nominal body reference. No internal switch structure is modeled.
            result[f'{kind}_switch_body']=cut(result[f'{kind}_switch_body'],
                y_cyl(x,face-.1,BZ,P['switch_actuator_diameter']/2,
                      front-face+P['switch_measured_travel']+.2))
        result[f'{kind}_switch_plunger']=y_cyl(x,face,BZ,P['switch_actuator_diameter']/2,front-face)
    return result

def on_bed(s):
    bb=s.BoundingBox()
    return s.translate((-bb.xmin,-bb.ymin,-bb.zmin))

def invert(s):
    return on_bed(s.rotate((0,0,0),(1,0,0),180))

def front_down(s):
    return on_bed(s.rotate((0,0,0),(1,0,0),90))

def build():
    for d in ('stl','step','preview','validation','plates'):
        (OUT/d).mkdir(parents=True,exist_ok=True)
    parts={}
    for name, fn in [('01_base',base),('02_lid',lid),('03_case_deck',deck),('07_switch_carrier',carrier_frame),('08_switch_retainer',retainer),('09_led_lens',lens)]:
        print('Building',name,flush=True)
        parts[name]=fn()
    for i,kind in enumerate(('play','pause','stop'),4):
        parts[f'{i:02d}_button_{kind}']=button(kind).translate((BX[i-4],0,BZ))
    # Coupon is an exact crop of the lid's three-button region, not a substitute geometry.
    parts['10_button_fit_test']=parts['02_lid'].intersect(box(201.0,-0.5,18,49.0,15,20.1)).clean()
    # Full-width, low-material DVD fit gauge: opening exactly 192 x 16.8 mm.
    gauge=box(0,0,0,198,8,22.8)
    gauge=cut(gauge,box(3,-0.1,3,SR-SL,8.2,P['slot_top']-DECK))
    parts['11_case_fit_test']=gauge
    records={}
    for name,s in parts.items():
        if name in ('02_lid','03_case_deck','10_button_fit_test'):
            pr=invert(s)
        elif 'button_' in name and name!='10_button_fit_test':
            pr=front_down(s)
        elif name=='07_switch_carrier':
            pr=on_bed(s.rotate((0,0,0),(1,0,0),-90))
        elif name in ('08_switch_retainer','09_led_lens'):
            pr=front_down(s)
        elif name=='11_case_fit_test':
            pr=front_down(s)
        else:
            pr=on_bed(s)
        assert s.isValid(), f'{name}: invalid BREP'
        assert len(s.Solids())==1, f'{name}: disconnected solids {len(s.Solids())}'
        cq.exporters.export(pr,str(OUT/'stl'/f'{name}.stl'),tolerance=0.035,angularTolerance=0.1)
        cq.exporters.export(s,str(OUT/'step'/f'{name}.step'))
        mesh=trimesh.load_mesh(OUT/'stl'/f'{name}.stl')
        records[name]={'size_mm':np.round(mesh.extents,3).tolist(),'volume_cm3':round(mesh.volume/1000,3),
                       'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
                       'connected_bodies':int(mesh.body_count),'triangles':len(mesh.faces),
                       'brep_valid':True,'fits_A1':bool(np.all(mesh.extents<=[256,256,256]))}
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1, (name,records[name])
        assert records[name]['fits_A1']
        print(name,records[name]['size_mm'],flush=True)
    assembly=cq.Assembly(name='Movie_Time_NFC_DVD_case_player')
    for name,s in parts.items():
        if name.startswith(('10','11')): continue
        color=cq.Color(0.57,0.68,0.53) if 'button_' in name else cq.Color(0.88,0.84,0.73)
        assembly.add(s,name=name,color=color)
    assembly.export(str(OUT/'step'/'Movie_Time_assembled.step'))
    # Export electronic envelopes separately: reference geometry, never printable parts.
    env=electronic_envelopes()
    ref=cq.Assembly(name='Electronics_reference_envelopes_NOT_FOR_PRINTING')
    for name,s in env.items(): ref.add(s,name=name)
    ref.export(str(OUT/'step'/'Electronics_reference_NOT_FOR_PRINTING.step'))
    (OUT/'validation'/'mesh_report.json').write_text(json.dumps(records,indent=2)+'\n')
    mechanical_checks(parts,env)
    from check_case_fit import check_case_fit
    check_case_fit()
    # BREP objects cached as STEP for rendering without regenerating.
    cache=ROOT/'build/render';cache.mkdir(parents=True,exist_ok=True)
    for name,s in env.items():
        cq.exporters.export(s,str(cache/f'{name}.step'))
    return parts,env,records

def mechanical_checks(parts,env):
    checks={}; collisions=[]
    physical={k:v for k,v in parts.items() if not k.startswith(('10','11'))}
    names=list(physical)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            vol=physical[a].intersect(physical[b]).Volume()
            if vol>0.02: collisions.append({'a':a,'b':b,'volume_mm3':round(vol,4)})
    for a,s in env.items():
        for b,t in physical.items():
            vol=s.intersect(t).Volume()
            if vol>0.02: collisions.append({'a':a,'b':b,'volume_mm3':round(vol,4)})
    checks['part_or_component_collisions']=collisions
    # Sweep the complete rigid case from fully out to fully inserted.
    sweep=box(SL+P['case_side_clearance'],-P['case_depth'],DECK+0.01,
              P['case_spine'],P['case_depth']+STOP-0.01,P['case_thickness'])
    sweep_collisions=[]
    for n,s in physical.items():
        vol=sweep.intersect(s).Volume()
        if vol>0.02:sweep_collisions.append({'part':n,'volume_mm3':round(vol,4)})
    checks['dvd_insertion_sweep_collisions']=sweep_collisions
    checks.update({'case_mm':[P['case_spine'],P['case_depth'],P['case_thickness']],
                   'slot_mm':[SR-SL,P['slot_top']-DECK],
                   'insertion_depth_mm':STOP,'spine_protrusion_mm':P['case_depth']-STOP,
                   'button_diametral_clearance_mm':P['button_hole_diameter']-P['button_diameter'],
                   'button_initial_gap_mm':round(env['play_switch_plunger'].BoundingBox().ymin-P['button_stem_tip_y'],3),
                   'button_hard_stop_travel_mm':P['button_guide_front_y']-3.4,'nfc_membrane_mm':P['nfc_membrane'],
                   'physical_print_verified':False,'electronic_scan_verified':False})
    # Verify cap motion through the expected stroke against shell and retainer.
    motion=[]
    for name,s in physical.items():
        if not name.startswith(('04','05','06')):continue
        for dy in (0.2,0.45,0.64):
            for other in ('02_lid','07_switch_carrier','08_switch_retainer'):
                vol=s.translate((0,dy,0)).intersect(physical[other]).Volume()
                if vol>0.02:motion.append({'button':name,'travel':dy,'part':other,'volume_mm3':vol})
    checks['button_motion_collisions']=motion
    (OUT/'validation'/'mechanical_report.json').write_text(json.dumps(checks,indent=2)+'\n')
    assert not collisions, collisions
    assert not sweep_collisions,sweep_collisions
    assert not motion,motion
    print('Mechanical interference and motion checks passed',flush=True)

if __name__=='__main__':
    build()
