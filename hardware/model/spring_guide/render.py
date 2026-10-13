"""Actual CAD cutaway views of the two seated case sizes and deflected guide."""
from pathlib import Path
import sys
import vtk
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model'))
from render_model import actor, text, CREAM, GREEN, DARK
from build import OUT, beam_points, required_deflection, Z, HEIGHT


def beam_actor(points,thickness=2.0):
    # Triangulate the exact extrusion outline directly. This avoids an OCC
    # tessellation stall on the long, shallow concave faces of the bent leaf.
    outline=[(x-thickness/2,y) for x,y in points]+[(x+thickness/2,y) for x,y in reversed(points)]
    count=len(outline)
    vertices=vtk.vtkPoints()
    for z in (Z,Z+HEIGHT):
        for x,y in outline:vertices.InsertNextPoint(x,y,z)
    faces=vtk.vtkCellArray()
    for ids in (list(reversed(range(count))),list(range(count,2*count))):
        faces.InsertNextCell(count)
        for i in ids:faces.InsertCellPoint(i)
    for i in range(count):
        j=(i+1)%count
        faces.InsertNextCell(4)
        for k in (i,j,j+count,i+count):faces.InsertCellPoint(k)
    data=vtk.vtkPolyData();data.SetPoints(vertices);data.SetPolys(faces)
    triangles=vtk.vtkTriangleFilter();triangles.SetInputData(data)
    normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(triangles.GetOutputPort());normals.SetFeatureAngle(45)
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
    result=vtk.vtkActor();result.SetMapper(mapper);result.GetProperty().SetColor(0.32,0.65,0.40)
    return result


def run():
    window=vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1);window.SetSize(1800,1050);window.SetMultiSamples(8)
    fixed={p.stem:cq.importers.importStep(str(p)).val() for p in (ROOT/'output/step').glob('0*.step') if not p.stem.startswith('02')}
    lid=cq.importers.importStep(str(OUT/'step/02_lid_with_spring.step')).val()
    # Cut the roof away in the render so the internal mechanism can be seen.
    lid=lid.intersect(cq.Workplane('XY').box(270,170,30.5,centered=False).translate((-5,-10,0)).val())
    # Remove the lip above the spring pocket as part of this explanatory cutaway.
    lid=lid.cut(cq.Workplane('XY').box(4.5,94,2,centered=False).translate((199.5,13.5,29)).val())
    spring=cq.importers.importStep(str(OUT/'step/12_spring_standard_PETG.step')).val()
    mount=spring.intersect(cq.Workplane('XY').box(40,11.1,10,centered=False).translate((195,13.9,20)).val())
    for index,(label,width,thickness) in enumerate([('BLU-RAY',170,14),('DVD',190,14)]):
        print('Rendering',label,flush=True)
        ren=vtk.vtkRenderer();ren.SetViewport(index/2,0,(index+1)/2,1)
        ren.SetBackground(0.95,0.945,0.92);window.AddRenderer(ren)
        for name,shape in fixed.items():ren.AddActor(actor(shape,GREEN if 'button_' in name else CREAM))
        ren.AddActor(actor(lid,CREAM))
        case=cq.Workplane('XY').box(width,135,thickness,centered=False).edges('|Z').fillet(1).translate((8.05,-27,18.05)).val()
        ren.AddActor(actor(case,(0.12,0.33,0.57) if label=='BLU-RAY' else (0.22,0.26,0.30)))
        displacement,where=required_deflection(8.05+width,108)
        points=beam_points(displacement,where)
        ren.AddActor(beam_actor(points))
        ren.AddActor(actor(mount,(0.32,0.65,0.40)))
        tip=cq.Workplane('XY',origin=(*points[-1],Z)).circle(2).extrude(HEIGHT).val()
        ren.AddActor(actor(tip,(0.32,0.65,0.40)))
        text(ren,label,55,958,36)
        text(ren,'Same left edge / same NFC position',55,910,23)
        text(ren,'Spring bends outward to suit the case',55,170,23)
        text(ren,'Roof removed to show the mechanism',55,125,21)
        text(ren,'Deflection illustration; print test required',55,88,20)
        camera=ren.GetActiveCamera();camera.SetPosition(125,58,500);camera.SetFocalPoint(125,58,0)
        camera.SetViewUp(0,1,0);camera.ParallelProjectionOn();camera.SetParallelScale(163)
        for pos,intensity in [((0,-150,500),0.8),((400,250,350),0.4)]:
            light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos)
            light.SetFocalPoint(125,60,15);light.SetIntensity(intensity);ren.AddLight(light)
        ren.ResetCameraClippingRange()
    print('Capturing image',flush=True)
    window.Render()
    grab=vtk.vtkWindowToImageFilter();grab.SetInput(window);grab.SetInputBufferTypeToRGB();grab.ReadFrontBufferOff();grab.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'preview/spring_mechanism.png'))
    writer.SetInputConnection(grab.GetOutputPort());writer.Write();window.Finalize()


if __name__=='__main__':run()
