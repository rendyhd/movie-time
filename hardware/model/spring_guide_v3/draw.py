"""Dimensioned native diagram from the exact CAD profile and cross-sections."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
import numpy as np
from build import (OUT,profile,THICKNESS,REST_REAR,MAX_TRAVEL,SHOE_XZ,
                   LEFT_RAIL_XZ,RIGHT_RAIL_XZ,AXIS,TRACK_FRONT,TRACK_REAR,
                   SHOE_FRONT,SHOE_REAR,AMPLITUDE,Z,HEIGHT)

INK='#263c44';BG='#f8f5ed';GREEN='#478358';TAN='#c2ac85';BLUE='#c6dce7'
fig=plt.figure(figsize=(12,9),dpi=170,facecolor=BG)
gs=fig.add_gridspec(1,3,width_ratios=[1,1,1.48],left=.055,right=.97,bottom=.15,top=.84,wspace=.20)
fig.text(.055,.951,'The spring end moves with a sliding shoe',fontsize=23,weight='bold',color=INK)
fig.text(.055,.915,'Revision 3  •  Curved material stays beside the track throughout the movement',fontsize=13,color=INK)

def top(ax,amplitude,title,case_right=None):
    ax.set_facecolor(BG);ax.set_aspect('equal');ax.set_xlim(164,220);ax.set_ylim(7,145);ax.axis('off')
    ax.set_title(title,fontsize=15,color=INK,pad=14)
    if case_right is not None:
        ax.add_patch(Rectangle((161,7),case_right-161,101,facecolor=BLUE,edgecolor='#678a9e',lw=1))
        ax.text(168,83,'DVD CASE',rotation=90,fontsize=10,color='#496d83',ha='center')
    ax.add_patch(Rectangle((211,27),2.4,80,facecolor='#ded5c4'))
    for x,y,w,h in [(200.5,14,18.7,10),(207.5,23.5,3.2,TRACK_FRONT-23.5),(203,TRACK_FRONT,7.7,TRACK_REAR-TRACK_FRONT)]:
        ax.add_patch(Rectangle((x,y),w,h,facecolor=TAN,edgecolor='#a99166',lw=.7))
    ax.plot([206.85,206.85],[TRACK_FRONT,TRACK_REAR],ls=':',color='#f8f5ed',lw=2)
    p,t=profile(amplitude);n=np.column_stack((np.cos(t),-np.sin(t)))
    ax.add_patch(Polygon(np.vstack((p-.5*THICKNESS*n,(p+.5*THICKNESS*n)[::-1])),closed=True,facecolor=GREEN,edgecolor=GREEN,lw=.3,zorder=4))
    ax.add_patch(Rectangle((200.5,14),18.7,11,facecolor='#90b095',edgecolor=GREEN,lw=.7,zorder=5))
    for x in (205,214):ax.add_patch(Circle((x,19.5),1.15,facecolor=BG,edgecolor=GREEN,zorder=6))
    travel=p[-1,1]-REST_REAR
    ax.add_patch(Rectangle((204.4,SHOE_FRONT+travel),4.9,8,facecolor=GREEN,edgecolor='#285638',lw=.5,zorder=5))
    ax.add_patch(Rectangle((AXIS-.5,REST_REAR+travel),207.9-(AXIS-.5),4,facecolor=GREEN,edgecolor='#285638',lw=.5,zorder=5))
    ax.plot([164,219],[108,108],color='#b7a98c',lw=.7,ls='--')
    ax.plot([164,219],[141.6,141.6],color='#8c968e',lw=.7,ls=':')
    ax.text(164,142.7,'Inside rear wall',fontsize=8,color='#6c7974')
    ax.text(164,109.3,'Case rear stop',fontsize=8,color='#8a795c')
    return travel

a=fig.add_subplot(gs[0]);top(a,AMPLITUDE,'Empty')
a.annotate('Middle\ncontact',xy=(AXIS-AMPLITUDE-.5,58),xytext=(171,79),fontsize=10,color=GREEN,ha='center',arrowprops={'arrowstyle':'->','color':GREEN})
a.annotate('Shoe',xy=(206.8,REST_REAR+3),xytext=(185,118),fontsize=10,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
b=fig.add_subplot(gs[1]);travel=top(b,AXIS-198.05-.5-.05,'DVD inserted',198.05)
b.annotate('',xy=(216,REST_REAR+3+travel),xytext=(216,REST_REAR+3),arrowprops={'arrowstyle':'<->','color':INK,'lw':1.2})
b.text(217,REST_REAR+3+travel/2,f'{travel:.1f} mm',rotation=90,ha='left',va='center',fontsize=10,color=INK)
b.annotate('Whole end\nmoves back',xy=(206.8,REST_REAR+2+travel),xytext=(184,127),fontsize=10,color=GREEN,ha='center',arrowprops={'arrowstyle':'->','color':GREEN})

c=fig.add_subplot(gs[2]);c.set_aspect('equal');c.set_xlim(198,214);c.set_ylim(13,36);c.axis('off')
c.set_title('How the joint slides',fontsize=15,color=INK,pad=14)
c.add_patch(Rectangle((203,21),7.7,1.6,facecolor=TAN,edgecolor='#a99166',lw=.7))
for section in (LEFT_RAIL_XZ,RIGHT_RAIL_XZ):c.add_patch(Polygon(section,closed=True,facecolor=TAN,edgecolor='#a99166',lw=.7))
c.add_patch(Polygon(SHOE_XZ,closed=True,facecolor=GREEN,edgecolor='#285638',lw=.7,zorder=3))
c.add_patch(Rectangle((AXIS-.5,21),1,8,facecolor=GREEN,edgecolor='#285638',lw=.7,zorder=3))
c.add_patch(Rectangle((AXIS-.5,27.2),207.9-(AXIS-.5),1.8,facecolor=GREEN,edgecolor=GREEN,lw=.3,zorder=3))
c.annotate('Spring end\nstays outside',xy=(AXIS,24),xytext=(199.9,31.5),ha='center',fontsize=10,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
c.annotate('Arm passes\nabove rails',xy=(206,27.9),xytext=(210.5,31.5),ha='center',fontsize=10,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
c.annotate('Rigid shoe',xy=(206.8,24),xytext=(209.5,17.5),ha='center',fontsize=11,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
c.annotate('Fixed track',xy=(203.5,22),xytext=(201.1,17.5),ha='center',fontsize=11,color='#967746',arrowprops={'arrowstyle':'->','color':'#967746'})
c.text(206,14.6,'Cross-section looking along the track',fontsize=8.5,color=INK,ha='center')
fig.text(.055,.083,'Print the two PETG parts together. Reuse the PLA test fixture, mounting bridge and screws.',fontsize=12,color=INK)
fig.text(.055,.052,'Geometry illustration; the revised sliding action and spring force still need a physical test.',fontsize=10,color='#6b7979')
for ext in ('png','svg'):fig.savefig(OUT/'preview'/f'sliding_shoe.{ext}',facecolor=BG)
plt.close(fig)
