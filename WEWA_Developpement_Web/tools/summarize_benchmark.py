"""Summarize real frame captures; does not generate fake performance results.
Input JSON: {metadata: {...}, frames: [{frame_ms, cpu_ms?, gpu_ms?}, ...]}.
Exclude loading/warmup and background intervals before capture. No empty pass.
"""
import argparse,json,math
from pathlib import Path
def percentile(a,p):
    a=sorted(a);i=(len(a)-1)*p;lo=math.floor(i);hi=math.ceil(i)
    return a[lo]+(a[hi]-a[lo])*(i-lo)
def summarize(data):
    frames=data.get('frames',[])
    if not frames:raise ValueError('No measurements supplied')
    times=[float(x['frame_ms']) for x in frames]
    if any(not math.isfinite(t) or t<=0 for t in times):raise ValueError('Invalid frame time')
    worst=sorted(times,reverse=True)[:max(1,math.ceil(len(times)*.01))]
    report={'metadata':data.get('metadata',{}),'frames':len(times),'duration_s':sum(times)/1000,
      'fps_over_capture':1000*len(times)/sum(times),'frame_ms_p50':percentile(times,.5),
      'frame_ms_p95':percentile(times,.95),'frame_ms_p99':percentile(times,.99),
      'one_percent_low_fps':1000/(sum(worst)/len(worst)),
      'frames_over_50ms':sum(t>50 for t in times),'frames_over_100ms':sum(t>100 for t in times),
      'definition':'1% low = reciprocal of mean of worst ceil(1%) frame durations; no certification implied'}
    for key in ['cpu_ms','gpu_ms']:
        values=[float(f[key]) for f in frames if f.get(key) is not None]
        if values and all(math.isfinite(v) and v>=0 for v in values):report[key+'_p95']=percentile(values,.95)
    report['duration_gate_180s']=report['duration_s']>=180
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('capture');p.add_argument('--out',required=True);a=p.parse_args()
    result=summarize(json.loads(Path(a.capture).read_text()))
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2))
