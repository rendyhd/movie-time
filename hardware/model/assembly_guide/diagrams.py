"""Assembly maps from current model coordinates; no print geometry is edited."""
from pathlib import Path
import sys,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyBboxPatch
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/final_version/preview'
sys.path.insert(0,str(ROOT/'model'));import build_model as m
BG='#f7f4ec';INK='#293e42';COL={'A':'#675886','B':'#337d91','C':'#bd7636','D':'#426fab','E':'#50834e'}

def marker(ax,x,y,code,r=6):
    ax.add_patch(Circle((x,y),r,facecolor=COL[code],edgecolor='white',lw=1.2,zorder=10))
    ax.text(x,y,code,color='white',ha='center',va='center',fontsize=12,weight='bold',zorder=11)

def frame(ax,title):
    ax.set_aspect('equal');ax.set_facecolor(BG);ax.axis('off')
    ax.set_title(title,fontsize=15,color=INK,pad=12)

def maps():
    fig=plt.figure(figsize=(12,10),dpi=160);fig.patch.set_facecolor(BG)
    gs=fig.add_gridspec(2,2,height_ratios=[1,1.15],left=.035,right=.97,top=.93,bottom=.055,hspace=.38,wspace=.16)
    a=fig.add_subplot(gs[0,0]);b=fig.add_subplot(gs[0,1]);c=fig.add_subplot(gs[1,:])
    for ax,title in [(a,'A · Base, viewed from underneath'),(b,'B · Deck, viewed from above')]:
        frame(ax,title);ax.set_xlim(-12,262);ax.set_ylim(-19,160)
        ax.add_patch(FancyBboxPatch((0,0),250,144,boxstyle='round,pad=0,rounding_size=10',facecolor='#dfd8c7',edgecolor=INK,lw=1))
        ax.text(125,-13,'FRONT / CASE OPENING',ha='center',fontsize=11,color=INK)
        ax.text(125,151,'REAR / USB',ha='center',fontsize=10,color=INK)
    for x,y in m.P['lid_screws']:marker(a,250-x,y,'A')
    b.add_patch(Rectangle((8.3,2.65),191.4,102.75,facecolor='#ebeee5',edgecolor=INK,lw=1))
    for x,y in m.P['deck_screws']:marker(b,x,y,'B')
    b.text(226,62,'Wiring\nbay',ha='center',va='center',color=INK,fontsize=11)
    frame(c,'C, D, E · Inside of lid, front button area enlarged')
    c.set_xlim(-5,70);c.set_ylim(-9,31)
    c.add_patch(Rectangle((0,0),65,28,facecolor='#dfd8c7',edgecolor=INK,lw=1))
    # Looking at the underside with the front still toward you mirrors X.
    c.add_patch(Rectangle((250-246,6.8),43.2,4.6,facecolor='#c7d6df',edgecolor=INK,lw=1))
    c.add_patch(Rectangle((250-246,10.6),43,1.8,facecolor='#a9bdc7',edgecolor=INK,lw=1))
    for x,word in zip(m.BX,('PLAY','PAUSE','STOP')):
        c.add_patch(Circle((250-x,2.4),3.4,facecolor='#8eaa80',edgecolor=INK,lw=.7))
        c.text(250-x,-3,word,ha='center',fontsize=10,color=INK)
    c.add_patch(Rectangle((250-219.2,14),18.7,11,facecolor='#8eaa80',edgecolor=INK,lw=1))
    for x in (215.25,228.75):marker(c,250-x,8.8,'C',1.6)
    for x in (204.8,244):
        marker(c,250-x,14.7,'D',1.6)
        c.annotate('',xy=(250-x,11.5),xytext=(250-x,13),arrowprops={'arrowstyle':'->','color':COL['D'],'lw':1.4})
    for x in (205,214):marker(c,250-x,19.5,'E',1.6)
    c.text(57,19,'Spring\nblock',ha='center',va='center',fontsize=11,color=INK)
    c.text(32,-7,'FRONT EDGE TOWARD YOU · INSIDE VIEW REVERSES THE BUTTON ORDER',ha='center',fontsize=9,color=INK)
    fig.savefig(OUT/'screw_locations.png',facecolor=BG);plt.close(fig)

def electronics():
    fig,ax=plt.subplots(figsize=(12,8),dpi=160);fig.patch.set_facecolor(BG);frame(ax,'Electronics placement · base viewed from above')
    ax.set_xlim(-32,290);ax.set_ylim(-27,164)
    ax.add_patch(FancyBboxPatch((0,0),250,144,boxstyle='round,pad=0,rounding_size=10',facecolor='#dfd8c7',edgecolor=INK,lw=1.2))
    ax.add_patch(Rectangle((8,0),192,108,facecolor='#f0eee5',edgecolor='#adad9f',ls='--',lw=1))
    ax.text(116,44,'CASE DECK COVERS\nTHIS AREA',ha='center',va='center',color='#8a9289',fontsize=12)
    ax.add_patch(Rectangle((12.5,56.5),43,41,facecolor='#c47770',edgecolor=INK,lw=1))
    ax.text(34,77,'PN532',ha='center',va='center',color='white',weight='bold',fontsize=13)
    ax.add_patch(Rectangle((209.2,104),25.6,34.2,facecolor='#5f97ae',edgecolor=INK,lw=1))
    ax.text(222,120,'D1\nmini',ha='center',va='center',color='white',fontsize=12,weight='bold')
    ax.add_patch(Circle((224,48),10,facecolor='#525e60',edgecolor=INK,lw=1))
    ax.add_patch(Rectangle((204.5,4.5),11,1.8,facecolor='#b39a50',edgecolor=INK,lw=1))
    ax.plot([55.5,69,69,204,209],[88,88,118,118,118],ls='--',lw=2,color='#687e60')
    ax.plot([223,239,239,235],[14,14,100,110],ls='--',lw=2,color='#687e60')
    ax.text(132,128,'Wires through the rear tunnel',ha='center',fontsize=10,color=INK)
    for label,xy,xytext in [('Antenna side up',(34,93),(-29,112)),('USB faces rear',(222,138),(263,152)),
                            ('Buzzer grille',(224,48),(263,64)),('LED + lens',(210,5),(255,-13))]:
        ax.annotate(label,xy=xy,xytext=xytext,ha='center',va='center',fontsize=11,color=INK,
                    arrowprops={'arrowstyle':'->','color':INK,'lw':1})
    ax.text(118,-14,'FRONT / CASE SPINE FACES YOU',ha='center',color=INK,fontsize=12)
    ax.text(120,154,'REAR',ha='center',color=INK,fontsize=11)
    fig.savefig(OUT/'electronics_placement.png',facecolor=BG);plt.close(fig)

if __name__=='__main__':maps();electronics()
