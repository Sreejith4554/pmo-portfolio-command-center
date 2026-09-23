"""Regenerate deterministic raw data, processed star schema, and weekly history."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from pmo.generate import save,write_csv
from pmo.model import validate
from pmo.reporting import exports,weekly_report
from pmo.engine import summarize
if __name__=='__main__':
    data=save(ROOT);validation=validate(data);rules=json.loads((ROOT/'config/health_rules.json').read_text())
    tables,results=exports(data,rules,ROOT/'data/processed')
    for i,r in enumerate(results):
        (ROOT/'data/historical'/f"{r['reporting_date']}.json").write_text(json.dumps(r,indent=2)+'\n')
        (ROOT/'examples'/f"weekly-report-{r['reporting_date']}.md").write_text(weekly_report(r,results[i-1] if i else None),encoding='utf-8')
    kpis=summarize(results[-1])['kpis'];(ROOT/'examples/latest-kpis.json').write_text(json.dumps(kpis,indent=2)+'\n')
    print(json.dumps({'validation':validation,'latest':kpis},indent=2))
