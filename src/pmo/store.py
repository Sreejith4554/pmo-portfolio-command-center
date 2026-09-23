"""Saved scenario overlay and audit log, separate from immutable baseline fixtures."""
import copy
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
from .model import load,validate,validate_rules

EDITABLE={
 'budgets':('project_id',{'forecast_cost'}),
 'statuses':('project_id',{'forecast_finish'}),
 'milestones':('milestone_id',{'forecast_date'}),
 'risks':('risk_id',{'probability','impact','status','mitigation_status'}),
 'issues':('issue_id',{'status','resolution_date'}),
 'actions':('action_id',{'status'}),
 'allocations':('allocation_id',{'allocated_hours'})}

class Store:
    def __init__(self,root,state=None):
        self.root=Path(root);self.baseline=load(root)
        self.base_rules=validate_rules(json.loads((self.root/'config/health_rules.json').read_text()))
        directory=Path(state) if state else self.root/'state';directory.mkdir(parents=True,exist_ok=True)
        self.db=directory/'scenarios.sqlite'
        with self.connection() as c:
            c.executescript('CREATE TABLE IF NOT EXISTS edits(table_name TEXT,row_id TEXT,day TEXT,payload TEXT,PRIMARY KEY(table_name,row_id,day)); CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY,payload TEXT); CREATE TABLE IF NOT EXISTS meta(id INTEGER PRIMARY KEY,revision INTEGER); INSERT OR IGNORE INTO meta VALUES(1,0); CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at TEXT,operation TEXT,payload TEXT);')
    @contextmanager
    def connection(self):
        c=sqlite3.connect(self.db,timeout=15);c.row_factory=sqlite3.Row
        try:
            c.execute('BEGIN IMMEDIATE');yield c;c.commit()
        except Exception:c.rollback();raise
        finally:c.close()
    def _read(self,c):
        data=copy.deepcopy(self.baseline);edits=c.execute('SELECT * FROM edits').fetchall()
        for e in edits:
            key=EDITABLE[e['table_name']][0]
            for row in data[e['table_name']]:
                if row[key]==e['row_id'] and row['reporting_date']==e['day']:row.update(json.loads(e['payload']))
        custom=c.execute('SELECT payload FROM config WHERE id=1').fetchone()
        rules=json.loads(custom[0]) if custom else dict(self.base_rules)
        revision=c.execute('SELECT revision FROM meta WHERE id=1').fetchone()[0]
        return data,rules,revision,bool(edits or custom)
    def read(self):
        with self.connection() as c:return self._read(c)
    def change(self,body):
        with self.connection() as c:
            data,rules,revision,_=self._read(c)
            if body.get('revision')!=revision:raise ValueError('Scenario changed in another session; refresh and try again')
            if body.get('operation')=='reset':
                c.execute('DELETE FROM edits');c.execute('DELETE FROM config')
            elif body.get('operation')=='rules':
                rules=validate_rules(body['rules']);c.execute('INSERT OR REPLACE INTO config VALUES(1,?)',(json.dumps(rules),))
            elif body.get('operation')=='edit':
                table=body['table'];key,allowed=EDITABLE.get(table,(None,set()))
                updates=body['updates']
                if not key or not isinstance(updates,dict) or not updates or not set(updates)<=allowed:raise ValueError('Unsupported edit')
                row=next((r for r in data[table] if r[key]==body['row_id'] and r['reporting_date']==body['reporting_date']),None)
                if row is None:raise ValueError('Record not found')
                if table=='milestones' and row['actual_date']:raise ValueError('Completed milestone forecasts are locked in this scenario editor')
                before=copy.deepcopy(row);row.update(updates);validate(data)
                old=c.execute('SELECT payload FROM edits WHERE table_name=? AND row_id=? AND day=?',(table,body['row_id'],body['reporting_date'])).fetchone()
                payload=json.loads(old[0]) if old else {};payload.update(updates)
                c.execute('INSERT OR REPLACE INTO edits VALUES(?,?,?,?)',(table,body['row_id'],body['reporting_date'],json.dumps(payload)))
                body={**body,'before':before,'after':row}
            else:raise ValueError('Unknown operation')
            c.execute('UPDATE meta SET revision=revision+1 WHERE id=1')
            c.execute('INSERT INTO audit(at,operation,payload) VALUES(?,?,?)',(datetime.now(timezone.utc).isoformat(),body['operation'],json.dumps(body)))
            return {'revision':revision+1,'saved':True}
    def audit(self):
        with self.connection() as c:return [dict(r) for r in c.execute('SELECT id,at,operation,payload FROM audit ORDER BY id DESC LIMIT 100')]
