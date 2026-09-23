"""Non-destructive repository and analytical-model checks. No proprietary runtime claim."""
import csv,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from pmo.model import load

def main():
 data=load(ROOT)
 schemas=json.loads((ROOT/'powerbi/table-schemas.json').read_text())
 tables={name:list(csv.DictReader((ROOT/'data/processed'/f'{name}.csv').open(encoding='utf-8'))) for name in schemas}
 relations=json.loads((ROOT/'powerbi/relationships.json').read_text())
 for r in relations:
  one=[x[r['one_column']] for x in tables[r['one_table']]];many=[x[r['many_column']] for x in tables[r['many_table']]]
  assert len(one)==len(set(one)),f'Dimension key not unique: {r}'
  assert set(many)<=set(one),f'Orphan analytical relationship: {r}'
  assert r['active'] and r['direction']=='Single'
 for table,definition in schemas.items():
  assert len(tables[table])==definition['rows'];assert set(tables[table][0])=={c['name'] for c in definition['columns']}
  assert (ROOT/'powerbi/queries'/f'{table}.pq').exists()
 dax=(ROOT/'powerbi/measures.dax').read_text()
 for table,column in re.findall(r'\b(\w+)\[([^\]]+)\]',dax):
  assert table in schemas and column in {c['name'] for c in schemas[table]['columns']},(table,column)
 assert len(tables['FactProject'])==216
 latest=[r for r in tables['FactProject'] if r['reporting_date']=='2026-09-21' and r['lifecycle']=='Active']
 assert len(latest)==15 and sum(int(r['forecast_variance']) for r in latest)==304750
 for p in ROOT.rglob('*.md'):
  if any(part in ('node_modules','.venv','output','state') for part in p.parts):continue
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   if '://' not in target and not target.startswith('#'):assert (p.parent/target.split('#')[0]).exists(),(p,target)
 textfiles=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.py','.js','.cjs','.json','.yaml','.yml','.md','.csv','.pq','.dax') and not any(part in ('node_modules','.venv','__pycache__','state','output') for part in p.parts)]
 patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'\bsk-[A-Za-z0-9]{20,}\b',r'\bxox[baprs]-[A-Za-z0-9-]{15,}\b',r'\bAKIA[A-Z0-9]{16}\b',r'\bgh[pousr]_[A-Za-z0-9]{30,}\b']
 for p in textfiles:
  text=p.read_text(encoding='utf-8');assert not any(re.search(pattern,text) for pattern in patterns),f'Potential secret: {p}'
 result={'analytical_tables':len(tables),'relationships_checked':len(relations),'project_period_rows':216,'dax_column_references':'PASS (static only)','relative_links':'PASS','focused_secret_scan':'PASS','source_rows':sum(len(x) for x in data.values())}
 (ROOT/'docs/package-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
