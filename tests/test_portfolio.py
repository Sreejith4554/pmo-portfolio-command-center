import copy,csv,json,sys,tempfile,threading,unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from pmo.generate import generate,save
from pmo.model import validate,validate_rules
from pmo.engine import calculate,summarize,band
from pmo.reporting import exports,weekly_report
from pmo.store import Store
from pmo.server import handler
DATA=generate();RULES=json.loads((ROOT/'config/health_rules.json').read_text());DAY='2026-09-21'

class Validation(unittest.TestCase):
 def setUp(self):self.data=copy.deepcopy(DATA)
 def reject(self):
  with self.assertRaises(ValueError):validate(self.data)
 def test_full_fixture_valid(self):self.assertTrue(validate(self.data)['valid'])
 def test_milestone_baselines_stable(self):
  baseline={}
  for m in self.data['milestones']:
   baseline.setdefault(m['milestone_id'],m['baseline_date']);self.assertEqual(baseline[m['milestone_id']],m['baseline_date'])
 def test_reporting_timestamps_never_regress(self):
  for pid in {p['project_id'] for p in self.data['projects']}:
   dates=[s['last_reporting_date'] for s in self.data['statuses'] if s['project_id']==pid]
   self.assertEqual(dates,sorted(dates))
 def test_boolean_risk_score_rejected(self):self.data['risks'][0]['probability']=True;self.reject()
 def test_deterministic_generation(self):self.assertEqual(DATA,generate())
 def test_project_finish_before_start(self):self.data['projects'][0]['planned_finish']='2025-01-01';self.reject()
 def test_actual_finish_before_start(self):self.data['statuses'][0]['actual_finish']='2025-01-01';self.reject()
 def test_future_actual_milestone(self):self.data['milestones'][0]['actual_date']='2030-01-01';self.reject()
 def test_orphan_milestone(self):self.data['milestones'][0]['project_id']='MISSING';self.reject()
 def test_orphan_dependency_project(self):self.data['dependencies'][0]['upstream_project_id']='MISSING';self.reject()
 def test_mismatched_dependency_milestone(self):self.data['dependencies'][0]['upstream_milestone_id']='P01-M1';self.reject()
 def test_mismatched_downstream_task(self):self.data['dependencies'][0]['downstream_task_id']='P01-T01';self.reject()
 def test_negative_actual_cost(self):self.data['costs'][0]['amount']=-1;self.reject()
 def test_probability_bounds(self):self.data['risks'][0]['probability']=6;self.reject()
 def test_impact_bounds(self):self.data['risks'][0]['impact']=0;self.reject()
 def test_invalid_date(self):self.data['milestones'][0]['baseline_date']='2026-02-30';self.reject()
 def test_duplicate_id(self):self.data['projects'].append(self.data['projects'][0]);self.reject()
 def test_incomplete_snapshot(self):self.data['budgets'].pop();self.reject()
 def test_zero_budget(self):self.data['budgets'][0]['approved_budget']=0;self.reject()
 def test_nan_cost(self):self.data['budgets'][0]['forecast_cost']=float('nan');self.reject()
 def test_forecast_below_actual(self):self.data['budgets'][0]['forecast_cost']=1;self.reject()
 def test_unknown_resource(self):self.data['allocations'][0]['resource_id']='X';self.reject()
 def test_completed_project_deliverables(self):
  for m in self.data['milestones']:
   if m['project_id']=='P16' and m['reporting_date']==DAY:m['actual_date']=''
  self.reject()
 def test_bad_threshold_order(self):
  r=dict(RULES);r['cost_red_pct']=r['cost_amber_pct']
  with self.assertRaises(ValueError):validate_rules(r)
 def test_nonexistent_period(self):
  with self.assertRaises(ValueError):calculate(self.data,'2030-01-01',RULES)

class Calculations(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.result=calculate(DATA,DAY,RULES);cls.p={p['project_id']:p for p in cls.result['projects']}
 def test_project_count(self):self.assertEqual(len(self.p),18)
 def test_latest_rag_mix(self):
  k=summarize(self.result)['kpis'];self.assertEqual((k['active_projects'],k['green'],k['amber'],k['red']),(15,4,3,8))
 def test_green(self):self.assertEqual(self.p['P01']['overall_rag'],'Green')
 def test_amber(self):self.assertEqual(self.p['P02']['overall_rag'],'Amber')
 def test_red_forecast(self):self.assertEqual(self.p['P05']['health_dimensions']['cost'],'Red')
 def test_financial_reconcile(self):
  for p in self.p.values():
   actual=sum(c['amount'] for c in DATA['costs'] if c['project_id']==p['project_id'])
   self.assertEqual(p['actual_cost'],actual);self.assertEqual(p['forecast_variance'],p['forecast_cost']-p['approved_budget'])
 def test_cost_not_earned_value(self):self.assertEqual(self.p['P05']['actual_vs_planned'],self.p['P05']['actual_cost']-self.p['P05']['planned_cost'])
 def test_threshold_exact_boundaries(self):
  self.assertEqual([band(x,5,15) for x in (4.99,5,14.99,15)],['Green','Amber','Amber','Red'])
 def test_risk_exposure(self):
  for r in self.result['risks']:self.assertEqual(r['exposure'],r['probability']*r['impact'])
 def test_critical_risk_override(self):self.assertEqual(self.p['P06']['health_dimensions']['risk'],'Red')
 def test_closed_risk_no_escalation(self):
  for r in self.result['risks']:
   if r['status']=='Closed':self.assertEqual(r['escalation_status'],'None')
 def test_critical_issue(self):self.assertEqual(self.p['P12']['health_dimensions']['issues'],'Red')
 def test_due_today_not_overdue(self):
  data=copy.deepcopy(DATA)
  for a in data['actions']:a['due_date']=a['reporting_date']
  self.assertTrue(all(a['overdue']==0 for a in calculate(data,DAY,RULES)['actions']))
 def test_completed_late_milestone(self):
  m=next(m for m in self.result['milestones'] if m['milestone_id']=='P04-M1')
  self.assertEqual((m['status'],m['days_variance'],m['overdue']),('Completed late',3,0))
 def test_milestone_effective_date_floor(self):
  data=copy.deepcopy(DATA)
  for m in data['milestones']:
   if m['milestone_id']=='P03-M3' and m['reporting_date']==DAY:m['forecast_date']='2026-09-15'
  m=next(m for m in calculate(data,DAY,RULES)['milestones'] if m['milestone_id']=='P03-M3')
  self.assertEqual(m['days_variance'],7)
 def test_dependency_real_join(self):
  d=next(d for d in self.result['dependencies'] if d['dependency_id']=='DEP01')
  self.assertEqual((d['upstream_project_id'],d['project_id'],d['exposure_days']),('P03','P04',14))
 def test_upstream_edit_propagates(self):
  data=copy.deepcopy(DATA)
  for m in data['milestones']:
   if m['milestone_id']=='P03-M3' and m['reporting_date']==DAY:m['forecast_date']='2026-10-12'
  d=next(d for d in calculate(data,DAY,RULES)['dependencies'] if d['dependency_id']=='DEP01')
  self.assertEqual(d['exposure_days'],21)
 def test_resource_overload(self):self.assertEqual(sum(r['overload_hours']>0 for r in self.result['resource_capacity']),4)
 def test_filter_does_not_hide_other_allocations(self):
  filtered=summarize(self.result,department='D3')
  for r in filtered['resource_capacity']:
   original=next(x for x in self.result['resource_capacity'] if x['resource_id']==r['resource_id']);self.assertEqual(r,original)
 def test_completed_excluded_active_totals(self):
  k=summarize(self.result)['kpis'];self.assertEqual((k['completed_projects'],k['on_hold_projects']),(2,1))
 def test_empty_filter(self):self.assertEqual(summarize(self.result,department='missing')['kpis']['active_projects'],0)
 def test_recovery_history(self):
  first=calculate(DATA,'2026-07-06',RULES);p=next(p for p in first['projects'] if p['project_id']=='P07')
  self.assertEqual((p['overall_rag'],self.p['P07']['overall_rag']),('Red','Green'))
 def test_deterioration_history(self):
  first=calculate(DATA,'2026-07-06',RULES);p=next(p for p in first['projects'] if p['project_id']=='P08')
  self.assertEqual((p['overall_rag'],self.p['P08']['overall_rag']),('Amber','Red'))
 def test_budget_change_history(self):
  first=calculate(DATA,'2026-07-06',RULES);p=next(p for p in first['projects'] if p['project_id']=='P07')
  self.assertEqual(self.p['P07']['approved_budget']-p['approved_budget'],25000)
 def test_report_same_kpis(self):
  text=weekly_report(self.result,calculate(DATA,'2026-09-14',RULES));self.assertIn('4 Green / 3 Amber / 8 Red',text);self.assertIn('Amber → Green',text)
 def test_report_required_sections(self):
  text=weekly_report(self.result)
  for title in ('Portfolio summary','Major changes','Projects requiring attention','Critical milestones','Financial exceptions','Critical RAID','Dependency concerns','Overdue actions','Decisions required'):self.assertIn(title,text)
 def test_twelve_periods(self):self.assertEqual(len(DATA['periods']),12)
 def test_budget_movement_is_real_data(self):self.assertEqual(summarize(self.result)['kpis']['forecast_variance'],304750)

class Scenarios(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.store=Store(ROOT,self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def edit(self,**kwargs):
  body={'operation':'edit','revision':0,'table':'budgets','row_id':'P05','reporting_date':DAY,'updates':{'forecast_cost':550000}};body.update(kwargs);return self.store.change(body)
 def test_saved_edit_and_restart(self):
  self.edit();new=Store(ROOT,self.temp.name);data,_,rev,scenario=new.read()
  self.assertTrue(scenario);self.assertEqual(rev,1);self.assertEqual(next(b for b in data['budgets'] if b['project_id']=='P05' and b['reporting_date']==DAY)['forecast_cost'],550000)
 def test_baseline_unchanged(self):
  before=copy.deepcopy(self.store.baseline);self.edit();self.assertEqual(before,self.store.baseline)
 def test_reject_stale_revision(self):
  self.edit()
  with self.assertRaises(ValueError):self.edit()
 def test_invalid_edit_rollback(self):
  with self.assertRaises(ValueError):self.edit(updates={'forecast_cost':-1})
  self.assertEqual(self.store.read()[2],0)
 def test_arbitrary_field_rejected(self):
  with self.assertRaises(ValueError):self.edit(updates={'approved_budget':1})
 def test_completed_milestone_locked(self):
  with self.assertRaises(ValueError):self.edit(table='milestones',row_id='P01-M1',updates={'forecast_date':'2026-10-12'})
 def test_reset_preserves_audit(self):
  self.edit();self.store.change({'operation':'reset','revision':1});self.assertFalse(self.store.read()[3]);self.assertEqual(len(self.store.audit()),2)
 def test_rule_change_persists(self):
  r=dict(RULES);r['cost_red_pct']=30;self.store.change({'operation':'rules','revision':0,'rules':r});self.assertEqual(self.store.read()[1]['cost_red_pct'],30)
 def test_exports_keys_and_row_count(self):
  with tempfile.TemporaryDirectory() as out:
   tables,_=exports(DATA,RULES,out);self.assertEqual(len(tables['FactProject']),216)
   self.assertEqual(len({(r['project_id'],r['reporting_date']) for r in tables['FactProject']}),216)
   self.assertEqual(sum(r['amount'] for r in tables['FactCost']),sum(p['actual_cost'] for p in calculate(DATA,DAY,RULES)['projects']))

class HTTP(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(ROOT,self.temp.name);self.server=ThreadingHTTPServer(('127.0.0.1',0),handler(self.store));self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.base=f'http://127.0.0.1:{self.server.server_port}'
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
 def get(self,path):
  with urlopen(self.base+path) as r:return json.load(r)
 def test_actual_http_portfolio(self):self.assertEqual(self.get('/api/portfolio')['kpis']['active_projects'],15)
 def test_http_filter(self):self.assertTrue(all(p['department_id']=='D1' for p in self.get('/api/portfolio?department=D1')['projects']))
 def test_write_without_token_blocked(self):
  with self.assertRaises(HTTPError) as ctx:urlopen(Request(self.base+'/api/change',b'{}',{'Content-Type':'application/json'}))
  self.assertEqual(ctx.exception.code,403)
 def test_host_rebinding_blocked(self):
  with self.assertRaises(HTTPError) as ctx:urlopen(Request(self.base+'/api/meta',headers={'Host':'evil.invalid'}))
  self.assertEqual(ctx.exception.code,403)
 def test_cross_origin_blocked(self):
  token=self.get('/api/meta')['token']
  with self.assertRaises(HTTPError) as ctx:urlopen(Request(self.base+'/api/change',b'{}',{'X-PMO-Token':token,'Origin':'https://evil.invalid'}))
  self.assertEqual(ctx.exception.code,403)
 def test_write_and_read_http(self):
  token=self.get('/api/meta')['token'];body={'operation':'edit','revision':0,'table':'budgets','row_id':'P05','reporting_date':DAY,'updates':{'forecast_cost':550000}}
  with urlopen(Request(self.base+'/api/change',json.dumps(body).encode(),{'X-PMO-Token':token,'Content-Type':'application/json'})) as r:self.assertEqual(json.load(r)['revision'],1)
  result=self.get('/api/portfolio');self.assertTrue(result['scenario'])

if __name__=='__main__':unittest.main()
