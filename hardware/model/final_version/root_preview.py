"""Side-by-side detail rendered from the actual before/after STEP solids."""
from pathlib import Path
import sys
import vtk
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model'))
import render_model as r

def run():
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1)
    win.SetSize(1800,1000);win.SetMultiSamples(8)
    crop=cq.Workplane('XY').box(14,20,14,centered=False).translate((196,17,17)).val()
    paths=[ROOT/'output/final_version_plus20/step/12_single_leaf_PETG.step',
           ROOT/'output/final_version/step/12_single_leaf_PETG.step']
    for i,path in enumerate(paths):
        ren=vtk.vtkRenderer();ren.SetViewport(i/2,0,(i+1)/2,1)
        ren.SetBackground(.965,.955,.935);win.AddRenderer(ren)
        shape=r.read(path).intersect(crop)
        ren.AddActor(r.actor(shape,(.43,.60,.46)))
        r.text(ren,'Previous joint' if i==0 else 'Reinforced joint',50,915,36)
        r.text(ren,'1.2 mm fin at the block' if i==0 else '2.4 mm attachment, rounded shoulders',50,865,24)
        r.text(ren,'Abrupt step underneath' if i==0 else 'Fin extends into the block with a sloped underside',50,70,22)
        r.text(ren,'Actual CAD detail; mounting block and fin cropped for visibility.',50,35,18)
        cam=ren.GetActiveCamera();cam.SetFocalPoint(202,25.5,24)
        cam.SetPosition(230,73,2);cam.SetViewUp(0,0,1)
        cam.ParallelProjectionOn();cam.SetParallelScale(11.5)
        for pos,intensity in [((230,70,-35),.7),((170,80,80),.5)]:
            light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos)
            light.SetFocalPoint(202,26,24);light.SetIntensity(intensity);ren.AddLight(light)
        ren.ResetCameraClippingRange()
    win.Render()
    cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.SetInputBufferTypeToRGB()
    cap.ReadFrontBufferOff();cap.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(ROOT/'output/final_version/preview/reinforced_joint.png'))
    writer.SetInputConnection(cap.GetOutputPort());writer.Write();win.Finalize()

if __name__=='__main__':run()
