import importlib.util, json, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
spec=importlib.util.spec_from_file_location('bench','scripts/strata_longctx_bench.py'); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
class TestBench(unittest.TestCase):
 def test_status_and_cache(self):
  r={'usage':{'prompt_tokens':63000,'completion_tokens':256,'prompt_tokens_details':{'cached_tokens':0}},'timings':{'prompt_ms':100,'predicted_ms':100},'ttft_ms':10,'error':None}
  self.assertEqual(b.status(r,'64k',131072,256),[])
  r['usage']['prompt_tokens']=100; r['usage']['completion_tokens']=1; r['usage']['prompt_tokens_details']['cached_tokens']=4
  self.assertTrue({'input_too_short','short_output','cache_contaminated'}.issubset(b.status(r,'64k',131072,256)))
  self.assertIn('context_overflow',b.status(r,'1k',200,128))
 def test_missing(self):
  f=b.status({'usage':None,'timings':None,'ttft_ms':None,'error':'timeout'},'1k',4096,128)
  self.assertTrue({'request_error','missing_usage','missing_timing','no_first_delta','cache_unknown'}.issubset(f))
 def test_stream(self):
  class H(BaseHTTPRequestHandler):
   def do_POST(self):
    self.send_response(200); self.end_headers()
    events=[': keepalive','data: '+json.dumps({'choices':[{'delta':{'role':'assistant'}}]}),'data: '+json.dumps({'choices':[{'delta':{'reasoning_content':'think'}}]}),'data: '+json.dumps({'choices':[{'delta':{'content':'yes'},'finish_reason':'stop'}],'usage':{'prompt_tokens':12,'completion_tokens':1},'timings':{'prompt_ms':3,'predicted_ms':2}}),'data: [DONE]']
    self.wfile.write(('\n\n'.join(events)+'\n\n').encode())
   def log_message(self,*args): pass
  server=HTTPServer(('127.0.0.1',0),H); t=threading.Thread(target=server.serve_forever,daemon=True); t.start()
  try:
   r=b.send('http://127.0.0.1:'+str(server.server_port),'m','hi',1,5); self.assertEqual(r['usage']['prompt_tokens'],12); self.assertEqual(r['finish_reason'],'stop'); self.assertIsNotNone(r['ttft_ms']); self.assertIsNotNone(r['first_answer_ms']); self.assertIsNone(r['error'])
  finally: server.shutdown(); server.server_close()
 def test_telemetry(self):
  s=b.snapshot(); self.assertGreater(s['ram_available_gib'],0); self.assertIn('cpu_jiffies_total',s)
if __name__=='__main__': unittest.main()
