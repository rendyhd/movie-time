"""Compare reinforced-root reaction with the user's working Plus20 spring.

This only estimates changes in ideal bending reaction; it is not a test of
printed joint strength. The 3D mounting fillets are outside the rod model.
"""
from pathlib import Path
import importlib.util,json

ROOT=Path(__file__).resolve().parents[2]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m

def force(module,right,h=.025):
    rod=module.Rod(80);energy=[]
    for edge in (right-h,right+h):
        q,p,r=rod.solve(edge,108)
        energy.append(r['normalized_bending_energy'])
    return (energy[1]-energy[0])/(2*h)

def run():
    old=load('plus20_leaf',ROOT/'output/final_version_plus20/source/leaf_motion.py')
    new=load('tuned_leaf',ROOT/'model/final_version/leaf_motion.py')
    assert (old.THICKNESS,old.HEIGHT,old.Z)==(new.THICKNESS,new.HEIGHT,new.Z)
    rows=[]
    for label,right in [('Blu-ray at left wall',178.05),('Blu-ray allowance at left wall',180.05),('DVD at left wall',198.05)]:
        before=force(old,right);after=force(new,right)
        rows.append({'case':label,'right_edge_mm':right,'old_normalized_force':before,
                     'new_normalized_force':after,'force_increase_percent':100*(after/before-1)})
    # Check finite-difference step sensitivity at the design target.
    fine_ratio=force(new,178.05,.0125)/force(old,178.05,.0125)
    ratio=rows[0]['new_normalized_force']/rows[0]['old_normalized_force']
    assert abs(fine_ratio-ratio)<.005
    assert 1.0<ratio<1.10,('reinforcement changes bending reaction too much',ratio)
    old_tip=old.natural_profile(100)[0][-1];new_tip=new.natural_profile(100)[0][-1]
    assert abs(old_tip-new_tip).max()<1e-9
    report={'target':'reinforce the fin attachment while preserving the working Plus20 shape',
            'change':'2.4 mm attachment tapering to the existing 1.2 mm leaf over 1.5 mm; rounded block shoulders; embedded root with underside ramp',
            'root_thickness_before_mm':1.2,'root_thickness_after_mm':new.ROOT_THICKNESS,
            'root_taper_length_mm':new.ROOT_TAPER_LENGTH,
            'mounting_holes_and_block_envelope_unchanged':True,
            'free_tip_extra_inward_reach_mm':float(old_tip[0]-new_tip[0]),
            'comparison':rows,'finite_difference_step_mm':.025,
            'half_step_force_ratio':fine_ratio,
            'method':'Derivative of normalized equilibrium bending energy against imposed case right-edge position. Variable section rigidity at the root; same nominal EI on the active span. Frictionless rod model, not a measured force. Shoulder fillets and underside blend are not modeled as 3D stress features.',
            'joint_strength_or_fatigue_verified':False,
            'tuned_spring_physically_tested':False}
    path=ROOT/'output/final_version/validation/force_tuning.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':run()
