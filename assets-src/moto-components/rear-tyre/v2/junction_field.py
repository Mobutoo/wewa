"""Original V1 scalar fields, and bounded smooth junction-only smooth depth union.
No photo pixels, commercial mould, new groove, diameter or width definition.
"""
import numpy as np,math
class JunctionField:
 def __init__(self,P):
  self.P=P;self.pitch=math.tau*P['outside_radius_m_estimated']/P['tread_repeats_estimated'];q=np.array(P['outer_profile_xr_m_estimated'][4:13]);self.xs=q[:,0];self.ys=q[:,1];h=np.diff(self.xs);d=np.diff(self.ys)/h;m=[d[0]]
  for i in range(1,len(self.xs)-1):
   a,b=d[i-1:i+1];w0,w1=2*h[i]+h[i-1],h[i]+2*h[i-1];m.append(0 if a*b<=0 else(w0+w1)/(w0/a+w1/b))
  m.append(d[-1]);self.ms=np.array(m)
 def radius(self,x):
  i=np.clip(np.searchsorted(self.xs,x,side='right')-1,0,len(self.xs)-2);h=self.xs[i+1]-self.xs[i];u=(x-self.xs[i])/h;return(2*u**3-3*u*u+1)*self.ys[i]+(u**3-2*u*u+u)*h*self.ms[i]+(-2*u**3+3*u*u)*self.ys[i+1]+(u**3-u*u)*h*self.ms[i+1]
 @staticmethod
 def smooth(a,b,x):
  t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
 def trench(self,d,width,depth):return depth*(1-self.smooth(max(0,width/2-self.P['groove_lip_transition_m_estimated']),width/2,d))
 def fields(self,x,arc,terminate=False):
  r=self.radius(x);side=np.where(x>=0,1.,-1.);ax=np.abs(x);u=arc/self.pitch;lane=.010+.0024*np.sin(math.tau*u+.35*side);a=self.trench(np.abs(ax-lane),self.P['main_groove_width_m_estimated'],self.P['groove_depth_m_estimated']);target=.60*ax+.0018*np.sin(ax/.032*math.pi)+np.where(side>0,0,self.pitch*.5);dist=np.abs((arc-target+self.pitch/2)%self.pitch-self.pitch/2)/math.sqrt(1+.60**2);b=self.trench(dist,.0030,.0032)*self.smooth(.0065,.012,ax)*(1-self.smooth(.034,.039,ax));dist=np.abs((arc+.003*np.sin(x/.012*math.pi)+self.pitch)%(2*self.pitch)-self.pitch);c=self.trench(dist,.0028,.0029)*(1-self.smooth(.008,.012,ax));
  if terminate:
   bottom=self.P['main_groove_width_m_estimated']/2-self.P['groove_lip_transition_m_estimated'];g=self.smooth(lane-bottom,lane+bottom,ax);b=b*g;c=c*(1-g)
  fade=self.smooth(.279,.289,r)*((r>=.279)&(ax<=.039));return np.stack([a,b,c],axis=-1)*fade[...,None]
 def depth(self,x,arc,new=True):
  a=self.fields(x,arc,terminate=new and self.P.get('terminate_in_main_groove_floor',False));m=a.max(axis=-1)
  if not new:return m
  # Scaled p-norm avoids powers of millimetres and retains exact single-field values.
  u=np.divide(a,m[...,None],out=np.zeros_like(a),where=m[...,None]>0);return m*np.sum(u**self.P['junction_union_p'],axis=-1)**(1/self.P['junction_union_p'])
 def crown(self,x,arc):return self.radius(x)-self.depth(x,arc)
