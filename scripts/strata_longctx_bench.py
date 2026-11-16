#!/usr/bin/env python3
"""Sequential Strata chat benchmark. No request is sent without --execute."""
import argparse, csv, datetime, hashlib, json, os, random, statistics, subprocess, threading, time, urllib.request, urllib.error, uuid
from pathlib import Path
LEVELS={'1k':1024,'64k':65536,'128k':131072,'256k':262144}
def now(): return datetime.datetime.now().astimezone().isoformat()
def fetch(url):
 with urllib.request.urlopen(url,timeout=15) as r: return json.load(r)
def prompt(n, nonce):
 rng=random.Random(9371); words=['module','request','cache','kernel','trace','buffer','result','thread','value','index','record','validate','context','engine','stream','priority']
 pieces=[]
 for i in range(n):
  s=' '.join(rng.choice(words)+str(rng.randrange(10000)) for _ in range(12))
  pieces.append(f'Item {i:06d}: {s}. The measured result needs review.\n')
 return f'Run identifier {nonce}. Read the following synthetic records. Write a detailed technical explanation of the records and their implications in at least 300 words.\n'+''.join(pieces)
def send(base,model,content,max_tokens,timeout=600):
 body={'model':model,'messages':[{'role':'user','content':content}],'temperature':0,'max_tokens':max_tokens,'stream':True,'stream_options':{'include_usage':True},'reasoning_effort':'none'}
 req=urllib.request.Request(base+'/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 t=time.monotonic(); first=None; answer=None; usage=None; timings=None; finish=None; events=[]; error=None
 try:
  with urllib.request.urlopen(req,timeout=timeout) as resp:
   for raw in resp:
    line=raw.decode('utf-8').strip()
    if not line.startswith('data:'): continue
    data=line[5:].strip()
    if data=='[DONE]': break
    try: obj=json.loads(data)
    except ValueError: error='malformed_sse'; continue
    events.append(obj); usage=obj.get('usage') or usage; timings=obj.get('timings') or timings
    for choice in obj.get('choices',[]):
     delta=choice.get('delta') or {}; content_delta=delta.get('content') or delta.get('tool_calls'); reason=delta.get('reasoning_content') or delta.get('reasoning')
     if (content_delta or reason) and first is None: first=(time.monotonic()-t)*1000
     if content_delta and answer is None: answer=(time.monotonic()-t)*1000
     finish=choice.get('finish_reason') or finish
 except Exception as e: error=type(e).__name__+': '+str(e)
 return {'usage':usage,'timings':timings,'finish_reason':finish,'ttft_ms':first,'first_answer_ms':answer,'total_ms':(time.monotonic()-t)*1000,'error':error,'events':events}
def snapshot():
 mem={}
 for line in Path('/proc/meminfo').read_text().splitlines():
  k,_,v=line.partition(':'); p=v.split()
  if p and p[0].isdigit(): mem[k]=int(p[0])
 cpu=Path('/proc/stat').read_text().splitlines()[0].split()[1:]; cpu=[int(x) for x in cpu]; freq=[]
 for x in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_cur_freq'):
  try: freq.append(int(x.read_text().strip())/1000)
  except (ValueError,OSError): pass
 row={'cpu_jiffies_total':sum(cpu),'cpu_jiffies_idle':cpu[3]+cpu[4], 'cpu_mhz_avg':statistics.mean(freq) if freq else None, 'cpu_mhz_min':min(freq) if freq else None, 'cpu_mhz_max':max(freq) if freq else None,'time':now(),'monotonic':time.monotonic(),'ram_used_gib':(mem['MemTotal']-mem['MemAvailable'])/1048576,'ram_available_gib':mem['MemAvailable']/1048576,'swap_used_gib':(mem['SwapTotal']-mem['SwapFree'])/1048576}
 processes=[]
 for f in Path('/proc').glob('[0-9]*/status'):
  try:
   fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in f.read_text().splitlines() if ':' in x}
   process_name=fields.get('Name')
   if process_name not in ('strata-host','llama-server'): continue
   cmd=(f.parent/'cmdline').read_bytes().replace(b'\0',b' ').decode('utf-8','replace')
   if process_name=='strata-host' and '/components/engine/' not in cmd: continue
   processes.append({'pid':int(f.parent.name),'name':process_name,'rss_gib':int(fields.get('VmRSS','0').split()[0])/1048576,'swap_gib':int(fields.get('VmSwap','0').split()[0])/1048576})
  except (OSError,ValueError,IndexError): pass
 row['engine_processes']=processes
 try:
  p=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,clocks.sm,clocks.mem,power.limit','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=8,check=True)
  row['gpus']=[]
  for line in p.stdout.splitlines():
   v=[x.strip() for x in line.split(',')]; keys=('index','vram_used_mib','vram_total_mib','util_pct','temp_c','power_w','sm_mhz','memory_mhz','power_limit_w')
   if len(v)==len(keys):
    try: row['gpus'].append(dict(zip(keys,[float(x) for x in v])))
    except ValueError: row['gpus'].append({'raw':line})
 except Exception as e: row['error']=str(e)
 return row
def monitor(stop,rows):
 while not stop.is_set():
  rows.append(snapshot()); stop.wait(1)
def unsafe(samples, initial=None):
 if not samples or any(not s.get('gpus') for s in samples): return True
 initial=samples[0].get('swap_used_gib',0) if initial is None else initial
 return any(s.get('ram_available_gib',100)<3 or s.get('swap_used_gib',0)-initial>.5 or any(abs(g.get('power_limit_w',0)-250)>0.5 for g in s.get('gpus',[])) for s in samples)
def xid_since(since):
 try:
  p=subprocess.run(['journalctl','-k','--since',since,'--no-pager'],capture_output=True,text=True,timeout=15)
  if p.returncode: return None
  return [line for line in p.stdout.splitlines() if ('NVRM' in line and ('Xid' in line or 'fallen off' in line))]
 except Exception: return None
def status(r,level,context,max_tokens):
 flags=[]; u=r.get('usage') or {}; t=r.get('timings') or {}; p=u.get('prompt_tokens'); c=u.get('completion_tokens'); cached=(u.get('prompt_tokens_details') or {}).get('cached_tokens',t.get('cache_n'))
 if r.get('error'): flags.append('request_error')
 if not isinstance(p,int): flags.append('missing_usage')
 elif level!='1k' and p < .9*LEVELS[level]: flags.append('input_too_short')
 if isinstance(p,int) and p+max_tokens>context: flags.append('context_overflow')
 if not isinstance(c,int) or c < .9*max_tokens: flags.append('short_output')
 if cached is None: flags.append('cache_unknown')
 elif p and cached/p>.01: flags.append('cache_contaminated')
 if r.get('ttft_ms') is None: flags.append('no_first_delta')
 if not t.get('prompt_ms') or not t.get('predicted_ms'):
  if not (r.get('first_answer_ms') and r.get('total_ms',0)>r.get('first_answer_ms',0) and isinstance(p,int) and isinstance(c,int) and c>1): flags.append('missing_timing')
 return flags

def main():
 a=argparse.ArgumentParser(); a.add_argument('--url',default='http://127.0.0.1:8080'); a.add_argument('--context',type=int,help='configured context for APIs without Strata JSON metrics'); a.add_argument('--levels',default='1k,64k,128k'); a.add_argument('--repeats',type=int,default=3); a.add_argument('--warmups',type=int,default=1); a.add_argument('--output-tokens',type=int,default=256); a.add_argument('--output-tokens-1k',type=int,default=128); a.add_argument('--gpu-index',type=int,default=0); a.add_argument('--out',required=True); a.add_argument('--execute',action='store_true'); a.add_argument('--dry-run',action='store_true'); a.add_argument('--timeout',type=int,default=5400); args=a.parse_args()
 levels=args.levels.split(',')
 if any(x not in LEVELS for x in levels) or args.repeats<1 or args.warmups<1: a.error('invalid levels or trial counts')
 print(json.dumps({'levels':levels,'execute':args.execute and not args.dry_run,'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}),flush=True)
 if not args.execute or args.dry_run: return
 power=subprocess.run(['nvidia-smi','-i',str(args.gpu_index),'--query-gpu=power.limit','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=10)
 if abs(float(power.stdout.strip())-250)>.5: raise SystemExit('GPU power limit is not 250 W; no benchmark started')
 out=Path(args.out); out.mkdir(parents=True,exist_ok=True); models=fetch(args.url+'/v1/models'); model=models['data'][0]['id']
 try:
  metrics=fetch(args.url+'/metrics'); engine=metrics.get('engine',{}); context=int(engine['max_context']) if engine.get('max_context') else args.context
 except (ValueError,KeyError,TypeError):
  with urllib.request.urlopen(args.url+'/metrics',timeout=15) as response: metrics={'prometheus_text':response.read().decode('utf-8','replace')}
  context=args.context
 if not context: raise SystemExit('context unknown; pass --context for a non-Strata server')
 for level in levels:
  target=768 if level=='1k' else int(LEVELS[level]*.95); cap=args.output_tokens_1k if level=='1k' else args.output_tokens
  if target+cap>context: raise SystemExit(f'{level} needs {target+cap} context; server reports {context}')
 if any((out/('level-'+x)).exists() for x in levels): raise SystemExit('level directory exists; choose a new output directory')
 (out/'environment.json').write_text(json.dumps({'created':now(),'metrics':metrics,'models':models,'args':vars(args),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
 for level in levels:
  folder=out/('level-'+level); folder.mkdir(); level_start=snapshot(); initial_swap=level_start['swap_used_gib']; (folder/'level_start.json').write_text(json.dumps(level_start,indent=2)); target=768 if level=='1k' else int(LEVELS[level]*.95); cap=args.output_tokens_1k if level=='1k' else args.output_tokens
  # Calibration uses measured server usage, with a one-token completion and a distinct nonce.
  n=max(1,target//75)
  for attempt in range(4):
   samples=[]; stop=threading.Event(); th=threading.Thread(target=monitor,args=(stop,samples)); start=now(); th.start()
   r=send(args.url,model,prompt(n,'calibration-'+uuid.uuid4().hex),1,args.timeout); stop.set(); th.join(); u=r.get('usage') or {}; actual=u.get('prompt_tokens'); xid=xid_since(start)
   with (folder/'calibration.jsonl').open('a') as f: f.write(json.dumps({'paragraphs':n,'response':r,'telemetry':samples,'xid':xid})+'\n')
   if not actual or r['error'] or unsafe(samples,initial_swap) or xid: raise SystemExit('calibration failed or safety stop; see calibration.jsonl')
   if abs(actual-target)<max(40,target*.025): break
   n=max(1,round(n*target/actual))
  records=[]
  for phase,count in [('warmup',args.warmups),('measured',args.repeats)]:
   for trial in range(1,count+1):
    nonce=uuid.uuid4().hex; text=prompt(n,nonce); samples=[]; stop=threading.Event(); th=threading.Thread(target=monitor,args=(stop,samples)); th.start(); started=now()
    r=send(args.url,model,text,cap,args.timeout); stop.set(); th.join(); flags=status(r,level,context,cap); xid=xid_since(started)
    u=r.get('usage') or {}; t=r.get('timings') or {}; pcount=u.get('prompt_tokens'); ccount=u.get('completion_tokens'); prefill=t.get('prompt_n',0)*1000/t['prompt_ms'] if t.get('prompt_ms') else (pcount*1000/r['first_answer_ms'] if pcount and r.get('first_answer_ms') else None); decode=t.get('predicted_n',0)*1000/t['predicted_ms'] if t.get('predicted_ms') else ((ccount-1)*1000/(r['total_ms']-r['first_answer_ms']) if ccount and ccount>1 and r.get('first_answer_ms') and r['total_ms']>r['first_answer_ms'] else None); row={'level':level,'phase':phase,'trial':trial,'started_at':started,'model':model,'configured_context_tokens':context,'target_prompt_tokens':target,'max_new_tokens':cap,'prompt_sha256':hashlib.sha256(text.encode()).hexdigest(),'actual_prompt_tokens':pcount,'cached_tokens':(u.get('prompt_tokens_details') or {}).get('cached_tokens',t.get('cache_n')),'completion_tokens':ccount,'finish_reason':r['finish_reason'],'ttft_ms':r['ttft_ms'],'first_answer_ms':r['first_answer_ms'],'total_ms':r['total_ms'],'prefill_tps':prefill,'decode_tps':decode,'timing_source':'engine' if t.get('prompt_ms') and t.get('predicted_ms') else 'wallclock_first-token_fallback','flags':flags,'error':r['error'],'xid':xid}
    with (folder/'telemetry.jsonl').open('a') as f:
     for s in samples: f.write(json.dumps({'phase':phase,'trial':trial,**s})+'\n')
    gpus=[g for sample in samples for g in sample.get('gpus',[]) if g.get('index')==args.gpu_index]
    for key in ('vram_used_mib','util_pct','temp_c','power_w','sm_mhz','memory_mhz','power_limit_w'):
     vals=[g[key] for g in gpus if key in g]; row['gpu_'+key+'_peak']=max(vals) if vals else None; row['gpu_'+key+'_avg']=statistics.mean(vals) if vals else None
    row['engine_rss_gib_peak']=max((p['rss_gib'] for s in samples for p in s.get('engine_processes',[])),default=None); row['engine_swap_gib_peak']=max((p['swap_gib'] for s in samples for p in s.get('engine_processes',[])),default=None); row['ram_used_gib_peak']=max((s['ram_used_gib'] for s in samples),default=None); row['swap_used_gib_peak']=max((s['swap_used_gib'] for s in samples),default=None)
    if len(samples)>1:
     total=samples[-1]['cpu_jiffies_total']-samples[0]['cpu_jiffies_total']; idle=samples[-1]['cpu_jiffies_idle']-samples[0]['cpu_jiffies_idle']; row['cpu_util_pct']=100*(total-idle)/total if total>0 else None
    else: row['cpu_util_pct']=None
    freq=[s['cpu_mhz_avg'] for s in samples if s.get('cpu_mhz_avg') is not None]; row['cpu_mhz_avg']=statistics.mean(freq) if freq else None
    with (folder/'requests.jsonl').open('a') as f: f.write(json.dumps({'result':row,'response':r},ensure_ascii=False)+'\n')
    records.append(row); print(json.dumps(row),flush=True)
    # Fail safe: stop after warmup safety failures or any request failure.
    if r['error'] or unsafe(samples,initial_swap) or xid: raise SystemExit('stopped for error or memory pressure')
  with (folder/'raw.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(records[0])); w.writeheader(); w.writerows(records)
  valid=[x for x in records if x['phase']=='measured' and not x['flags']]; summary={'valid_n':len(valid),'formal_n':args.repeats,'status':'complete' if len(valid)==args.repeats else 'INCOMPLETE'}
  for field in ('prefill_tps','decode_tps','ttft_ms','total_ms'):
   vals=[x[field] for x in valid if x[field] is not None]; summary[field+'_median']=statistics.median(vals) if vals else None
  (folder/'summary.json').write_text(json.dumps(summary,indent=2))
if __name__=='__main__': main()
