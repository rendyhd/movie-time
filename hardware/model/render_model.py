"""Render the actual STEP geometry, not an AI approximation."""
from pathlib import Path
import json
import cadquery as cq
import vtk
from vtk.util.numpy_support import numpy_to_vtk
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
P=json.loads((ROOT/'model/parameters.json').read_text())
CREAM=(0.86,0.82,0.72); GREEN=(0.48,0.62,0.46); DARK=(0.10,0.15,0.20)

def read(p): return cq.importers.importStep(str(p)).val()

def actor(shape,color,opacity=1):
    vertices,faces=shape.tessellate(0.07,0.14)
    points=vtk.vtkPoints()
    points.SetData(numpy_to_vtk(np.array([[v.x,v.y,v.z] for v in vertices]),deep=True))
    cells=vtk.vtkCellArray()
    for face in faces:
        cells.InsertNextCell(3)
        for ix in face:cells.InsertCellPoint(ix)
    data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(data);normals.SetFeatureAngle(45)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper)
    a.GetProperty().SetColor(*color);a.GetProperty().SetOpacity(opacity)
    a.GetProperty().SetAmbient(0.3);a.GetProperty().SetDiffuse(0.7);a.GetProperty().SetSpecular(0.12)
    a.GetProperty().SetSpecularPower(30)
    return a

def text(renderer,string,x,y,size=24,color=DARK):
    a=vtk.vtkTextActor();a.SetInput(string);a.SetPosition(x,y)
    a.GetTextProperty().SetFontFamilyToArial();a.GetTextProperty().SetFontSize(size)
    a.GetTextProperty().SetColor(*color)
    renderer.AddViewProp(a)

def wire(renderer,points,color,radius=0.6):
    pts=vtk.vtkPoints()
    for p in points:pts.InsertNextPoint(*p)
    spline=vtk.vtkParametricSpline();spline.SetPoints(pts)
    src=vtk.vtkParametricFunctionSource();src.SetParametricFunction(spline);src.SetUResolution(100)
    tube=vtk.vtkTubeFilter();tube.SetInputConnection(src.GetOutputPort());tube.SetRadius(radius);tube.SetNumberOfSides(8)
    mp=vtk.vtkPolyDataMapper();mp.SetInputConnection(tube.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mp);a.GetProperty().SetColor(*color);renderer.AddActor(a)

def scene(mode):
    ren=vtk.vtkRenderer();ren.SetBackground(0.95,0.945,0.92)
    # Ambient occlusion makes the real engraved details readable in a CAD render.
    steps=vtk.vtkRenderStepsPass()
    ao=vtk.vtkSSAOPass();ao.SetDelegatePass(steps);ao.SetRadius(2.0);ao.SetBias(0.04)
    ao.SetKernelSize(96);ao.BlurOn();ren.SetPass(ao)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1800,1150);win.AddRenderer(ren)
    win.SetMultiSamples(8)
    printed={p.stem:read(p) for p in (OUT/'step').glob('0*.step')}
    if mode in ('assembled','top','bluray'):
        for n,s in printed.items():
            ren.AddActor(actor(s,GREEN if 'button_' in n else CREAM))
        # Standard case in the validated seated position, shown only as context.
        case_width,case_thickness=(170,14) if mode=='bluray' else (190,14)
        case=cq.Workplane('XY').box(case_width,135,case_thickness,centered=False).edges('|Z').fillet(1).translate((9,-27,18.05)).val()
        if mode!='top':ren.AddActor(actor(case,(0.08,0.30,0.66) if mode=='bluray' else (0.07,0.09,0.11)))
        cover=cq.Workplane('XY').box(case_width-4,131,0.12,centered=False).translate((11,-25,18.06+case_thickness)).val()
        if mode!='top':ren.AddActor(actor(cover,(0.22,0.33,0.43)))
        text(ren,'MOVIE TIME',75,1045,38)
        text(ren,'Blu-ray case 170 x 135 x 14 mm  /  Actual CAD model' if mode=='bluray'
             else 'Movie buddy edition  /  Actual CAD model',75,1004,22)
        text(ren,'250 x 144 x 38 mm body',75,85,24)
        text(ren,'0.6 mm recessed artwork  |  Prints with the lid in one color' if mode=='top'
             else ('Keep case left-aligned  |  108 mm inside  |  27 mm spine exposed' if mode=='bluray'
                   else 'Play / Pause / Stop  |  Spine visible  |  LED below controls'),75,49,20)
        cam_pos=(365,-430,305);focal=(126,50,18);scale=160
        if mode=='top':
            cam_pos=(125,72,450);focal=(125,72,0);scale=107
    elif mode=='exploded':
        for n,s in printed.items():
            off=(0,0,0)
            if n=='02_lid':off=(0,0,95)
            if n=='03_case_deck':off=(0,0,45)
            if 'button_' in n:off=(0,-28,95)
            if n=='07_switch_carrier':off=(0,0,75)
            if n=='08_switch_retainer':off=(0,20,75)
            ren.AddActor(actor(s.translate(off),GREEN if 'button_' in n else CREAM))
        for p in (ROOT/'build/render').glob('*.step'):
            if 'switch' not in p.stem:
                col=(0.62,0.19,0.16) if 'PN532' in p.stem else ((0.1,0.43,0.57) if 'D1' in p.stem else DARK)
                ren.AddActor(actor(read(p),col))
        text(ren,'ASSEMBLY',75,1045,38)
        text(ren,'Removable lid / smooth case deck / electronics base',75,1004,22)
        text(ren,'Separate keyed button caps and switch retaining plate',75,55,22)
        cam_pos=(330,-440,335);focal=(125,62,63);scale=174
    else:
        ren.AddActor(actor(printed['01_base'],CREAM))
        for p in (ROOT/'build/render').glob('*.step'):
            if 'switch' in p.stem:continue
            col=(0.67,0.17,0.14) if 'PN532' in p.stem else ((0.10,0.43,0.57) if 'D1' in p.stem else DARK)
            ren.AddActor(actor(read(p),col))
        colors=[(0.83,0.20,0.17),(0.18,0.21,0.23),(0.24,0.48,0.70),(0.83,0.73,0.37)]
        for i,c in enumerate(colors):
            wire(ren,[(55,75+i,10),(62,80+i,6),(67+i,92,4.2),(67+i,116+i,4.2),
                      (130,116+i,4.2),(199,116+i,4.2),(209,114+i,6.6)],c,0.5)
        for i,c in enumerate(colors):
            wire(ren,[(207+i,22,15),(205+i*0.7,34,5),(205+i*0.7,83,5),
                      (210,94+i,5),(211+i,108,7)],c,0.5)
        text(ren,'INSIDE THE BASE',75,1045,38)
        text(ren,'PN532 left  /  D1 Mini rear right  /  buzzer and LED in right bay',75,1004,22)
        text(ren,'Component envelopes and suggested wire routes; case deck removed',75,55,21)
        cam_pos=(270,-160,480);focal=(125,67,8);scale=147
    camera=ren.GetActiveCamera();camera.SetPosition(*cam_pos);camera.SetFocalPoint(*focal)
    camera.SetViewUp(*( (0,1,0) if mode=='top' else (0,0,1) ));camera.ParallelProjectionOn();camera.SetParallelScale(scale)
    for pos,intensity in [((0,-250,500),0.8),((400,150,250),0.5)]:
        light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos);light.SetFocalPoint(125,70,10);light.SetIntensity(intensity);ren.AddLight(light)
    ren.ResetCameraClippingRange();win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'preview'/f'{mode}.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write()
    win.Finalize()

if __name__=='__main__':
    import sys
    for mode in (sys.argv[1:] or ('assembled','top','exploded','electronics')):
        print('Rendering',mode,flush=True);scene(mode)
