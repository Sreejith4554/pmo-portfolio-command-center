"""One authoritative calculation path for interface, reports and Power BI exports."""
from datetime import date, timedelta
from .model import validate_rules

RANK={'Green':0,'Amber':1,'Red':2}
def days(a,b):return (date.fromisoformat(a)-date.fromisoformat(b)).days
def worst(*states):return max(states,key=lambda x:RANK[x])
def band(value,amber,red):return 'Red' if value>=red else 'Amber' if value>=amber else 'Green'
def pct(a,b):return round(100*a/b,2) if b else 0


def calculate(data,day,rules):
    validate_rules(rules)
    if day not in {p['reporting_date'] for p in data['periods']}:raise ValueError('Unknown reporting period')
    source={t:[r.copy() for r in rows if r.get('reporting_date',day)==day] for t,rows in data.items()}
    people={p['person_id']:p['person_name'] for p in data['people']}
    project_dim={p['project_id']:p for p in data['projects']}
    departments={d['department_id']:d['department_name'] for d in data['departments']}
    for m in source['milestones']:
        effective=m['actual_date'] or max(m['forecast_date'],day)
        m['days_variance']=days(effective,m['baseline_date'])
        m['overdue']=int(not m['actual_date'] and m['baseline_date']<day)
        m['critical_overdue']=int(m['overdue'] and m['criticality']=='Critical')
        m['due_next_14_days']=int(not m['actual_date'] and 0<=days(m['baseline_date'],day)<=14)
        m['status']=('Completed late' if m['days_variance']>0 else 'Completed on time') if m['actual_date'] else 'Overdue' if m['overdue'] else 'Forecast late' if m['days_variance']>0 else 'Upcoming'
    for r in source['risks']:
        r['exposure']=r['probability']*r['impact']
        r['age_days']=days(day,r['opened_date']) if r['status']=='Open' else 0
        r['overdue']=int(r['status']=='Open' and r['due_date']<day)
        r['critical']=int(r['status']=='Open' and r['exposure']>=rules['risk_red_exposure'])
        r['escalation_status']='PMO' if r['critical'] else 'PM' if r['status']=='Open' and r['exposure']>=rules['risk_amber_exposure'] else 'None'
        r['owner']=people[r['owner_id']]
    for r in source['issues']:
        r['age_days']=days(r['resolution_date'] or day,r['opened_date'])
        r['overdue']=int(r['status']=='Open' and r['due_date']<day)
        r['critical']=int(r['status']=='Open' and r['severity']=='Critical')
        r['escalation_status']='PMO' if r['critical'] else 'PM' if r['overdue'] else 'None'
        r['owner']=people[r['owner_id']]
    for a in source['actions']:
        a['overdue']=int(a['status']=='Open' and a['due_date']<day);a['owner']=people[a['owner_id']]
    milestones={m['milestone_id']:m for m in source['milestones']}
    tasks={t['task_id']:t for t in source['tasks']}
    for d in source['dependencies']:
        m=milestones[d['upstream_milestone_id']];t=tasks[d['downstream_task_id']]
        available=m['actual_date'] or max(day,m['forecast_date'])
        available=(date.fromisoformat(available)+timedelta(days=d['lag_days'])).isoformat()
        d.update(available_date=available,needed_date=t['planned_start'],
                 exposure_days=max(0,days(available,t['planned_start'])) if not t['actual_finish'] else 0,
                 upstream_project=project_dim[d['upstream_project_id']]['project_name'],downstream_project=project_dim[d['project_id']]['project_name'])
        d['status']='Satisfied' if t['actual_finish'] else 'Exposed' if d['exposure_days']>0 else 'Within allowance'
        d['severe']=int(d['criticality']=='Critical' and d['exposure_days']>=rules['dependency_red_days'])
    resources=[]
    for r in data['resources']:
        allocated=sum(a['allocated_hours'] for a in source['allocations'] if a['resource_id']==r['resource_id'])
        capacity=r['weekly_capacity_hours']*rules['resource_capacity_hours']/40
        resources.append({**r,'reporting_date':day,'allocated_hours':allocated,'capacity_hours':capacity,'utilisation_pct':pct(allocated,capacity),'overload_hours':max(0,allocated-capacity)})
    source['resource_capacity']=resources
    projects=[]
    for p in data['projects']:
        pid=p['project_id'];parts={t:[r for r in rows if r.get('project_id')==pid] for t,rows in source.items()}
        s=parts['statuses'][0];b=parts['budgets'][0]
        actual=sum(c['amount'] for c in data['costs'] if c['project_id']==pid and c['transaction_date']<=day)
        variance=b['forecast_cost']-b['approved_budget'];variance_pct=pct(variance,b['approved_budget'])
        open_m=[m for m in parts['milestones'] if not m['actual_date']]
        schedule=max(0,days(s['actual_finish'] or max(s['forecast_finish'],day),p['planned_finish']))
        risks=[r for r in parts['risks'] if r['status']=='Open']
        critical_unmitigated=any(r['critical'] and r['mitigation_status']=='Not started' for r in risks)
        max_exposure=max((r['exposure'] for r in risks),default=0)
        open_issues=[i for i in parts['issues'] if i['status']=='Open']
        overdue_actions=sum(a['overdue'] for a in parts['actions'])
        exposed=[d for d in parts['dependencies'] if d['exposure_days']>0]
        rag={
          'schedule':band(schedule,rules['schedule_amber_days'],rules['schedule_red_days']),
          'cost':band(variance_pct,rules['cost_amber_pct'],rules['cost_red_pct']),
          'risk':'Red' if critical_unmitigated else 'Amber' if max_exposure>=rules['risk_amber_exposure'] else 'Green',
          'issues':'Red' if any(i['critical'] for i in open_issues) else 'Amber' if open_issues else 'Green',
          'milestones':'Red' if any(m['critical_overdue'] for m in open_m) else 'Amber' if any(m['overdue'] or m['days_variance']>=rules['schedule_amber_days'] for m in open_m) else 'Green',
          'dependencies':'Red' if any(d['severe'] for d in exposed) else 'Amber' if exposed else 'Green',
          'actions':'Red' if overdue_actions>=rules['action_red_count'] else 'Amber' if overdue_actions else 'Green',
          'reporting':'Amber' if days(day,s['last_reporting_date'])>=rules['stale_reporting_days'] else 'Green'}
        drivers=[]
        messages={
          'schedule':f'{schedule} days beyond planned finish',
          'cost':f'{variance_pct:.2f}% forecast overrun (€{variance:,.0f})',
          'risk':f'{sum(r["critical"] for r in risks)} critical risks; highest exposure {max_exposure}/25',
          'issues':f'{len(open_issues)} open issues; {sum(i["critical"] for i in open_issues)} critical',
          'milestones':f'{sum(m["critical_overdue"] for m in open_m)} critical and {sum(m["overdue"] for m in open_m)} total overdue gates',
          'dependencies':f'{len(exposed)} exposed upstream dependencies',
          'actions':f'{overdue_actions} overdue governance actions',
          'reporting':f'{days(day,s["last_reporting_date"])} days since latest submitted update'}
        for dim,state in rag.items():
            if state!='Green':drivers.append({'dimension':dim,'rag':state,'reason':messages[dim]})
        total_tasks=len(parts['tasks']);done=sum(bool(t['actual_finish']) for t in parts['tasks'])
        projects.append({**p,**s,**b,'department':departments[p['department_id']],'manager':people[p['manager_id']],'sponsor':people[p['sponsor_id']],
          'actual_cost':actual,'budget_remaining':b['approved_budget']-actual,'actual_vs_planned':actual-b['planned_cost'],
          'actual_vs_planned_pct':pct(actual-b['planned_cost'],b['planned_cost']),'forecast_variance':variance,'forecast_variance_pct':variance_pct,
          'schedule_variance_days':schedule,'percentage_complete':pct(done,total_tasks),'overall_rag':worst(*rag.values()),
          'health_dimensions':rag,'health_drivers':drivers,'open_risks':len(risks),'critical_risks':sum(r['critical'] for r in risks),
          'risk_exposure':sum(r['exposure'] for r in risks),'open_issues':len(open_issues),'critical_issues':sum(i['critical'] for i in open_issues),
          'overdue_actions':overdue_actions,'overdue_tasks':sum(not t['actual_finish'] and t['due_date']<day for t in parts['tasks']),
          'overdue_milestones':sum(m['overdue'] for m in parts['milestones']),'critical_milestones_overdue':sum(m['critical_overdue'] for m in parts['milestones']),
          'milestones_due':sum(m['due_next_14_days'] for m in parts['milestones']),'dependency_exposure':len(exposed),
          'completion_count':done,'task_count':total_tasks})
    return {'reporting_date':day,'projects':projects,**{t:source[t] for t in ('milestones','tasks','risks','issues','actions','assumptions','dependencies','allocations','resource_capacity')}}


def summarize(result,department='',rag=''):
    rows=[p for p in result['projects'] if (not department or p['department_id']==department) and (not rag or p['overall_rag']==rag)]
    active=[p for p in rows if p['lifecycle']=='Active']
    ids={p['project_id'] for p in rows};active_ids={p['project_id'] for p in active}
    out={'reporting_date':result['reporting_date'],'total_projects':len(rows),'active_projects':len(active),'completed_projects':sum(p['lifecycle']=='Completed' for p in rows),
         'on_hold_projects':sum(p['lifecycle']=='On Hold' for p in rows),'green':sum(p['overall_rag']=='Green' for p in active),'amber':sum(p['overall_rag']=='Amber' for p in active),'red':sum(p['overall_rag']=='Red' for p in active),
         'approved_budget':sum(p['approved_budget'] for p in active),'actual_cost':sum(p['actual_cost'] for p in active),'planned_cost':sum(p['planned_cost'] for p in active),'forecast_cost':sum(p['forecast_cost'] for p in active),
         'projects_over_budget':sum(p['forecast_variance']>0 for p in active),
         'average_schedule_variance':round(sum(p['schedule_variance_days'] for p in active)/len(active),2) if active else 0,
         'average_completion':round(sum(p['percentage_complete'] for p in active)/len(active),2) if active else 0}
    for field in ('overdue_milestones','critical_milestones_overdue','milestones_due','open_risks','critical_risks','open_issues','critical_issues','overdue_actions','dependency_exposure'):
        out[field]=sum(p[field] for p in active)
    out['forecast_variance']=out['forecast_cost']-out['approved_budget']
    out['forecast_variance_pct']=pct(out['forecast_variance'],out['approved_budget'])
    filtered={k:[r for r in result[k] if r['project_id'] in ids] for k in ('milestones','tasks','risks','issues','actions','assumptions','dependencies','allocations')}
    # Utilisation includes all portfolio allocations; department filtering must not hide shared work.
    used={a['resource_id'] for a in filtered['allocations']}
    resource_rows=[r for r in result['resource_capacity'] if r['resource_id'] in used]
    out['overloaded_resources']=sum(r['overload_hours']>0 for r in resource_rows)
    return {'kpis':out,'projects':rows,**filtered,'resource_capacity':resource_rows}


def history(data,rules):
    return [calculate(data,p['reporting_date'],rules) for p in data['periods']]
