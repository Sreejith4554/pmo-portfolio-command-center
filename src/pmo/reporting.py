"""Reproducible management reports and typed star-schema CSV exports."""
import json
from pathlib import Path
from .engine import summarize, history
from .generate import write_csv


def weekly_report(current,previous=None,department='',rag='',scenario=False):
    view=summarize(current,department,rag);k=view['kpis'];active=[p for p in view['projects'] if p['lifecycle']=='Active']
    prior={p['project_id']:p for p in previous['projects']} if previous else {}
    def line(text):return '- '+text+'\n'
    text=f"# Weekly PMO report — {current['reporting_date']}\n\nINDEPENDENT PORTFOLIO PROJECT · Entirely synthetic data and financial values.\n\n"
    text+=f"Mode: {'SAVED SCENARIO' if scenario else 'BASELINE'}. Department filter: {department or 'All'}; RAG filter: {rag or 'All'}. Financial and exception totals cover Active projects only.\n\n## Portfolio summary\n\n"
    text+=line(f"{k['total_projects']} projects in scope: {k['active_projects']} Active, {k['completed_projects']} Completed, {k['on_hold_projects']} On Hold.")
    text+=line(f"Active health: {k['green']} Green / {k['amber']} Amber / {k['red']} Red.")
    text+=line(f"Approved budget €{k['approved_budget']:,.0f}; actual €{k['actual_cost']:,.0f}; forecast €{k['forecast_cost']:,.0f}; forecast variance €{k['forecast_variance']:,.0f} ({k['forecast_variance_pct']}%).")
    text+='\n## Major changes since previous period\n\n'
    changes=[]
    for p in view['projects']:
        old=prior.get(p['project_id'])
        if old and (p['overall_rag']!=old['overall_rag'] or p['lifecycle']!=old['lifecycle'] or p['approved_budget']!=old['approved_budget']):
            changes.append(f"{p['project_name']}: {old['overall_rag']} → {p['overall_rag']}; {old['lifecycle']} → {p['lifecycle']}; approved budget movement €{p['approved_budget']-old['approved_budget']:,.0f}.")
    text+=''.join(line(x) for x in changes) or 'No RAG, lifecycle or approved-budget changes within this filter (or no previous period).\n'
    text+='\n## Projects requiring attention\n\n'
    for p in active:
        if p['overall_rag']!='Green':text+=line(f"{p['project_id']} {p['project_name']} — {p['overall_rag']}: "+'; '.join(d['reason'] for d in p['health_drivers']))
    ids={p['project_id'] for p in active}
    sections=[('Critical milestones',view['milestones'],lambda r:r['critical_overdue'],lambda r:f"{r['project_id']} {r['milestone_name']}: baseline {r['baseline_date']}, forecast {r['forecast_date']}, variance {r['days_variance']} days."),
      ('Financial exceptions',active,lambda r:r['forecast_variance']>0,lambda r:f"{r['project_name']}: €{r['forecast_variance']:,.0f} forecast overrun ({r['forecast_variance_pct']}%)."),
      ('Critical RAID items',view['risks']+view['issues'],lambda r:r['critical'],lambda r:f"{r['project_id']} {r['title']} — owner {r['owner']}; due {r['due_date']}; escalation {r['escalation_status']}."),
      ('Dependency concerns',view['dependencies'],lambda r:r['exposure_days']>0,lambda r:f"{r['upstream_project_id']} → {r['project_id']}: {r['upstream_milestone_id']} needed by {r['downstream_task_id']} on {r['needed_date']}; available {r['available_date']}; {r['exposure_days']} days exposure."),
      ('Overdue actions',view['actions'],lambda r:r['overdue'],lambda r:f"{r['project_id']} {r['title']} — {r['owner']}, due {r['due_date']}.")]
    for title,rows,predicate,format_row in sections:
        text+=f'\n## {title}\n\n';lines=[format_row(r) for r in rows if r['project_id'] in ids and predicate(r)]
        text+=''.join(line(x) for x in lines) or 'None in scope.\n'
    text+='\n## Resource constraints\n\n'
    text+=''.join(line(f"{r['resource_name']}: {r['allocated_hours']} hours allocated / {r['capacity_hours']} capacity. Full-portfolio workload; shared resources are not truncated by filters.") for r in view['resource_capacity'] if r['overload_hours']>0) or 'No overload in the resources used by this scope.\n'
    text+='\n## Decisions required\n\n'
    decisions=[]
    for p in active:
        if p['overall_rag']=='Red':decisions.append(f"{p['sponsor']}: review {p['project_name']} with {p['manager']} and approve an owned recovery/containment action by the next weekly review.")
        if p['health_dimensions']['cost']=='Red':decisions.append(f"{p['sponsor']}: choose cost containment, scope reduction or a formal funding change for {p['project_name']}; no funding approval is assumed.")
    text+=''.join(line(x) for x in decisions) or 'No threshold-triggered decision.\n'
    return text+'\nActions above are rule-derived recommendations, not recorded sponsor approvals.\n'


def exports(data,rules,folder,scenario=False):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    results=history(data,rules);people={p['person_id']:p['person_name'] for p in data['people']};deps={d['department_id']:d['department_name'] for d in data['departments']}
    tables={
      'DimProject':[{**p,'department':deps[p['department_id']],'manager':people[p['manager_id']],'sponsor':people[p['sponsor_id']]} for p in data['projects']],
      'DimPeriod':data['periods'], 'DimResource':data['resources'],
      'DimUpstreamProject':[{'upstream_project_id':p['project_id'],'upstream_project_name':p['project_name']} for p in data['projects']],
      'FactProject':[], 'FactMilestone':[], 'FactRisk':[], 'FactIssue':[], 'FactAction':[], 'FactDependency':[], 'FactAllocation':[], 'FactResource':[], 'FactTask':[],
      'FactCost':data['costs']}
    for result in results:
        for p in result['projects']:
            fields=['project_id','reporting_date','lifecycle','phase','forecast_finish','actual_finish','last_reporting_date','approved_budget','planned_cost','forecast_cost','actual_cost','budget_remaining','actual_vs_planned','actual_vs_planned_pct','forecast_variance','forecast_variance_pct','schedule_variance_days','percentage_complete','overall_rag','open_risks','critical_risks','risk_exposure','open_issues','critical_issues','overdue_actions','overdue_tasks','overdue_milestones','critical_milestones_overdue','milestones_due','dependency_exposure']
            row={k:p[k] for k in fields};row.update({k+'_rag':v for k,v in p['health_dimensions'].items()});tables['FactProject'].append(row)
        for fact,source in [('FactMilestone','milestones'),('FactRisk','risks'),('FactIssue','issues'),('FactAction','actions'),('FactDependency','dependencies'),('FactAllocation','allocations'),('FactResource','resource_capacity'),('FactTask','tasks')]:tables[fact].extend(result[source])
    for name,rows in tables.items():write_csv(folder/(name+'.csv'),rows)
    summary=[summarize(r)['kpis'] for r in results]
    write_csv(folder/'PortfolioKPI.csv',summary)
    (folder/'weekly-report.md').write_text(weekly_report(results[-1],results[-2] if len(results)>1 else None,scenario=scenario),encoding='utf-8')
    (folder/'export-info.json').write_text(json.dumps({'synthetic':True,'scenario':scenario,'reporting_periods':len(results),'tables':{k:len(v) for k,v in tables.items()}},indent=2)+'\n')
    return tables,results
