"""Two unchanged legacy groove fields, bounded smooth union at their overlap.

Frame: axleX, y=r*sin(theta), z=.29+r*cos(theta). No new tread family.
The outer Catmull-Rom crown is evaluated from the original control polygon.
"""
import math
import numpy as np
PROFILE=np.array([(0,.290),(.012,.2893),(.023,.286),(.030,.280),(.034,.269),(.0355,.253),
 (.033,.236),(.029,.2215),(.027,.2159),(.022,.2159),(.0215,.221),(.025,.235),(.027,.250),(.026,.266),(.021,.274),(0,.280),
 (-.021,.274),(-.026,.266),(-.027,.250),(-.025,.235),(-.0215,.221),(-.022,.2159),(-.027,.2159),(-.029,.2215),(-.033,.236),(-.0355,.253),(-.034,.269),(-.030,.280),(-.023,.286),(-.012,.2893)],dtype=np.float64)

class JunctionField:
    def __init__(self,P):
        self.P=P;self.R=P['outside_radius_m_estimated'];self.pitch=math.tau*self.R/P['original_repeat_count_estimated']
        # Five monotone positive outer segments. Repair band is only4.2..7.8mm,
        # inside the first segment; extra segments merely bound diagnostics.
        self.coefficients=[]
        for i in range(5):
            a,b,c,d=[PROFILE[j%len(PROFILE)]for j in[i-1,i,i+1,i+2]]
            self.coefficients.append(np.stack([b,.5*(-a+c),.5*(2*a-5*b+4*c-d),.5*(-a+3*b-3*c+d)]))
        self.coefficients=np.array(self.coefficients)
    @staticmethod
    def smooth(a,b,x):
        t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
    def radius(self,x):
        ax=np.abs(np.asarray(x,dtype=np.float64));i=np.clip(np.searchsorted(PROFILE[1:6,0],ax,side='right'),0,4)
        c=self.coefficients[i];u=np.clip((ax-PROFILE[i,0])/(PROFILE[i+1,0]-PROFILE[i,0]),0,1)
        for _ in range(9):
            f=c[...,0,0]+u*(c[...,1,0]+u*(c[...,2,0]+u*c[...,3,0]))-ax
            derivative=c[...,1,0]+u*(2*c[...,2,0]+3*u*c[...,3,0])
            u=np.clip(u-np.divide(f,derivative,out=np.zeros_like(f),where=np.abs(derivative)>1e-12),0,1)
        return c[...,0,1]+u*(c[...,1,1]+u*(c[...,2,1]+u*c[...,3,1]))
    def fields(self,x,arc):
        x=np.asarray(x);r=self.radius(x);phase=(arc/self.pitch-.68*np.abs(x)/.031)%1
        dist=np.minimum(phase,1-phase)*self.pitch
        a=.003*(1-self.smooth(.00035,.00130,dist))
        b=.0016*(1-self.smooth(.0003,.0010,np.abs(np.abs(x)-.006)))
        mask=self.smooth(.276,.282,r)*((r>=.276)&(np.abs(x)<=.031))
        return a*mask,b*mask,dist
    def depth(self,x,arc,new=True):
        a,b,_=self.fields(x,arc);m=np.maximum(a,b)
        if not new:return m
        # Numerically stable p4 union; exactly one field returns exactly itself.
        aa=np.divide(a,m,out=np.zeros_like(a),where=m>0);bb=np.divide(b,m,out=np.zeros_like(b),where=m>0)
        return m*(aa**4+bb**4)**.25
    def crown(self,x,arc,new=True):return self.radius(x)-self.depth(x,arc,new)
    def support(self,x,arc):
        _,_,dist=self.fields(x,arc);lo,hi=self.P['repair_band_abs_x_m']
        return(np.abs(x)>=lo)&(np.abs(x)<=hi)&(dist<=self.P['repair_band_crosscut_arc_distance_max_m'])
    def normal_weight(self,x,arc):
        _,_,d=self.fields(x,arc);a=np.abs(x)
        return self.smooth(.0042,.0048,a)*(1-self.smooth(.0072,.0078,a))*(1-self.smooth(.0018,.0025,d))
    def normal(self,x,arc):
        step=2e-6;r=self.crown(x,arc);rx=(self.crown(x+step,arc)-self.crown(x-step,arc))/(2*step)
        rs=(self.crown(x,arc+step)-self.crown(x,arc-step))/(2*step);theta=arc/self.R;si=np.sin(theta);co=np.cos(theta)
        px=np.stack([np.ones_like(x),rx*si,rx*co],-1)
        ps=np.stack([np.zeros_like(x),rs*si+r/self.R*co,rs*co-r/self.R*si],-1)
        n=np.cross(px,ps);return n/np.linalg.norm(n,axis=-1)[...,None]
