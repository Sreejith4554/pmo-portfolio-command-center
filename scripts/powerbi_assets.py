"""Generate portable M queries, relationship metadata and real data dictionaries."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'data/processed';schemas={}
for path in sorted(folder.glob('*.csv')):
 if path.stem=='PortfolioKPI':continue
 rows=list(csv.DictReader(path.open(encoding='utf-8')));columns=[]
 for col in rows[0]:
  values=[r[col] for r in rows if r[col]!='']
  if col.endswith('_date') or col in ('planned_start','planned_finish','forecast_finish','actual_finish'):dtype='date'
  else:
   try:
    [int(v) for v in values];dtype='int64' if values else 'text'
   except ValueError:
    try:[float(v) for v in values];dtype='number'
    except ValueError:dtype='text'
  columns.append({'name':col,'type':dtype,'nullable':any(r[col]=='' for r in rows)})
 schemas[path.stem]={'rows':len(rows),'columns':columns}
 types={'date':'type date','int64':'Int64.Type','number':'type number','text':'type text'}
 conversions=',\n        '.join('{"'+c['name']+'", '+types[c['type']]+'}' for c in columns)
 m='''let
    Source = Csv.Document(File.Contents(BaseFolder & "/'''+path.name+'''"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, {
        '''+conversions+'''
    }, "en-US")
in
    Typed
'''
 (ROOT/'powerbi/queries'/f'{path.stem}.pq').write_text(m)
relationships=[]
for name,schema in schemas.items():
 if not name.startswith('Fact'):continue
 cols={c['name'] for c in schema['columns']}
 if 'project_id' in cols:relationships.append({'one_table':'DimProject','one_column':'project_id','many_table':name,'many_column':'project_id','active':True,'direction':'Single'})
 if 'reporting_date' in cols:relationships.append({'one_table':'DimPeriod','one_column':'reporting_date','many_table':name,'many_column':'reporting_date','active':True,'direction':'Single'})
 if 'transaction_date' in cols:relationships.append({'one_table':'DimPeriod','one_column':'reporting_date','many_table':name,'many_column':'transaction_date','active':True,'direction':'Single'})
 if 'resource_id' in cols:relationships.append({'one_table':'DimResource','one_column':'resource_id','many_table':name,'many_column':'resource_id','active':True,'direction':'Single'})
 if 'upstream_project_id' in cols:relationships.append({'one_table':'DimUpstreamProject','one_column':'upstream_project_id','many_table':name,'many_column':'upstream_project_id','active':True,'direction':'Single'})
(ROOT/'powerbi/table-schemas.json').write_text(json.dumps(schemas,indent=2)+'\n')
(ROOT/'powerbi/relationships.json').write_text(json.dumps(relationships,indent=2)+'\n')
with (ROOT/'powerbi/relationships.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(relationships[0]));w.writeheader();w.writerows(relationships)
(ROOT/'powerbi/queries/BaseFolder.pq').write_text('"C:/REPLACE_WITH_PROJECT_FOLDER/data/processed" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
print('Generated',len(schemas),'typed M queries and',len(relationships),'relationships.')
