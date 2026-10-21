"""Original C2 eye/neck outline, all dimensions authored rather than calibrated."""
import math

def outline(theta,p):
    t=(theta+math.pi)%(2*math.pi)-math.pi
    a=abs(t);h=p['neck_top_relative_z_m'];cut=math.atan(p['neck_top_half_width_m']/h);end=math.radians(p['neck_circle_join_degrees']);eye=p['outer_eye_radius_m']
    if a<=cut:
        sec=1/math.cos(t);tan=math.tan(t)
        return h*tan,h,h*sec*sec,0,2*h*sec*sec*tan,0
    if a>=end:r=eye;dr=ddr=0
    else:
        length=end-cut;rc=h/math.cos(cut);dc=rc*math.tan(cut);ddc=rc*(math.tan(cut)**2+1/math.cos(cut)**2)
        c0=rc;c1=dc*length;c2=.5*ddc*length*length;A=eye-c0-c1-c2;B=-c1-2*c2;C=-2*c2
        c=[c0,c1,c2,10*A-4*B+.5*C,-15*A+7*B-C,6*A-3*B+.5*C];u=(a-cut)/length
        r=sum(v*u**i for i,v in enumerate(c));dr=sum(i*c[i]*u**(i-1)for i in range(1,6))/length*(1 if t>=0 else -1);ddr=sum(i*(i-1)*c[i]*u**(i-2)for i in range(2,6))/length**2
    s=math.sin(t);c=math.cos(t)
    return r*s,r*c,dr*s+r*c,dr*c-r*s,ddr*s+2*dr*c-r*s,ddr*c-2*dr*s-r*c

def frame(theta,p):
    x,z,dx,dz,ddx,ddz=outline(theta,p);speed=math.hypot(dx,dz);assert speed>0
    nx=-dz/speed;nz=dx/speed;scale=(dx*ddx+dz*ddz)/speed**2
    dnx=-ddz/speed-nx*scale;dnz=ddx/speed-nz*scale
    curvature=(dx*ddz-dz*ddx)/speed**3
    return x,z,dx,dz,nx,nz,dnx,dnz,curvature
