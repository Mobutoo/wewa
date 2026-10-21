"""Composition views keep local motorcycle Y up; all source vertices still checked in frame."""
import sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import powertrain_completion_common_open_v1 as protocol

def look_y_up(ob,target):
 back=(ob.location-Vector(target)).normalized();right=Vector((0,1,0)).cross(back).normalized();up=back.cross(right).normalized();ob.rotation_euler=Matrix((right,up,back)).transposed().to_euler()
protocol.look=look_y_up
review,source_dir,mode=sys.argv[sys.argv.index('--')+1:];protocol.stage(review,source_dir,mode)
