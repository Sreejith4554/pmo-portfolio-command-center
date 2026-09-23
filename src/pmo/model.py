"""Relational data-quality checks. Reject inconsistent input rather than mask it."""
import json
import math
from datetime import date
from pathlib import Path

KEYS={'departments':['department_id'],'people':['person_id'],'projects':['project_id'],'resources':['resource_id'],'periods':['reporting_date'],
 'statuses':['project_id','reporting_date'],'budgets':['project_id','reporting_date'],'costs':['cost_id']}
for table,key in [('milestones','milestone_id'),('tasks','task_id'),('risks','risk_id'),('issues','issue_id'),('actions','action_id'),('dependencies','dependency_id'),('allocations','allocation_id'),('assumptions','assumption_id')]:KEYS[table]=[key,'reporting_date']

def require(condition,message):
    if not condition:raise ValueError(message)

def valid_date(value):
    require(isinstance(value,str) and date.fromisoformat(value).isoformat()==value,'Invalid ISO date')

def number(value,minimum=0):
    require(isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=minimum,'Invalid numeric value')

def validate(data):
    for table,keys in KEYS.items():
        require(table in data and isinstance(data[table],list),f'Missing table {table}')
        ids=[]
        for row in data[table]:
            require(all(k in row and row[k]!='' for k in keys),f'Missing key in {table}')
            ids.append(tuple(row[k] for k in keys))
            for key,value in row.items():
                if (key.endswith('_date') or key in ('planned_start','planned_finish','forecast_finish','actual_finish')) and value:valid_date(value)
        require(len(ids)==len(set(ids)),f'Duplicate key in {table}')
    projects={p['project_id']:p for p in data['projects']};people={p['person_id'] for p in data['people']}
    periods={p['reporting_date'] for p in data['periods']};resources={r['resource_id']:r for r in data['resources']}
    departments={d['department_id'] for d in data['departments']}
    require(len(periods)>0,'Reporting periods missing')
    for r in data['resources']:number(r['weekly_capacity_hours'],1)
    for p in projects.values():
        require(p['department_id'] in departments,'Orphan department')
        require(p['manager_id'] in people and p['sponsor_id'] in people,'Orphan project owner')
        require(p['planned_start']<=p['planned_finish'],'Finish precedes start')
    for table,rows in data.items():
        for row in rows:
            if 'project_id' in row:require(row['project_id'] in projects,f'Orphan project in {table}')
            if table!='periods' and 'reporting_date' in row:require(row['reporting_date'] in periods,'Unknown reporting period')
            if 'owner_id' in row:require(row['owner_id'] in people,'Unknown owner')
    expected={(p,d) for p in projects for d in periods}
    for table in ('statuses','budgets'):
        require({(r['project_id'],r['reporting_date']) for r in data[table]}==expected,f'Incomplete {table} snapshots')
    statuses={(r['project_id'],r['reporting_date']):r for r in data['statuses']}
    for s in data['statuses']:
        p=projects[s['project_id']]
        require(s['lifecycle'] in ('Active','Completed','On Hold'),'Invalid lifecycle')
        require(s['forecast_finish']>=p['planned_start'],'Forecast before start')
        require(s['last_reporting_date']<=s['reporting_date'],'Reporting timestamp in future')
        if s['actual_finish']:
            require(p['planned_start']<=s['actual_finish']<=s['reporting_date'],'Invalid project actual finish')
        require((s['lifecycle']=='Completed')==bool(s['actual_finish']),'Completion state mismatch')
    for table in ('milestones','tasks'):
        for r in data[table]:
            actual=r['actual_date'] if table=='milestones' else r['actual_finish']
            require((r['project_id'],r['reporting_date']) in statuses,'Missing status')
            if actual:require(projects[r['project_id']]['planned_start']<=actual<=r['reporting_date'],'Invalid actual date')
            if table=='milestones':
                require(r['criticality'] in ('Critical','Normal'),'Invalid milestone criticality')
                require(r['forecast_date']>=projects[r['project_id']]['planned_start'],'Milestone forecast before project start')
            else:
                require(r['planned_start']<=r['due_date'],'Task finish before start')
                if actual:require(actual>=r['planned_start'],'Task completes before planned start')
            if statuses[(r['project_id'],r['reporting_date'])]['lifecycle']=='Completed':require(bool(actual),'Incomplete deliverable in completed project')
    for key in expected:
        require(any((t['project_id'],t['reporting_date'])==key for t in data['tasks']),'Project snapshot has no tasks')
    for r in data['risks']:
        require(type(r['probability']) is int and 1<=r['probability']<=5,'Risk probability outside 1–5')
        require(type(r['impact']) is int and 1<=r['impact']<=5,'Risk impact outside 1–5')
        require(r['status'] in ('Open','Closed'),'Invalid risk status')
        require(r['mitigation_status'] in ('Not started','In progress','Complete'),'Invalid mitigation status')
        require(r['opened_date']<=r['reporting_date'],'Risk not yet opened')
    for r in data['issues']:
        require(r['status'] in ('Open','Resolved') and r['severity'] in ('Critical','Moderate'),'Invalid issue values')
        require(r['opened_date']<=r['reporting_date'],'Issue not yet opened')
        require((r['status']=='Resolved')==bool(r['resolution_date']),'Issue resolution mismatch')
        if r['resolution_date']:require(r['opened_date']<=r['resolution_date']<=r['reporting_date'],'Invalid issue resolution date')
    for a in data['actions']:require(a['status'] in ('Open','Done'),'Invalid action status')
    for b in data['budgets']:
        number(b['approved_budget'],1);number(b['planned_cost']);number(b['forecast_cost'])
        actual=sum(c['amount'] for c in data['costs'] if c['project_id']==b['project_id'] and c['transaction_date']<=b['reporting_date'])
        require(b['forecast_cost']>=actual,'Forecast below actual cost')
    for c in data['costs']:
        number(c['amount']);require(c['transaction_date'] in periods,'Cost outside reporting periods')
    for a in data['allocations']:
        require(a['resource_id'] in resources,'Unknown resource');number(a['allocated_hours'])
    ms={(m['milestone_id'],m['reporting_date']):m for m in data['milestones']}
    tasks={(t['task_id'],t['reporting_date']):t for t in data['tasks']}
    for d in data['dependencies']:
        require(d['upstream_project_id'] in projects and d['upstream_project_id']!=d['project_id'],'Invalid upstream project')
        mk=(d['upstream_milestone_id'],d['reporting_date']);tk=(d['downstream_task_id'],d['reporting_date'])
        require(mk in ms and ms[mk]['project_id']==d['upstream_project_id'],'Invalid upstream milestone')
        require(tk in tasks and tasks[tk]['project_id']==d['project_id'],'Invalid downstream task')
        number(d['lag_days']);require(d['criticality'] in ('Critical','Normal'),'Invalid dependency criticality')
    return {'valid':True,'tables':len(data),'rows':sum(len(v) for v in data.values())}


def load(root):
    data=json.loads((Path(root)/'data/raw/portfolio.json').read_text(encoding='utf-8'))
    validate(data)
    return data


def validate_rules(rules):
    expected={'schedule_amber_days','schedule_red_days','cost_amber_pct','cost_red_pct','risk_amber_exposure','risk_red_exposure','dependency_red_days','action_red_count','stale_reporting_days','resource_capacity_hours'}
    require(set(rules)==expected,'Invalid configuration keys')
    for value in rules.values():number(value,1)
    for prefix,suffix in [('schedule','days'),('cost','pct'),('risk','exposure')]:
        require(rules[f'{prefix}_amber_{suffix}']<rules[f'{prefix}_red_{suffix}'],'Amber threshold must be below red')
    require(rules['risk_red_exposure']<=25,'Risk threshold exceeds scoring scale')
    return rules
