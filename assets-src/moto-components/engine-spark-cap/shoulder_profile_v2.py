"""One straight conical shoulder between true tangent circular fillets."""
import math
def shoulder_profile(p):
 x0=p['shoulder_start_x_m'];x1=p['shoulder_end_x_m'];a=p['shoulder_outer_start_radius_m'];b=p['shoulder_outer_end_radius_m'];r=p['shoulder_end_arc_radius_m'];length=x1-x0;drop=a-b
 low=0.;high=1.3
 for _ in range(80):
  t=(low+high)/2;value=length*math.tan(t)-2*r*(1/math.cos(t)-1)
  if value<drop:low=t
  else:high=t
 angle=(low+high)/2;A=(x0+r*math.sin(angle),a-r*(1-math.cos(angle)));B=(x1-r*math.sin(angle),b+r*(1-math.cos(angle)));profile=[];n=p['shoulder_arc_steps']
 for j in range(1,n+1):
  t=angle*j/n;profile.append((x0+r*math.sin(t),a-r*(1-math.cos(t))))
 for x in [.052,.054,.056]:
  if A[0]<x<B[0]:profile.append((x,A[1]-math.tan(angle)*(x-A[0])))
 profile.append(B)
 for j in range(1,n+1):
  t=angle*(1-j/n);profile.append((x1-r*math.sin(t),b+r*(1-math.cos(t))))
 assert all(profile[i][0]<profile[i+1][0]for i in range(len(profile)-1))
 assert abs((A[1]-B[1])/(B[0]-A[0])-math.tan(angle))<1e-10
 return profile,{'cone_angle_deg':math.degrees(angle),'true_end_arc_radius_m':r,'straight_section_endpoints_x_r_m':[A,B],'straight_section_length_x_m':B[0]-A[0],'estimated_not_measured':True}
