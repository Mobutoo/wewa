"""Observed bearing disk/stem; unobserved plain crown explicitly provisional.
One closed mesh; cosmetic helical profile, no engagement or exact ISO claim.
"""
import math

def build(P):
 N=P['angular_vertices'];R=P['working_head_radius_m'];h=P['working_head_crown_height_m'];edge=P['working_head_edge_radius_m'];root=P['working_thread_root_radius_m'];crest=P['working_thread_crest_radius_m'];blend=P['working_root_blend_radius_m'];L=P['working_stem_length_m'];pitch=P['nominal_related_thread_pitch_m'];profile=[]
 # Front crown begins at one pole, never a collapsed circumferential ring.
 pole=(-edge-h,0)
 for j in range(1,65):
  a=math.pi*j/128;profile.append((-edge-h*math.cos(a),R*math.sin(a),False))
 for j in range(1,25):
  a=math.pi*j/48;profile.append((-edge+edge*math.sin(a),R-edge+edge*math.cos(a),False))
 begin=R-edge;finish=root+blend
 for j in range(1,129):
  t=j/128;r=begin+(finish-begin)*t;depression=P['working_underside_groove_amplitude_m']*math.sin(math.pi*t)**2*math.sin(math.pi*P['working_underside_concentric_groove_count']*t)**2;profile.append((-depression,r,False))
 for j in range(1,25):
  a=math.pi*j/48;profile.append((blend*(1-math.cos(a)),root+blend-blend*math.sin(a),False))
 tipround=.00015;steps=math.ceil((L-tipround-blend)/pitch*P['thread_samples_per_pitch'])
 for j in range(1,steps+1):profile.append((blend+(L-tipround-blend)*j/steps,root,True))
 for j in range(1,25):
  a=math.pi*j/48;profile.append((L-tipround+tipround*math.sin(a),root-tipround+tipround*math.cos(a),False))
 def rounded_ramp(t,e=.10):
  return (t*t/(2*e)if t<e else (1-e)-(1-t)**2/(2*e)if t>1-e else t-e/2)/(1-e)
 def radius(x,base,thread,a):
  if not thread:return base
  phase=((x-blend)/pitch-a/math.tau)%1
  q=1 if phase<.12 or phase>.88 else 1-rounded_ramp((phase-.12)/.34)if phase<.46 else 0 if phase<.54 else rounded_ramp((phase-.54)/.34)
  run=.00045;t=min(1,max(0,(x-blend)/run),max(0,(L-tipround-x)/run));fade=t*t*(3-2*t);return root+(crest-root)*q*fade
 vertices=[(pole[0],0,0)];faces=[];UV=[];lengths=[0.];previous=pole
 for x,r,thread in profile:lengths.append(lengths[-1]+math.dist(previous,(x,r)));previous=(x,r)
 total=lengths[-1]+profile[-1][1];vs=[q/total for q in lengths];end=len(profile)
 for x,r,thread in profile:
  for j in range(N):
   a=math.tau*j/N;rr=radius(x,r,thread,a);vertices.append((x,rr*math.cos(a),rr*math.sin(a)))
 for j in range(N):
  faces.append((0,1+j,1+(j+1)%N));UV.append([((j+.5)/N,0),(j/N,vs[1]),((j+1)/N,vs[1])])
 for i in range(len(profile)-1):
  for j in range(N):
   k=(j+1)%N;a=1+i*N+j;b=1+i*N+k;c=1+(i+1)*N+k;d=1+(i+1)*N+j;faces.extend([(a,d,c),(a,c,b)]);UV.extend([[(j/N,vs[i+1]),(j/N,vs[i+2]),((j+1)/N,vs[i+2])],[(j/N,vs[i+1]),((j+1)/N,vs[i+2]),((j+1)/N,vs[i+1])]])
 cap=len(vertices);vertices.append((L,0,0));last=1+(len(profile)-1)*N
 for j in range(N):faces.append((last+j,cap,last+(j+1)%N));UV.append([(j/N,vs[-1]),((j+.5)/N,1),((j+1)/N,vs[-1])])
 return vertices,faces,UV,{'angular_vertices':N,'meridian_rings':len(profile),'cosmetic_pitch_m':pitch,'nominal_pitch_source':'Related catalogue only, not measured currentRDC','head_crown_and_drive_unobserved':True,'plain_crown_is_incomplete_provisional_envelope':True,'separate_washer_inferred':False,'thread_profile_engagement_certified':False,'all_non_nominal_dimensions_estimated':True}
