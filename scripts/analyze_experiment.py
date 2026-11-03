#!/usr/bin/env python3
"""Deterministic reanalysis of all frozen attempts and required fields.
Public edition: output moved outside evidence, UTF-8 explicit, checks retained.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
"""
import json,pathlib,statistics,hashlib,copy
from integrity import require
B=pathlib.Path(__file__).resolve().parents[1]; E=B/'evidence';KEYS=['year','month','day','hour']
def schema(obj):
 return isinstance(obj,dict) and set(obj)==set(KEYS) and all(isinstance(obj[k],dict) and set(obj[k])=={'status','value'} and obj[k]['status'] in ['known','ambiguous','unknown'] and ((obj[k]['status']=='known' and isinstance(obj[k]['value'],str) and len(obj[k]['value'])==2) or (obj[k]['status']!='known' and obj[k]['value'] is None)) for k in KEYS)
def validate(obj,ref):return schema(obj) and all(obj[k]==ref[k] for k in KEYS)
def analyze(output_dir):
 output_dir=pathlib.Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
 hashes=json.loads((E/'experiment-frozen-hashes.json').read_text(encoding="utf-8"))
 for name,h in hashes.items():require(hashlib.sha256((E/name).read_bytes()).hexdigest()==h,('frozen input changed',name))
 requests=json.loads((E/'experiment-requests.json').read_text(encoding="utf-8"));raw=[json.loads(x) for x in (E/'experiment-raw.jsonl').read_text(encoding="utf-8").splitlines()]; require(len(raw)==len(requests)==132, "Expected all 132 attempts")
 ids=[r['run_id'] for r in raw];require(len(set(ids))==132 and set(ids)=={r['run_id'] for r in requests}, 'Run identifiers differ from frozen requests')
 frozen={r['run_id']:r for r in requests}
 detail=[]
 for row in raw:
  expected=frozen[row['run_id']]
  for key in ['case_id','family_id','arm','repeat','reference']:require(row[key]==expected[key],('metadata mismatch',row['run_id'],key))
  s=row.get('response',{}).get('message',{}).get('content','');obj=None;parse=True
  try:obj=json.loads(s)
  except Exception:parse=False
  ref=expected['reference'];fields={k:isinstance(obj,dict) and obj.get(k)==ref[k] for k in KEYS}
  detail.append({'run_id':row['run_id'],'case_id':row['case_id'],'family_id':row['family_id'],'arm':row['arm'],'repeat':row['repeat'],'parse':parse,'schema':schema(obj),'exact':validate(obj,ref),'fields':fields,'uncertain_fields':{k:fields[k] for k in KEYS if ref[k]['status']!='known'},'parsed':obj,'reference':ref,'response_status':row['status'],'wall_seconds':row['request_wall_seconds'],'done_reason':row.get('response',{}).get('done_reason')})
 summary={'n_cases':22,'n_repeats':2,'n_calls':132,'n_families':len(set(r['family_id'] for r in raw)),'arms':{}}
 for arm in ['A','B','C']:
  rows=[r for r in detail if r['arm']==arm];casegroups={}
  for r in rows:casegroups.setdefault(r['case_id'],[]).append(r)
  summary['arms'][arm]={'n':len(rows),'parse_pass':sum(r['parse'] for r in rows),'schema_pass':sum(r['schema'] for r in rows),'exact':sum(r['exact'] for r in rows),'fields_correct':sum(sum(r['fields'].values()) for r in rows),'fields_total':4*len(rows),'uncertain_correct':sum(sum(r['uncertain_fields'].values()) for r in rows),'uncertain_total':sum(len(r['uncertain_fields']) for r in rows),'errors':sum(r['response_status']=='error' for r in rows),'truncated':sum(r['done_reason']=='length' for r in rows),'wall_median_seconds':statistics.median(r['wall_seconds'] for r in rows),'wall_min_seconds':min(r['wall_seconds'] for r in rows),'wall_max_seconds':max(r['wall_seconds'] for r in rows),'repeat_exact_object_agreement':sum(v[0]['parsed']==v[1]['parsed'] and v[0]['parsed'] is not None for v in casegroups.values()),'repeat_pairs':len(casegroups)}
 c=[r for r in detail if r['arm']=='C'];passed=sum(r['exact'] for r in c)
 summary['arms']['D']={'n':len(c),'delivered':passed,'abstained':len(c)-passed,'fields_delivered_correct':passed*4,'fields_total':4*len(c),'extra_llm_calls':0,'definition':'exact C output delivered unchanged iff schema and every reference field match'}
 summary['paired_response_differences']={}
 for a,b in [('A','B'),('B','C')]:
  ra={r['case_id']+'_'+str(r['repeat']):r for r in detail if r['arm']==a};rb={r['case_id']+'_'+str(r['repeat']):r for r in detail if r['arm']==b}
  summary['paired_response_differences'][a+'_'+b]={'both_correct':sum(ra[k]['exact'] and rb[k]['exact'] for k in ra),'a_only':sum(ra[k]['exact'] and not rb[k]['exact'] for k in ra),'b_only':sum(not ra[k]['exact'] and rb[k]['exact'] for k in ra),'neither':sum(not ra[k]['exact'] and not rb[k]['exact'] for k in ra)}
 summary['interpretation_limit']='Finite purposive input set; references are implementation-relative. Repeats and boundary neighbors are not independent population samples. No p-values or population confidence intervals.'
 cases={r['case_id']:r['reference'] for r in requests};tests=[]
 for cid,ref in cases.items():
  tests.append({'case_id':cid,'mutation':'none','expected':True,'actual':validate(ref,ref)})
  for k in KEYS:
   x=copy.deepcopy(ref)
   x[k]={'status':'known','value':'甲子' if ref[k].get('value')!='甲子' else '乙丑'}
   tests.append({'case_id':cid,'mutation':k+'_contradiction_or_false_certainty','expected':False,'actual':validate(x,ref)})
  for label,obj in [('empty',{}),('missing_hour',{k:v for k,v in ref.items() if k!='hour'}),('extra_key',ref|{'note':'extra'})]:tests.append({'case_id':cid,'mutation':label,'expected':False,'actual':validate(obj,ref)})
 summary['fault_injection']={'positive':22,'negative':len(tests)-22,'total':len(tests),'passed':sum(t['expected']==t['actual'] for t in tests),'scope':'exact finite-field gate only, not free-text semantics or oracle correctness'}
 for file,obj in [('experiment-scored.json',detail),('experiment-summary.json',summary),('validator-fault-injection.json',tests)]: (output_dir/file).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
 return summary
if __name__=='__main__':
 raise SystemExit('Run scripts/reproduce.py so evidence integrity is verified first.')
