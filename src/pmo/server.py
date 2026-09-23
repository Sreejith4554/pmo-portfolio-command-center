"""Local management UI; same-origin writes, revision checks and bounded input."""
import argparse
import json
import logging
import os
import secrets
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from .store import Store
from .engine import calculate,summarize
from .reporting import weekly_report,exports


def handler(store):
    token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args):logging.info('%s %s',self.command,self.path.split('?')[0])
        def send(self,status,data,ctype='application/json'):
            if ctype=='application/json':data=json.dumps(data,allow_nan=False).encode()
            elif isinstance(data,str):data=data.encode()
            self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'")
            self.end_headers();self.wfile.write(data)
        def host_ok(self):return urlparse('http://'+self.headers.get('Host','')).hostname in ('localhost','127.0.0.1','::1')
        def do_GET(self):
            if not self.host_ok():return self.send(403,{'error':'Local host only'})
            path=urlparse(self.path);q=parse_qs(path.query)
            try:
                if path.path in ('/','/app.js','/style.css'):
                    name={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[path.path]
                    ctype={'/':'text/html; charset=utf-8','/app.js':'text/javascript; charset=utf-8','/style.css':'text/css; charset=utf-8'}[path.path]
                    return self.send(200,(store.root/'dashboard'/name).read_bytes(),ctype)
                data,rules,revision,scenario=store.read();day=q.get('period',[data['periods'][-1]['reporting_date']])[0]
                if path.path=='/api/meta':return self.send(200,{'periods':data['periods'],'departments':data['departments'],'rules':rules,'revision':revision,'scenario':scenario,'token':token})
                if path.path=='/api/audit':return self.send(200,store.audit())
                if path.path not in ('/api/portfolio','/api/report'):return self.send(404,{'error':'Not found'})
                result=calculate(data,day,rules);department=q.get('department',[''])[0];rag=q.get('rag',[''])[0]
                if path.path=='/api/report':
                    dates=[p['reporting_date'] for p in data['periods']];i=dates.index(day);previous=calculate(data,dates[i-1],rules) if i else None
                    return self.send(200,weekly_report(result,previous,department,rag,scenario),'text/markdown; charset=utf-8')
                all_results=[calculate(data,p['reporting_date'],rules) for p in data['periods'] if p['reporting_date']<=day]
                trends=[summarize(r,department,rag)['kpis'] for r in all_results]
                out=summarize(result,department,rag)
                out.update(history=trends,revision=revision,scenario=scenario,rules=rules,
                   project_history={p['project_id']:[{k:v for k,v in x.items() if k in ('reporting_date','overall_rag','percentage_complete','approved_budget','forecast_cost','risk_exposure','schedule_variance_days')} for period_result in all_results for x in period_result['projects'] if x['project_id']==p['project_id']] for p in out['projects']})
                self.send(200,out)
            except (ValueError,KeyError,TypeError) as e:self.send(422,{'error':str(e)})
            except Exception:
                logging.exception('Read failed');self.send(500,{'error':'Read failed; inspect local server log'})
        def do_POST(self):
            if not self.host_ok():return self.send(403,{'error':'Local host only'})
            origin=self.headers.get('Origin')
            if origin and origin!='http://'+self.headers.get('Host'):return self.send(403,{'error':'Origin rejected'})
            if not secrets.compare_digest(self.headers.get('X-PMO-Token',''),token):return self.send(403,{'error':'Session token required'})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<=length<=65536:raise ValueError('Request too large')
                body=json.loads(self.rfile.read(length) or b'{}')
                if self.path=='/api/change':result=store.change(body)
                elif self.path=='/api/export':
                    data,rules,revision,scenario=store.read();tables,_=exports(data,rules,store.root/'output',scenario)
                    result={'tables':len(tables),'rows':sum(len(r) for r in tables.values()),'folder':'output','revision':revision}
                else:return self.send(404,{'error':'Not found'})
                self.send(200,result)
            except (ValueError,KeyError,TypeError) as e:self.send(422,{'error':str(e)})
            except Exception:
                logging.exception('Write failed');self.send(500,{'error':'Write failed; inspect local server log'})
    return Handler


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--bind',default='127.0.0.1');args=parser.parse_args()
    root=Path(__file__).resolve().parents[2];logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
    store=Store(root,os.getenv('PMO_STATE_DIR'));server=ThreadingHTTPServer((args.bind,args.port),handler(store))
    print(f'PMO Command Center: http://localhost:{args.port} — synthetic portfolio',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
