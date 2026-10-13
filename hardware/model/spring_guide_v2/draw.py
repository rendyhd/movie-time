"""Native vector top view using the actual spring profile coordinates."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyBboxPatch,Polygon,Circle
from build import OUT,profile,allowed_amplitude,THICKNESS

ink='#263a42';green='#438553';bg='#f7f5ef'
fig,ax=plt.subplots(figsize=(11,8),dpi=180)
fig.patch.set_facecolor(bg);ax.set_facecolor(bg)
ax.set_aspect('equal');ax.set_xlim(-4,272);ax.set_ylim(-49,158);ax.axis('off')
ax.text(0,150,'Contact in the middle',fontsize=24,weight='bold',color=ink)
ax.text(0,141,'Guided tail stays outside the case path',fontsize=12,color=ink)
ax.add_patch(FancyBboxPatch((5.6,0),219.4,112,boxstyle='round,pad=0,rounding_size=2',facecolor='#e7e0ce',edgecolor='#bdb39e'))
for x,y,w,h in [(5.6,0,2.4,110.4),(8,108,192,2.4),(211,27,2.4,80)]:
    ax.add_patch(Rectangle((x,y),w,h,facecolor='#9d927b'))
ax.add_patch(Rectangle((8.05,-27),170,135,facecolor='#cadce9',edgecolor='#4e7893',lw=1.2))
ax.add_patch(Rectangle((8.05,-27),170,5,facecolor='#4e7893'))
ax.text(90,30,'Blu-ray case',ha='center',fontsize=16,color=ink)
ax.text(90,-24.5,'SPINE',ha='center',va='center',fontsize=9,color='white')
# Separate carrier, with an open sliding channel and two short retaining roofs.
for x,y,w,h in [(200.5,14,18.7,10),(207.5,23.5,3.2,110.5),
                (202.8,104.5,7.9,29.5),(200.3,104.5,.9,29.5)]:
    ax.add_patch(Rectangle((x,y),w,h,facecolor='#c8b48b',edgecolor='#ab946a',lw=.5))
points,_=profile(allowed_amplitude(178.05,108))
outline=[(x-THICKNESS/2,y) for x,y in points]+[(x+THICKNESS/2,y) for x,y in reversed(points)]
ax.add_patch(Polygon(outline,closed=True,facecolor=green,edgecolor=green,lw=.8,zorder=5))
ax.add_patch(Rectangle((200.5,14),18.7,11,facecolor='#8caf8f',edgecolor=green,lw=.8,zorder=6))
for x in (205,214):ax.add_patch(Circle((x,19.5),1.15,facecolor=bg,edgecolor=green,zorder=7))
for y in (106,123):
    ax.add_patch(Rectangle((200.3,y),10.4,5,facecolor='#bfa87d',alpha=.65,edgecolor='#ab946a',lw=.7,zorder=6))
ax.annotate('Flat contact\npresses sideways',xy=(178.6,64.5),xytext=(235,62),
            fontsize=11,color=green,ha='center',va='center',
            arrowprops={'arrowstyle':'->','color':green,'lw':1.5})
ax.annotate('Tail slides\nin this guide',xy=(202,114),xytext=(147,122),
            fontsize=11,color=ink,ha='center',
            arrowprops={'arrowstyle':'->','color':ink,'lw':1.1})
ax.annotate('Same two\nmounting screws',xy=(211,19.5),xytext=(245,10),
            fontsize=10,color=ink,ha='center',
            arrowprops={'arrowstyle':'->','color':ink,'lw':1})
ax.annotate('',xy=(93,-2),xytext=(93,-17),arrowprops={'arrowstyle':'->','color':'#4e7893','lw':2})
ax.text(0,-39,'Top view • new spring + carrier reuse your existing test fixture',fontsize=11,color=ink)
ax.text(0,-47,'Geometry illustration. Revised mechanism still needs a physical test.',fontsize=10,color='#6c7779')
for ext in ('png','svg'):fig.savefig(OUT/'preview'/f'middle_contact.{ext}',bbox_inches='tight',facecolor=bg)
plt.close(fig)
