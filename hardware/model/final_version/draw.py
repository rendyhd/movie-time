"""Engineering diagram using actual CAD and solved rod coordinates."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon,Circle,FancyBboxPatch
import numpy as np
from leaf_motion import OUT,natural_profile,TIP_RADIUS,LENGTH,Y0,thickness_at

INK='#283e43';BG='#f7f4ec';GREEN='#49825a';TAN='#d1c5ae'
fig,axes=plt.subplots(1,3,figsize=(12,8),dpi=170)
fig.patch.set_facecolor(BG)
fig.subplots_adjust(left=.045,right=.975,bottom=.16,top=.84,wspace=.15)
fig.text(.045,.953,'One leaf. One fixed end. Room to flex.',fontsize=24,weight='bold',color=INK)
fig.text(.045,.912,'Final design  •  Top view of the right side, with the roof removed',fontsize=13,color=INK)
poses=np.load(OUT/'validation/motion_poses.npz')

for ax,title,right in zip(axes,['Empty','Blu-ray inserted','DVD inserted'],[None,178.05,198.05]):
    ax.set_facecolor(BG);ax.set_aspect('equal');ax.set_xlim(159,226);ax.set_ylim(9,115);ax.axis('off')
    ax.set_title(title,fontsize=16,color=INK,pad=15)
    ax.add_patch(Rectangle((211,27),2.4,62,facecolor=TAN,edgecolor='#b5a68e',lw=.8))
    ax.add_patch(Rectangle((159,108),41,2.4,facecolor=TAN,edgecolor='#b5a68e',lw=.8))
    if right is not None:
        ax.add_patch(Rectangle((159,9),right-159,99,facecolor='#d3e0e8' if right<190 else '#d9dad8',edgecolor='#8396a0',lw=.8))
        ax.text(164,92,'CASE',rotation=90,color='#657d86',fontsize=11,ha='center')
        p=poses[f'{right}_108']
        tangent=np.gradient(p,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None]
        n=np.column_stack((tangent[:,1],-tangent[:,0]))
    else:
        p,t=natural_profile(100);n=np.column_stack((np.cos(t),-np.sin(t)))
    distance=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    half=thickness_at(distance)[:,None]/2
    poly=np.vstack((p-half*n,(p+half*n)[::-1]))
    ax.add_patch(Polygon(poly,closed=True,facecolor=GREEN,edgecolor=GREEN,lw=.3,zorder=4))
    ax.add_patch(Circle(p[-1],TIP_RADIUS,facecolor=GREEN,edgecolor=GREEN,zorder=4))
    ax.add_patch(FancyBboxPatch((200.5,14),18.7,11,boxstyle='round,pad=0,rounding_size=1.2',facecolor=GREEN,edgecolor='#315c3c',lw=.6,zorder=4))
    for x in (205,214):ax.add_patch(Circle((x,19.5),1.15,facecolor=BG,edgecolor='#315c3c',lw=.6,zorder=5))
    if right is None:
        ax.annotate('Free end',xy=p[-1],xytext=(174,88),ha='center',fontsize=11,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
        ax.annotate('Same two\nscrews',xy=(210,19.5),xytext=(179,28),ha='center',fontsize=10,color=INK,arrowprops={'arrowstyle':'->','color':INK})
        bound=Y0+LENGTH+TIP_RADIUS
        ax.plot([199,224],[bound,bound],ls=':',color='#929988',lw=.8)
        ax.annotate('',xy=(221,108),xytext=(221,bound),arrowprops={'arrowstyle':'<->','color':INK})
        ax.text(218,95,f'{108-bound:.1f} mm\nminimum\nrear margin',fontsize=9,ha='right',va='center',color=INK)
        ax.text(159,112,'Case rear stop',fontsize=9,color='#8c795a')
    else:
        idx=np.argmin(p[:,0])
        ax.annotate('Contact near\nthe middle',xy=p[idx],xytext=(181,40),ha='center',fontsize=10,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
        ax.annotate('End moves\nfreely',xy=p[-1],xytext=(203,94),ha='center',fontsize=10,color=GREEN,arrowprops={'arrowstyle':'->','color':GREEN})
fig.text(.045,.089,'Single PETG part  •  1.2 mm leaf × 10 mm high  •  Existing mounting screws and test fixture',fontsize=12,color=INK)
fig.text(.045,.052,'Loaded shapes are frictionless bending calculations. Printed feel, return and NFC reading require a physical check.',fontsize=10,color='#6b7877')
for ext in ('png','svg'):fig.savefig(OUT/'preview'/f'single_leaf_motion.{ext}',facecolor=BG)
plt.close(fig)
