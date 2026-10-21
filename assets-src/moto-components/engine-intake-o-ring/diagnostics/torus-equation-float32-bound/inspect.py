import bpy,math,json
p='/workspace/wewa-github/assets-src/moto-components/engine-intake-o-ring/engine-intake-o-ring-v1-geometry.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.collections['WEWA_ENGINE_INTAKE_O_RING'].objects:
 if o.type!='MESH':continue
 m=o.data;err=[(abs((math.hypot(v.co.x,v.co.y)-.0153)**2+v.co.z**2-.00095**2),tuple(v.co))for v in m.vertices];print('DIAG',o.name,o.location[:],m.name,len(m.vertices),max(err),min(v.co.x for v in m.vertices),max(v.co.x for v in m.vertices),o.matrix_world[:])
