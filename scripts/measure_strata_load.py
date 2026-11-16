#!/usr/bin/env python3
"""Measure Strata launch-to-ready plus system telemetry; requires fixed 250 W."""
import argparse,json,os,subprocess,sys,threading,time
from pathlib import Path
from strata_longctx_bench import monitor,now,snapshot
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('out'); p.add_argument('--family',default='qwen'); p.add_argument('--model',default='iq3_s'); p.add_argument('--model-path',required=True); p.add_argument('--data-dir',required=True); p.add_argument('--context',default='4k'); a=p.parse_args()
power=subprocess.run(['nvidia-smi','-i','0','--query-gpu=power.limit','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=10)
if abs(float(power.stdout.strip())-250)>.5: raise SystemExit('GPU power limit is not 250 W; launch aborted')
out=Path(a.out); out.mkdir(parents=True,exist_ok=False); env=os.environ.copy(); env.update(STRATA_HOME=str(root/'local/state'),STRATA_COMPONENTS_DIR=str(root/'local/components'),XDG_STATE_HOME=str(root/'local/xdg-state'),STRATA_NO_ACQUIRE='1')
cmd=[str(root/'local/strata-control/bin/strata'),'launch','--family',a.family,'--model',a.model,'--model-path',str(Path(a.model_path).resolve()),'--data-dir',str(Path(a.data_dir).resolve()),'--context',a.context,'--kv','int8','--vision','off','--parallel','1','--access','local','--port','8080','--tune','skip','--drafting','off','--set','STRATA_ROUTE_TAIL_SKIP=0','--set','STRATA_PREFILL_CPU_SHARE=0','--yes','--no-tui']
rows=[]; stop=threading.Event(); before=snapshot(); t=time.monotonic(); started=now(); th=threading.Thread(target=monitor,args=(stop,rows)); th.start()
try:
 with (out/'launch.log').open('w') as f: proc=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200)
 rc=proc.returncode
except subprocess.TimeoutExpired: rc=124
finally: stop.set(); th.join()
end=now(); elapsed=time.monotonic()-t
with (out/'telemetry.jsonl').open('w') as f:
 for row in rows: f.write(json.dumps(row)+'\n')
(out/'load.json').write_text(json.dumps({'started_at':started,'ended_at':end,'elapsed_s':elapsed,'return_code':rc,'command':cmd,'before':before,'after':snapshot(),'note':'Warm filesystem cache possible; includes launcher preparation and readiness. Not disk-cold.'},indent=2))
print(json.dumps({'elapsed_s':elapsed,'return_code':rc,'samples':len(rows)}),flush=True); sys.exit(rc)
