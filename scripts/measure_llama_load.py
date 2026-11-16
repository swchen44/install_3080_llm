#!/usr/bin/env python3
"""Launch a local llama-server and record startup plus host/GPU telemetry."""
import argparse, datetime, json, os, signal, statistics, subprocess, threading, time, urllib.error, urllib.request
from pathlib import Path

def now(): return datetime.datetime.now().astimezone().isoformat()

def snapshot(pid):
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, _, value = line.partition(':'); fields = value.split()
        if fields and fields[0].isdigit(): mem[key] = int(fields[0])
    stat = [int(x) for x in Path('/proc/stat').read_text().splitlines()[0].split()[1:]]
    freqs = []
    for item in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_cur_freq'):
        try: freqs.append(int(item.read_text().strip()) / 1000)
        except (OSError, ValueError): pass
    proc = {}
    try:
        status = {line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line}
        proc = {'pid': pid, 'rss_gib': int(status.get('VmRSS','0').split()[0])/1048576, 'swap_gib': int(status.get('VmSwap','0').split()[0])/1048576}
    except (OSError, ValueError, IndexError): pass
    gpu = subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,clocks.sm,clocks.mem,power.limit','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=8)
    vals = [x.strip() for x in gpu.stdout.strip().split(',')]
    names = ('index','vram_used_mib','vram_total_mib','util_pct','temp_c','power_w','sm_mhz','memory_mhz','power_limit_w')
    gpus = [dict(zip(names,[float(x) for x in vals]))] if len(vals)==len(names) else []
    return {'time':now(),'cpu_jiffies_total':sum(stat),'cpu_jiffies_idle':stat[3]+stat[4],
            'cpu_mhz_avg':statistics.mean(freqs) if freqs else None,
            'ram_available_gib':mem.get('MemAvailable',0)/1048576,
            'swap_used_gib':(mem.get('SwapTotal',0)-mem.get('SwapFree',0))/1048576,
            'process':proc,'gpus':gpus}

def ready(url):
    for suffix in ('/health','/v1/models'):
        try:
            with urllib.request.urlopen(url.rstrip('/')+suffix, timeout=2) as response:
                if response.status == 200: return True
        except Exception: pass
    return False

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--server',required=True); p.add_argument('--model',required=True); p.add_argument('--out',required=True)
    p.add_argument('--context',type=int,default=4096); p.add_argument('--gpu-layers',type=int,default=99)
    p.add_argument('--threads',type=int,default=10); p.add_argument('--cache-k',default='q8_0'); p.add_argument('--cache-v',default='q8_0')
    p.add_argument('--port',type=int,default=8081); p.add_argument('--timeout',type=int,default=1200)
    p.add_argument('--no-kv-offload',action='store_true'); p.add_argument('--library-path',action='append',default=[])
    a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=False)
    power=subprocess.run(['nvidia-smi','-i','0','--query-gpu=power.limit','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True,timeout=10)
    if abs(float(power.stdout.strip())-250)>0.5: raise SystemExit('GPU power limit is not 250 W; launch aborted')
    cmd=[a.server,'--model',a.model,'--ctx-size',str(a.context),'--gpu-layers',str(a.gpu_layers),'--threads',str(a.threads),'--threads-batch',str(a.threads),
         '--parallel','1','--cache-type-k',a.cache_k,'--cache-type-v',a.cache_v,'--flash-attn','on','--metrics','--host','127.0.0.1','--port',str(a.port),'--jinja']
    if a.no_kv_offload: cmd.append('--no-kv-offload')
    env=os.environ.copy(); env['LD_LIBRARY_PATH']=':'.join(a.library_path+[env.get('LD_LIBRARY_PATH','')]).strip(':')
    start=now(); t=time.monotonic(); before=snapshot(os.getpid()); samples=[]
    log=(out/'server.log').open('w')
    proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    initial_swap=before['swap_used_gib']; status='timeout'
    try:
        while time.monotonic()-t < a.timeout:
            row=snapshot(proc.pid); samples.append(row)
            if row['gpus'] and any(abs(g['power_limit_w']-250)>0.5 for g in row['gpus']): status='power_limit_changed'; break
            if row['ram_available_gib']<3: status='low_available_ram'; break
            if row['swap_used_gib']-initial_swap>3: status='swap_pressure'; break
            if ready(f'http://127.0.0.1:{a.port}'):
                status='ready'; break
            if proc.poll() is not None: status='process_exit'; break
            time.sleep(1)
    finally:
        if status!='ready' and proc.poll() is None:
            os.killpg(proc.pid,signal.SIGTERM)
            try: proc.wait(timeout=15)
            except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait()
        log.close()
    ended=now(); elapsed=time.monotonic()-t
    with (out/'telemetry.jsonl').open('w') as f:
        for row in samples: f.write(json.dumps(row)+'\n')
    report={'started_at':start,'ended_at':ended,'elapsed_s':elapsed,'status':status,'command':cmd,
            'environment':{'LD_LIBRARY_PATH':env['LD_LIBRARY_PATH']},'before':before,
            'after':snapshot(proc.pid) if proc.poll() is None else snapshot(os.getpid()),
            'process_pid':proc.pid,'process_return_code':proc.poll(),
            'note':'Filesystem page cache may be warm; load startup is not a disk-cold result.'}
    (out/'startup.json').write_text(json.dumps(report,indent=2)); print(json.dumps({'status':status,'elapsed_s':elapsed,'pid':proc.pid}),flush=True)
    if status!='ready': raise SystemExit(f'server failed to become ready: {status}; inspect server.log')

if __name__=='__main__': main()
