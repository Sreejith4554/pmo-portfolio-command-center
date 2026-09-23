"""Deterministic relational fixtures with coherent weekly project stories."""
import csv
import json
from datetime import date, timedelta
from pathlib import Path

NAMES = ['Cedar Service Standards','Harbor Customer Onboarding','Summit Supplier Portal','Orion Order Integration',
 'Meadow Network Expansion','Atlas Access Controls','River Fulfilment Recovery','Beacon Finance Platform',
 'Willow Knowledge Service','Juniper Reporting Hub','Birch Procurement Refresh','Maple Invoice Controls',
 'Elm Customer Insights','Pine Distribution Readiness','Aspen Commercial Launch','Laurel Closeout',
 'Olive Service Transition','Acacia Operating Model']
DEPARTMENTS = ['Operations','Technology','Supply Chain','Finance','Customer Experience','Transformation','Commercial']
STORIES = ['Stable service rollout','Moderate schedule and cost pressure','Supplier delay with downstream exposure',
 'Integration depends on supplier portal','Forecast funding gap','Unmitigated access-control risk',
 'Recovery after mitigation and replanning','Progressive deterioration across reporting periods',
 'Stable delivery','Overdue governance actions','Supplier uncertainty requiring mitigation','Critical control defect',
 'Healthy insight delivery','Moderate forecast overrun','Commercial readiness dependency','Completed on time',
 'Completed late within approved budget','On hold pending sponsor decision']

def iso(d): return d.isoformat()
def plus(s,days): return iso(date.fromisoformat(s)+timedelta(days=days))

def generate():
    data={k:[] for k in ('departments','people','projects','resources','periods','statuses','milestones','tasks','risks','issues','actions','dependencies','budgets','costs','allocations','assumptions')}
    for i,name in enumerate(DEPARTMENTS,1):data['departments'].append({'department_id':f'D{i}','department_name':name})
    for i in range(1,10):data['people'].append({'person_id':f'PM{i:02}','person_name':f'Demo Coordinator {i:02}','role':'Project Manager / Coordinator'})
    for i in range(1,8):data['people'].append({'person_id':f'SP{i:02}','person_name':f'Demo Sponsor {i:02}','role':'Sponsor'})
    for i in range(1,13):data['resources'].append({'resource_id':f'R{i:02}','resource_name':f'Demo Specialist {i:02}','role':['Analyst','Delivery Lead','Specialist'][i%3],'weekly_capacity_hours':40})
    for w in range(12):data['periods'].append({'reporting_date':iso(date(2026,7,6)+timedelta(weeks=w)),'period_index':w+1,'period_label':f'Week {w+1:02}'})
    for n,name in enumerate(NAMES,1):
        pid=f'P{n:02}';dep=(n-1)%7+1
        finish='2026-08-31' if n==16 else '2026-09-07' if n==17 else '2026-10-05'
        data['projects'].append({'project_id':pid,'project_name':name,'department_id':f'D{dep}','manager_id':f'PM{(n-1)%9+1:02}',
          'sponsor_id':f'SP{dep:02}','priority':['High','Medium','Medium'][n%3],'planned_start':'2026-06-01','planned_finish':finish,'story':STORIES[n-1]})
        previous_actual=0
        for w,period in enumerate(data['periods']):
            day=period['reporting_date'];budget=250000+n*25000+(25000 if n==7 and w>=8 else 0)
            delay={2:7,3:21,4:7,5:0,6:0,10:0,11:7,12:7,14:7,15:7}.get(n,0)
            if n==7:delay=21 if w<6 else 7 if w<11 else 0
            if n==8:delay=max(0,(w-4)*3)
            actual_finish='2026-08-31' if n==16 and day>='2026-08-31' else '2026-09-14' if n==17 and day>='2026-09-14' else ''
            lifecycle='Completed' if actual_finish else 'On Hold' if n==18 and w>=5 else 'Active'
            if n==17:delay=7
            factor={2:.07,3:.10,5:.25,14:.09}.get(n,0)
            if n==7:factor=.20 if w<6 else .10 if w<11 else .02
            if n==8:factor=max(0,(w-4)*.03)
            planned=round(budget*min(.95,.30+.05*w))
            actual=round(planned*(1+max(0,factor)*.5))
            if n==18 and w>=5:actual=round(budget*.50)
            if n in (16,17):
                completion_index=8 if n==16 else 10
                actual=round(budget*min(.99,.3+.69*w/completion_index));planned=actual
            forecast=max(actual,round(budget*(1+factor)))
            if lifecycle=='Completed':forecast=actual
            data['budgets'].append({'project_id':pid,'reporting_date':day,'approved_budget':budget,'planned_cost':planned,'forecast_cost':forecast,'currency':'EUR'})
            data['costs'].append({'cost_id':f'{pid}-C{w+1:02}','project_id':pid,'transaction_date':day,'category':'Synthetic delivery cost','amount':actual-previous_actual})
            previous_actual=actual
            data['statuses'].append({'project_id':pid,'reporting_date':day,'lifecycle':lifecycle,'phase':'Closed' if actual_finish else 'Delivery' if w>=4 else 'Planning',
                'forecast_finish':actual_finish or plus(finish,delay),'actual_finish':actual_finish,'last_reporting_date':'2026-08-03' if n==18 and w>=5 else day})
            for j in range(1,5):
                baseline=['2026-06-29','2026-08-10','2026-09-14' if n in (2,3,4,7,8,11,12,14,15,17) else '2026-09-28',finish][j-1]
                if n in (16,17):baseline=['2026-06-29','2026-07-20','2026-08-10',finish][j-1]
                # First gate is deliberately late for selected projects, with actual evidence.
                mdelay=3 if j==1 and n%4==0 else delay if j>=3 else 0
                forecast_date=plus(baseline,mdelay)
                actual_date=forecast_date if forecast_date<=day else ''
                if j==3 and delay>0 and lifecycle!='Completed':actual_date=''
                if lifecycle=='Completed':actual_date=min(forecast_date,actual_finish)
                data['milestones'].append({'milestone_id':f'{pid}-M{j}','project_id':pid,'reporting_date':day,
                    'milestone_name':['Design approval','Build acceptance','Readiness gate','Release handover'][j-1],
                    'baseline_date':baseline,'forecast_date':actual_date or forecast_date,'actual_date':actual_date,
                    'criticality':'Critical' if j==4 or j==3 and n in (3,4,6,7,8,12) else 'Normal'})
            for j in range(1,13):
                due=plus('2026-06-15',j*9) if n not in (16,17) else plus('2026-06-10',j*6)
                actual_date=plus(due,delay) if plus(due,delay)<=day else ''
                if n==18 and w>=5 and j>5:actual_date=''
                if lifecycle=='Completed':actual_date=min(plus(due,delay),actual_finish)
                data['tasks'].append({'task_id':f'{pid}-T{j:02}','project_id':pid,'reporting_date':day,'task_name':f'Delivery activity {j:02}',
                    'planned_start':plus(due,-10),'due_date':due,'actual_finish':actual_date,'owner_id':f'PM{(n-1)%9+1:02}'})
            for j in (1,2,3):
                probability=4 if (n==6 or n==3) and j==1 else 3 if n==11 and j==1 else 2
                impact=5 if n in (3,6,11) and j==1 else 2
                if n==7 and j==1:probability,impact=(4,5) if w<6 else (2,3)
                if n==8 and j==1:probability,impact=(2,2) if w<5 else (4,5)
                closed=(j==3 and w>=4) or (n==7 and w>=11) or lifecycle=='Completed'
                data['risks'].append({'risk_id':f'{pid}-RK{j}','project_id':pid,'reporting_date':day,
                    'title':['Supplier / control readiness','Review capacity uncertainty','Handover knowledge gap'][j-1],
                    'owner_id':f'PM{(n-1)%9+1:02}','probability':probability,'impact':impact,
                    'status':'Closed' if closed else 'Open','opened_date':'2026-06-15','due_date':'2026-09-14' if probability*impact>=12 else '2026-10-01',
                    'mitigation':'Confirm supplier evidence and mitigation owner' if j==1 else 'Agree review cover and acceptance evidence',
                    'mitigation_status':'Not started' if probability*impact>=20 else 'In progress'})
            for j in (1,2):
                critical=(n==12 or n==8 and w>=7) and j==1
                opened='2026-06-22'
                open_issue=(critical or n in (2,3,8) and j==1) and lifecycle!='Completed'
                data['issues'].append({'issue_id':f'{pid}-I{j}','project_id':pid,'reporting_date':day,'title':'Acceptance defect' if j==1 else 'Review backlog',
                    'owner_id':f'PM{(n-1)%9+1:02}','severity':'Critical' if critical else 'Moderate','status':'Open' if open_issue else 'Resolved',
                    'opened_date':opened,'due_date':'2026-09-14','resolution_date':'2026-06-29' if not open_issue else '', 'required_action':'Agree corrective action and acceptance evidence'})
            for j in (1,2,3):
                overdue=n in (3,6,8,10,12) and (j==1 or n==10)
                done=lifecycle=='Completed' or n==7 and w>=11
                data['actions'].append({'action_id':f'{pid}-A{j}','project_id':pid,'reporting_date':day,'title':['Confirm recovery plan','Review forecast and funding','Close acceptance evidence'][j-1],
                    'owner_id':f'PM{(n-1)%9+1:02}','due_date':'2026-09-14' if overdue else '2026-09-28','status':'Done' if done else 'Open','priority':'High' if j==1 else 'Normal'})
            data['assumptions'].append({'assumption_id':f'{pid}-AS1','project_id':pid,'reporting_date':day,'statement':'Sponsor provides review capacity within the agreed window',
                'owner_id':f'SP{dep:02}','review_date':'2026-09-28','status':'To validate' if n in (3,8,18) else 'Validated'})
            for j in (0,1):
                resource=f'R{((n-1)*2+j)%12+1:02}'
                hours=0 if lifecycle!='Active' else 26 if n in (3,4,8) else 10
                data['allocations'].append({'allocation_id':f'{pid}-{resource}','project_id':pid,'resource_id':resource,'reporting_date':day,'allocated_hours':hours})
    # An edge joins an upstream gate to an actual downstream task, both in the same snapshot.
    for w,p in enumerate(data['periods']):
        for k,(up,down) in enumerate([(3,4),(4,15),(8,14),(1,9),(7,13),(11,10),(2,5)],1):
            data['dependencies'].append({'dependency_id':f'DEP{k:02}','project_id':f'P{down:02}','upstream_project_id':f'P{up:02}',
                'upstream_milestone_id':f'P{up:02}-M{3 if k in (1,2,3,5,6) else 2}','downstream_task_id':f'P{down:02}-T12','reporting_date':p['reporting_date'],
                'owner_id':f'PM{(down-1)%9+1:02}','lag_days':0,'criticality':'Critical' if k in (1,2,3) else 'Normal',
                'required_action':'Agree supplying-project recovery date or downstream contingency'})
    return data


def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: raise ValueError('Cannot infer CSV columns from an empty table')
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def save(root):
    data=generate()
    root=Path(root)
    for name,rows in data.items():write_csv(root/'data'/'raw'/f'{name}.csv',rows)
    (root/'data'/'raw'/'portfolio.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    return data
