"""Native vector engineering diagrams for the print/assembly guide."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyBboxPatch

OUT=Path(__file__).resolve().parents[1]/'output/preview'
ink='#22313a';muted='#67736f';green='#64885b';bg='#f6f4ee'

fig,ax=plt.subplots(figsize=(12,8),dpi=180);fig.patch.set_facecolor(bg);ax.set_facecolor(bg)
ax.set_xlim(0,110);ax.set_ylim(-11,102);ax.axis('off')
ax.text(4,97,'Button wiring',fontsize=25,color=ink,weight='bold')
ax.text(4,91,'Each button closes its input to GND. Pins match movie-player.yaml.',fontsize=12,color=muted)
ax.add_patch(FancyBboxPatch((8,14),25,68,boxstyle='round,pad=0.5,rounding_size=3',facecolor='#dde5e3',edgecolor=ink,lw=1.5))
ax.text(20.5,77,'D1 MINI',ha='center',fontsize=15,color=ink,weight='bold')
ax.text(20.5,71,'ESP8266',ha='center',fontsize=11,color=muted)
rows=[(63,'D5 / GPIO14','PLAY','#56866c'),(46,'D6 / GPIO12','PAUSE','#5188a6'),(29,'D0 / GPIO16','STOP','#b78256')]
for y,pin,label,col in rows:
    ax.text(30.5,y+2,pin,ha='right',fontsize=10.5,color=ink)
    ax.plot([33,65],[y,y],color=col,lw=2.5)
    ax.plot([65,76],[y,y+5],color=ink,lw=2)
    ax.scatter([65,79],[y,y],s=22,color=ink,zorder=5)
    ax.plot([79,97],[y,y],color=ink,lw=2)
    ax.text(70,y+9,label,ha='center',fontsize=12,weight='bold',color=col)
ax.plot([97,97],[63,5],color=ink,lw=2)
ax.plot([8,4,4,97],[20,20,5,5],color=ink,lw=2)
ax.text(10,20,'GND',fontsize=10,color=ink)
for y,w in [(3.5,8),(1.5,5),(-.5,2)]:ax.plot([97-w/2,97+w/2],[y,y],color=ink,lw=2)
ax.text(99,13,'GND',fontsize=10,color=ink,rotation=90)
# External 3V3 pull-up is a named net; never to 5V.
ax.scatter([51],[29],s=24,color=ink,zorder=8)
ax.plot([51,51],[29,25],color=ink,lw=1.8)
ax.add_patch(Rectangle((49.6,16),2.8,9,facecolor=bg,edgecolor=ink,lw=1.8))
ax.plot([51,51],[16,12],color=ink,lw=1.8)
ax.scatter([51],[12],s=20,color=ink)
ax.text(55,20,'10 kΩ',fontsize=12,color=ink,va='center')
ax.text(51,8.2,'D1 Mini 3V3',fontsize=10,color=ink,ha='center')
ax.text(4,-6,'D5 / D6: internal pull-ups.   D0: external pull-up + polling.',fontsize=12,color=ink)
fig.savefig(OUT/'button_wiring.png',facecolor=bg,bbox_inches='tight');fig.savefig(OUT/'button_wiring.svg',facecolor=bg,bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(11,8),dpi=180);fig.patch.set_facecolor(bg);ax.set_facecolor(bg)
ax.set_xlim(-16,212);ax.set_ylim(-47,159);ax.set_aspect('equal');ax.axis('off')
ax.text(0,154,'NFC sticker position',fontsize=23,color=ink,weight='bold')
ax.text(0,144,'View through the case from above; sticker is on the UNDERSIDE.',fontsize=11,color=muted)
ax.add_patch(FancyBboxPatch((0,0),190,135,boxstyle='round,pad=0,rounding_size=2',facecolor='#e5e8e5',edgecolor=ink,lw=1.7))
ax.plot([170,170],[8,135],color='#397cb2',linestyle='--',lw=1.5)
ax.text(174,62,'Blu-ray right edge (170 mm)',rotation=90,ha='left',va='center',fontsize=9,color='#397cb2')
ax.add_patch(Rectangle((0,0),190,7,facecolor='#22313a'))
ax.text(95,3.5,'MOVIE SPINE — FACES YOU',ha='center',va='center',color='white',fontsize=11)
ax.text(95,130,'Opening edge — enters first',ha='center',fontsize=11,color=muted)
ax.add_patch(Circle((95,67.5),60,facecolor='none',edgecolor='#a9b0ac',linestyle='--',lw=1))
ax.text(110,64,'Disc area',ha='center',fontsize=11,color='#909b95')
ax.add_patch(Circle((26,104),12.5,facecolor='#adc79c',edgecolor=green,lw=2))
ax.plot([22,30],[104,104],color=green);ax.plot([26,26],[100,108],color=green)
ax.annotate('',xy=(26,119),xytext=(0,119),arrowprops={'arrowstyle':'<->','color':green})
ax.text(13,121,'26 mm',ha='center',fontsize=10,color=green)
ax.annotate('',xy=(-7,104),xytext=(-7,0),arrowprops={'arrowstyle':'<->','color':green})
ax.text(-10,52,'104 mm from spine',ha='center',va='center',rotation=90,fontsize=10,color=green)
ax.plot([-8,26],[104,104],color=green,lw=.8,linestyle=':')
ax.text(45,104,'Sticker center',fontsize=12,color=green,va='center')
ax.text(0,-14,'DVD 190 mm / Blu-ray 170 mm: align LEFT in the slot, then push to the stop.',fontsize=10.5,color=ink)
ax.text(0,-25,'Hide under the back-cover paper / sleeve. Bench-test each case format first.',fontsize=10.5,color=ink)
ax.text(0,-36,'For 135 mm-deep cases. Illustrative diagram; use the written measurements.',fontsize=10,color=muted)
fig.savefig(OUT/'tag_placement.png',facecolor=bg,bbox_inches='tight');fig.savefig(OUT/'tag_placement.svg',facecolor=bg,bbox_inches='tight');plt.close(fig)
