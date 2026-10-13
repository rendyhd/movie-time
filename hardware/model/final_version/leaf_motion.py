"""Frictionless planar rod calculation for a single, free-ended leaf.

This is a static, inextensible, linearly elastic bending model. It includes
large rotations and case contact, unlike the earlier prescribed-shape checks.
It does not establish printed friction, material recovery, creep or cycle life.
No measured PETG modulus is assumed; energy is normalized to EI=1000 N mm^2.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/final_version'
X0,Y0=202.0,25.0
# Preserve the working Plus20 bow. Only the local attachment is reinforced;
# the flexible span remains 1.2 x 10 mm and its free-end position is unchanged.
AMPLITUDE,SPAN,TRIM_DEG=29.0,46.0,3.0
THICKNESS,HEIGHT,Z=1.2,10.0,19.0
ROOT_THICKNESS,ROOT_TAPER_LENGTH=2.4,1.5
RADIUS=(AMPLITUDE**2+SPAN**2)/(4*AMPLITUDE)
ANGLE=2*np.arctan(AMPLITUDE/SPAN)
TRIM=np.deg2rad(TRIM_DEG)
LENGTH=RADIUS*(2*ANGLE-TRIM)
TIP_RADIUS=THICKNESS/2
N=40


def thickness_at(s):
    """Smooth local shoulder, with zero taper slope at either end."""
    q=np.clip(np.asarray(s,dtype=float)/ROOT_TAPER_LENGTH,0,1)
    return THICKNESS+(ROOT_THICKNESS-THICKNESS)*(1-3*q*q+2*q*q*q)


def natural_profile(samples=N):
    """Exact arc centerline and tangent angles, including the root point."""
    p=[(X0,Y0)];t=[0.0]
    x,y=X0,Y0
    for start,end in ((0.,-ANGLE),(-ANGLE,-TRIM)):
        k=np.sign(end-start)/RADIUS
        for angle in np.linspace(start,end,samples+1)[1:]:
            p.append((x+(np.cos(start)-np.cos(angle))/k,
                      y+(np.sin(angle)-np.sin(start))/k))
            t.append(float(angle))
        x,y=p[-1]
    return np.array(p),np.array(t)


class Rod:
    def __init__(self,n=N):
        self.n=n
        self.rest=np.r_[-(np.arange(n)+.5)*ANGLE/n,
                        -ANGLE+(np.arange(n)+.5)*(ANGLE-TRIM)/n]
        self.ds=np.r_[np.full(n,RADIUS*ANGLE/n),np.full(n,RADIUS*(ANGLE-TRIM)/n)]
        self.weights=(self.ds[:-1]+self.ds[1:])/2
        self.node_s=np.r_[0.,np.cumsum(self.ds)]
        self.hinge_thickness=thickness_at(self.node_s[1:-1])
        self.rigidity_ratio=(self.hinge_thickness/THICKNESS)**3
        self.intrinsic=np.diff(self.rest)
        self.fixed=self.rest[0]
        self.lower=np.tril(np.ones((2*n,2*n)))
        self.root=np.array([X0,Y0])

    def points(self,q):
        t=np.r_[self.fixed,q]
        p=np.vstack((self.root,self.root+np.cumsum(self.ds[:,None]*np.column_stack((np.sin(t),np.cos(t))),axis=0)))
        jx=self.lower[:,1:]*(self.ds*np.cos(t))[None,1:]
        jy=self.lower[:,1:]*(-self.ds*np.sin(t))[None,1:]
        zero=np.zeros((1,len(q)))
        return p,np.vstack((zero,jx)),np.vstack((zero,jy))

    def energy(self,q):
        d=(np.diff(np.r_[self.fixed,q])-self.intrinsic)/self.weights
        return float(500*np.sum(d*d*self.weights*self.rigidity_ratio))

    def gradient(self,q):
        d=(np.diff(np.r_[self.fixed,q])-self.intrinsic)/self.weights*self.rigidity_ratio
        return 1000*np.r_[-d[0],d[:-1]-d[1:],d[-1]][1:]

    def contacts(self,q,right,leading):
        p,jx,jy=self.points(q)
        # Include element midpoints to limit contact error between rod nodes.
        p=np.vstack((p,(p[:-1]+p[1:])/2))
        jx=np.vstack((jx,(jx[:-1]+jx[1:])/2))
        jy=np.vstack((jy,(jy[:-1]+jy[1:])/2))
        dx,dy=p[:,0]-right,p[:,1]-leading
        vx,vy=np.maximum(dx,0),np.maximum(dy,0)
        norm=np.hypot(vx,vy)
        distance=norm+np.minimum(np.maximum(dx,dy),0)
        gx=np.zeros(len(p));gy=np.zeros(len(p))
        outside=norm>1e-12
        gx[outside]=vx[outside]/norm[outside];gy[outside]=vy[outside]/norm[outside]
        gx[~outside & (dx>=dy)]=1;gy[~outside & (dy>dx)]=1
        sample_s=np.r_[self.node_s,(self.node_s[:-1]+self.node_s[1:])/2]
        return distance-thickness_at(sample_s)/2-.10, gx[:,None]*jx+gy[:,None]*jy

    def solve(self,right,leading,q=None):
        if q is None:q=self.rest[1:].copy()
        constraint={'type':'ineq','fun':lambda q:self.contacts(q,right,leading)[0],
                    'jac':lambda q:self.contacts(q,right,leading)[1]}
        # Scale only the optimizer objective for stable stopping near corner
        # contact. Reported energies retain the original EI=1000 convention.
        objective=lambda q:self.energy(q)/1000
        jacobian=lambda q:self.gradient(q)/1000
        result=minimize(objective,q,jac=jacobian,constraints=constraint,
                        method='SLSQP',options={'ftol':1e-12,'maxiter':1000})
        restarted=False
        if not result.success:
            # A corner-contact active set can stop at machine precision. Ask
            # the solver to reconverge from that state; never accept a failed
            # optimization merely because its drawing looks plausible.
            restarted=True
            result=minimize(objective,result.x,jac=jacobian,constraints=constraint,
                            method='SLSQP',options={'ftol':1e-11,'maxiter':1000})
        p,_,_=self.points(result.x)
        clearance=float(self.contacts(result.x,right,leading)[0].min())
        assert result.success and clearance>-.0001,(right,leading,result.message,clearance)
        t=np.r_[self.fixed,result.x]
        strain=np.max(self.hinge_thickness/2*np.abs((np.diff(t)-self.intrinsic)/self.weights))
        width=thickness_at(self.node_s)
        return result.x,p,{'right_mm':right,'leading_y_mm':leading,
                          'tip_xy_mm':p[-1].tolist(),'max_x_including_edge_mm':float(np.max(p[:,0]+width/2)),
                          'max_y_including_edge_mm':float(np.max(p[:,1]+width/2)),
                          'min_contact_constraint_mm':clearance,
                          'solver_restart_used':restarted,
                          'idealized_peak_bending_strain_percent':float(strain*100),
                          'normalized_bending_energy':self.energy(result.x)}


def run():
    (OUT/'validation').mkdir(parents=True,exist_ok=True)
    rod=Rod();reports=[];saved={};highest_x=0
    # All distinct left/center/right case edges for 170/172/190 mm cases.
    for right in (178.05,180.05,189.0,190.0,198.05,199.0,199.95):
        q=rod.rest[1:].copy()
        for leading in tuple(range(27,88,4))+(96,108):
            q,p,r=rod.solve(right,leading,q)
            reports.append(r);highest_x=max(highest_x,r['max_x_including_edge_mm'])
            saved[f'{right}_{leading}']=p
        # Reverse continuation checks frictionless extraction to zero contact.
        for leading in tuple(range(84,24,-4)):
            q,p,r=rod.solve(right,leading,q)
            r['direction']='withdrawal';reports.append(r)
            highest_x=max(highest_x,r['max_x_including_edge_mm'])
        assert np.max(np.abs(q-rod.rest[1:]))<.0001,('idealized return',right)
        print('Contact motion checked at case right edge',right,flush=True)
    # Mesh refinement at both seated formats and maximum right displacement.
    refinement=[]
    for right in (178.05,198.05,199.95):
        fine=Rod(80);q,p,r=fine.solve(right,108)
        coarse=saved[f'{right}_108']
        error=float(np.linalg.norm(coarse[-1]-p[-1]))
        assert error<.15,('rod refinement error',right,error)
        refinement.append({'case_right_mm':right,'tip_difference_mm':error})
    natural,_=natural_profile(100)
    rear_bound=Y0+LENGTH+TIP_RADIUS
    report={'revision':'single leaf reinforced root','status':'digital_design_complete_physical_validation_pending',
            'mechanism':'one fixed mounting block and one free-ended PETG leaf',
            'sliding_joints':0,'contact_motion_checks':reports,
            'all_contact_solves_converged':True,'refinement_checks':refinement,
            'leaf_thickness_mm':THICKNESS,'leaf_height_mm':HEIGHT,
            'root_thickness_mm':ROOT_THICKNESS,'root_taper_length_mm':ROOT_TAPER_LENGTH,
            'active_centerline_length_mm':LENGTH,'rest_tip_xy_mm':natural[-1].tolist(),
            'tip_rear_bound_if_straightened_mm':rear_bound,
            'minimum_tip_to_seated_case_rear_margin_mm':108-rear_bound,
            'minimum_guard_clearance_across_computed_poses_mm':211-highest_x,
            'max_idealized_bending_strain_percent':max(r['idealized_peak_bending_strain_percent'] for r in reports),
            'method':'Static planar inextensible discrete rod with intrinsic curvature, clamped root, free endpoint, nonlinear case-corner contact and thickness-dependent bending rigidity for the tapered root. Continuation through insertion and withdrawal. No guard contact is imposed; available guard clearance is checked afterward. The mounting-block fillets and underside blend are not resolved as 3D stress features.',
            'limitations':['Frictionless contact; no case sleeve friction or snag model.',
                           'No measured filament stiffness, yield, creep, fatigue or recovery model.',
                           'No layer adhesion, print tolerance or out-of-plane twist model.',
                           'Case positions are imposed; automatic left alignment and child operating force are not verified.'],
            'physically_tested':False,'automatic_alignment_verified':False,'nfc_hardware_tested':False}
    previous=OUT/'validation/previous_physical_test.json'
    if previous.exists():report['previous_revision_physical_test']=json.loads(previous.read_text())
    (OUT/'validation/motion.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez_compressed(OUT/'validation/motion_poses.npz',**saved)
    assert 211-highest_x>.75,('tip too close to guard',highest_x)
    assert 108-rear_bound>20
    print('Free-end rear bound',rear_bound,'guard clearance',211-highest_x,flush=True)


if __name__=='__main__':run()
