"""Complete, labelled connection diagram; symbols are not physical pin layouts."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/preview'
OUT.mkdir(parents=True, exist_ok=True)
BG = '#faf9f5'
INK = '#23373b'
MUTED = '#637478'
RED = '#c94b50'
GND = '#34434a'
PURPLE = '#8b58a1'
COLORS = {'D1': '#268899', 'D2': '#a77d26', 'D8': '#9a6296',
          'D7': '#a66c37', 'D5': '#36836a', 'D6': '#417fb6', 'D0': '#bd7728'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(15.4, 18.1), dpi=170, facecolor=BG)
ax = fig.add_axes((0, 0, 1, 1))
ax.set(xlim=(0, 1540), ylim=(1810, 0))
ax.axis('off')

def text(x, y, value, size=16, color=INK, weight='normal', ha='left', **kwargs):
    return ax.text(x, y, value, fontsize=size, color=color, weight=weight,
                   ha=ha, va='center', zorder=8, **kwargs)

def panel(x, y, w, h, fill='white', edge='#d5dddd', radius=18):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f'round,pad=0,rounding_size={radius}',
        facecolor=fill, edgecolor=edge, lw=1.4, zorder=1))

def wire(points, color, width=2.7, z=3, halo=True):
    xs, ys = zip(*points)
    line, = ax.plot(xs, ys, color=color, lw=width, solid_capstyle='round', zorder=z)
    if halo:
        line.set_path_effects([pe.Stroke(linewidth=width+4, foreground=BG), pe.Normal()])

def dot(x, y, color=GND, radius=5.6):
    ax.add_patch(Circle((x, y), radius, facecolor=color, edgecolor=color, zorder=7))

def terminal(x, y, color=INK):
    ax.add_patch(Circle((x, y), 5.4, facecolor='white', edgecolor=color, lw=1.8, zorder=6))

def controller_pin(y, label, color):
    text(421, y, label, size=17, weight='bold', ha='right', color=color)
    terminal(450, y, color)

def device_pin(y, label, color):
    terminal(1090, y, color)
    text(1112, y, label, size=17, weight='bold', color=color)

text(70, 63, 'Movie Time · complete wiring', 31, weight='bold')
text(70, 108, 'Original D1 mini + red PN532 + colour LED + passive buzzer + three buttons', 16.5, MUTED)
text(70, 143, 'Use the printed pin names. Positions below are rearranged for clarity; this is not a board pinout.', 14.5, MUTED)

# A single logical controller symbol, with all ten used pins shown once.
panel(70, 180, 380, 1350, '#e8f0ec', '#64867b')
text(260, 220, 'D1 MINI', 26, weight='bold', ha='center')
text(260, 252, 'ESP8266 · your micro-USB board', 14, MUTED, ha='center')
panel(114, 550, 292, 80, '#ffffff', '#b9c9c3', 9)
text(260, 576, 'MICRO-USB', 18, weight='bold', ha='center')
text(260, 605, 'Power with a 5V USB cable', 13.5, MUTED, ha='center')
text(260, 833, 'Only the labelled pins', 14.5, MUTED, ha='center')
text(260, 860, 'need wires for this build.', 14.5, MUTED, ha='center')
text(260, 1070, 'Button wiring matches', 14, MUTED, ha='center')
text(260, 1097, 'movie-player.yaml', 14, MUTED, ha='center')

controller_pin(290, '5V', RED)
controller_pin(350, 'G / GND', GND)
controller_pin(410, 'D1  /  GPIO5', COLORS['D1'])
controller_pin(470, 'D2  /  GPIO4', COLORS['D2'])
controller_pin(730, 'D8  /  GPIO15', COLORS['D8'])
controller_pin(945, 'D7  /  GPIO13', COLORS['D7'])
controller_pin(1180, 'D5  /  GPIO14', COLORS['D5'])
controller_pin(1280, 'D6  /  GPIO12', COLORS['D6'])
controller_pin(1380, 'D0  /  GPIO16', COLORS['D0'])
controller_pin(1460, '3V3', PURPLE)

# Module symbols deliberately use printed terminal names, not assumed clone positions.
panel(1090, 180, 380, 335, '#f9e9e7', '#d6a3a1')
text(1120, 220, 'PN532', 23, weight='bold')
text(1120, 253, 'Red NFC reader board', 14, MUTED)
for y, label, color in [(290, 'VCC', RED), (350, 'GND', GND),
                         (410, 'SCL', COLORS['D1']), (470, 'SDA', COLORS['D2'])]:
    device_pin(y, label, color)
text(1302, 361, 'I²C mode', 15, weight='bold')
text(1302, 391, '1 = ON', 15)
text(1302, 419, '2 = OFF', 15)

panel(1090, 550, 380, 290, '#f2edf8', '#bcadd0')
text(1120, 581, 'WS2812 · colour LED', 21, weight='bold')
for y, label, color in [(630, '5V / VDD', RED), (680, 'GND / VSS', GND),
                         (730, 'DIN / DI', COLORS['D8'])]:
    device_pin(y, label, color)
text(1120, 792, 'DOUT / DO stays unconnected.', 13.5, MUTED)

panel(1090, 885, 380, 165, '#f4edde', '#cdbc99')
text(1120, 918, 'PASSIVE BUZZER', 20, weight='bold')
device_pin(965, '+', COLORS['D7'])
device_pin(1010, '−', GND)
text(1180, 989, 'Original tagreader buzzer', 13, MUTED)

panel(1090, 1100, 380, 430, '#eef2ec', '#b6c7ad')
text(1120, 1135, 'PLAY', 19, weight='bold', color=COLORS['D5'])
text(1120, 1235, 'PAUSE', 19, weight='bold', color=COLORS['D6'])
text(1120, 1335, 'STOP', 19, weight='bold', color=COLORS['D0'])
text(1120, 1450, 'Two contacts per button.', 14, MUTED)
text(1120, 1478, 'Check the four legs below.', 14, MUTED)

# Power trunks first; white halos on later crossing wires mean no connection.
wire([(840, 290), (840, 630)], RED, z=2)
wire([(990, 350), (990, 1570), (1440, 1570), (1440, 1180)], GND, z=2)
wire([(450, 290), (1090, 290)], RED)
wire([(450, 350), (1090, 350)], GND)
wire([(840, 630), (1090, 630)], RED)
wire([(990, 680), (1090, 680)], GND)
wire([(990, 1010), (1090, 1010)], GND)
wire([(450, 410), (1090, 410)], COLORS['D1'])
wire([(450, 470), (1090, 470)], COLORS['D2'])
wire([(450, 730), (1090, 730)], COLORS['D8'])
wire([(450, 945), (1027, 945), (1027, 965), (1090, 965)], COLORS['D7'])
for x, y, col in [(840,290,RED), (840,630,RED), (990,350,GND),
                   (990,680,GND), (990,1010,GND)]:
    dot(x,y,col)
text(609, 271, 'Shared 5V supply', 13, RED, ha='center')
text(609, 330, 'Shared ground', 13, GND, ha='center')
text(626, 391, 'Clock', 12.5, COLORS['D1'], ha='center')
text(626, 451, 'Data', 12.5, COLORS['D2'], ha='center')
text(680, 710, 'LED data input', 13, COLORS['D8'], ha='center')
text(680, 925, 'Buzzer signal', 13, COLORS['D7'], ha='center')

for y, pin in [(1180,'D5'), (1280,'D6'), (1380,'D0')]:
    wire([(450,y),(1190,y)], COLORS[pin])
    wire([(1190,y),(1260,y-27)], INK, halo=False)
    terminal(1190,y)
    terminal(1270,y)
    wire([(1270,y),(1440,y)], GND, halo=False)
    dot(1440,y,GND)

# Stop's pull-up is a branch from the D0 net, never a series switch resistor.
wire([(450,1460),(770,1460),(770,1442)], PURPLE)
ax.add_patch(Rectangle((757,1398),26,44,facecolor='#f2e8d2',edgecolor=INK,lw=1.8,zorder=5))
wire([(770,1398),(770,1380)], COLORS['D0'])
dot(770,1380,COLORS['D0'])
text(733,1420,'10 kΩ',17,weight='bold',ha='right')
text(585,1440,'Resistor to 3V3',13,PURPLE,ha='center')
text(705,1510,'Put the resistor near the D1 mini.',13.5,MUTED,ha='center')
text(1190,1598,'All black wires join G / GND.',14,GND,ha='center')

# Practical notes remain part of the saved image.
panel(70, 1618, 1400, 135, '#f0f2ef', '#d5dddd', 12)
text(94, 1648, 'BEFORE SOLDERING', 15, weight='bold')
text(94, 1678, 'Unplug USB. On each 4-leg switch, choose two legs that are open when released and connected when pressed.', 13.5)
text(94, 1707, 'The two unused legs can stay unwired. D5/D6 use software pull-ups; D0 needs the external 10 kΩ shown above.', 13.5)
text(94, 1735, 'Dots = wires joined. Crossings without dots = separate wires. Colours are suggestions; follow the labels.', 13.5)
text(70, 1780, 'Checked against adonno/tagreader + movie-player.yaml · Original red PN532 only · Diagram, not physical pin order', 11, MUTED)

for suffix in ('png', 'svg'):
    fig.savefig(OUT / f'complete_wiring.{suffix}', facecolor=BG)
plt.close(fig)
print(OUT / 'complete_wiring.png')
print(OUT / 'complete_wiring.svg')
