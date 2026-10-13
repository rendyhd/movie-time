"""Dimensioned section from the actual solids, through the play-button axis."""
from pathlib import Path
import sys
import numpy as np
import cadquery as cq
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/final_version'
sys.path.insert(0,str(ROOT/'model'));import build_model as m

def section(shape):
    vertices,triangles=shape.tessellate(.025,.1)
    mesh=trimesh.Trimesh(np.array([v.toTuple() for v in vertices]),triangles,process=False)
    cut=mesh.section(plane_origin=(m.BX[0],0,0),plane_normal=(1,0,0))
    loops=[]
    for entity in cut.entities:
        line=entity.discrete(cut.vertices)
        assert np.linalg.norm(line[0]-line[-1])<1e-6,'open section contour'
        p=line[:,1:3]
        area=.5*np.sum(p[:-1,0]*p[1:,1]-p[1:,0]*p[:-1,1])
        if abs(area)>1e-7:loops.append(p)
    return loops

def add(ax,shape,color,z=2):
    loops=section(shape);vertices=[];codes=[]
    for i,p in enumerate(loops):
        depth=sum(MPath(other).contains_point(p[0]) for j,other in enumerate(loops) if i!=j)
        area=.5*np.sum(p[:-1,0]*p[1:,1]-p[1:,0]*p[:-1,1])
        if area*(1 if depth%2==0 else -1)<0:p=p[::-1]
        vertices.extend(p)
        codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(p)-2)+[MPath.CLOSEPOLY])
    ax.add_patch(PathPatch(MPath(vertices,codes),facecolor=color,edgecolor='#364443',lw=.8,zorder=z))

def run():
    fig,ax=plt.subplots(figsize=(12,8),dpi=160);bg='#f7f4ec';ink='#293e42'
    fig.patch.set_facecolor(bg);ax.set_facecolor(bg)
    fig.subplots_adjust(left=.05,right=.98,bottom=.16,top=.80)
    fig.text(.05,.94,'Switch seats moved 0.8 mm forward',fontsize=25,weight='bold',color=ink)
    fig.text(.05,.887,'CAD section at rest  ·  Actuator contact position calibrated from your installed measurements',fontsize=12,color=ink)
    for name,col in [('02_cute_lid_single_leaf','#d9d1bf'),('07_switch_carrier','#c7d6df'),
                      ('08_switch_retainer','#a9bdc7'),('04_button_play','#88a580')]:
        add(ax,cq.importers.importStep(str(OUT/'step'/f'{name}.step')).val(),col)
    env=m.electronic_envelopes()
    add(ax,env['play_switch_body'],'#525e60',3)
    add(ax,env['play_switch_plunger'],'#deb468',3)
    ax.set_aspect('equal');ax.set_xlim(-5.7,17);ax.set_ylim(17,37);ax.axis('off')
    labels=[('Existing cap',(-.7,26),(-5,25)),('Pin: Ø3 mm\n2.8 mm long',(5.0,26),(-5.4,18.5)),
            ('Holder +\npin guide',(5.2,29.2),(-4.8,34.8)),
            ('Actual switch\n6 × 6 × 4 mm',(9.4,26),(12.5,19.8)),
            ('Rear retaining\nplate',(12.3,30.1),(13.8,33.5))]
    for label,xy,xytext in labels:
        ax.annotate(label,xy=xy,xytext=xytext,color=ink,fontsize=11,
                    arrowprops={'arrowstyle':'->','color':ink,'lw':1.1},va='center',zorder=5)
    fig.text(.05,.10,'Predicted recess after moving the seats: 2.2 mm unpressed / 2.7 mm pressed. Existing pin: 2.8 mm.',fontsize=11,color=ink)
    fig.text(.05,.055,'Reuse the front panel and screws. Check the click and return with your actual switches before final assembly.',fontsize=11,color=ink)
    fig.savefig(OUT/'preview/button_fit_section.png',facecolor=bg);plt.close(fig)

if __name__=='__main__':run()
