"""Render the actual final enclosure STEP files with the existing CAD renderer."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model'))
import render_model
render_model.OUT=ROOT/'output/final_version'
if __name__=='__main__':
    for mode in ('assembled','top'):
        print('Rendering final',mode,flush=True)
        render_model.scene(mode)
