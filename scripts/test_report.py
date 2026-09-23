"""Execute assertions and record reviewable test evidence."""
import json,sys,unittest
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
class Result(unittest.TextTestResult):
 def startTestRun(self):self.records=[]
 def addSuccess(self,test):super().addSuccess(test);self.records.append({'test':test.id(),'expected':'All assertions pass','actual':'PASS'})
 def addFailure(self,test,err):super().addFailure(test,err);self.records.append({'test':test.id(),'expected':'All assertions pass','actual':'FAIL'})
 def addError(self,test,err):super().addError(test,err);self.records.append({'test':test.id(),'expected':'All assertions pass','actual':'ERROR'})
if __name__=='__main__':
 suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'));result=unittest.TextTestRunner(verbosity=1,resultclass=Result).run(suite)
 data={'scope':'Executed Python rules, persistence, export and local HTTP tests','executed_at':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'results':result.records}
 (ROOT/'docs/test-results.json').write_text(json.dumps(data,indent=2)+'\n')
 text='# Executed Python test evidence\n\n'+data['scope']+'\n\nExecuted: '+data['executed_at']+'\n\n| Test | Expected | Actual |\n|---|---|---|\n'+'\n'.join(f'| `{r["test"]}` | {r["expected"]} | {r["actual"]} |' for r in result.records)+'\n'
 (ROOT/'docs/test-results.md').write_text(text)
 sys.exit(not result.wasSuccessful())
