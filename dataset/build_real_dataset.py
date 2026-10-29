import json,ast,re,io,tokenize,pandas as pd,collections,difflib,hashlib
import openpyxl
from openpyxl.styles import Font,PatternFill
from openpyxl.utils import get_column_letter
hdr=['sample_id','group_id','origin','case_type','label','task_description','db_api','n_lines','band','query_style','source','fix_type','code','fixed_code','vulnerable_lines','sink','n_tokens','source_url']
def band(n): return '1-5' if n<=5 else '6-10' if n<=10 else '11-20' if n<=20 else '21-40' if n<=40 else '41-100' if n<=100 else '>100'
def ntok(c):
    try: return sum(1 for t in tokenize.generate_tokens(io.StringIO(c).readline) if t.type not in (tokenize.NL,tokenize.NEWLINE,tokenize.INDENT,tokenize.DEDENT,tokenize.ENDMARKER))
    except Exception: return None
SINK=re.compile(r'((?:\w+(?:\[[^\]]*\])?\.)*(?:execute|executemany|fetchrow|fetchval|fetchall|fetch|query|raw|run_query|exec|executescript|execute_sql|read_sql|read_sql_query))\(')
def db_api(c):
    t=c
    if re.search(r'sqlite',t,re.I): return 'sqlite3'
    if re.search(r'psycopg|asyncpg|\$1|RealDictCursor',t): return 'psycopg2' if 'psycopg' in t else 'other'
    if re.search(r'MySQLdb|mysql|pymysql|dictionary=True',t,re.I): return 'mysql'
    if re.search(r'\bsession\.|sqlalchemy|\btext\(|engine\.|db\.session',t): return 'sqlalchemy'
    if re.search(r'objects\.raw|django|connection\.cursor|\.extra\(',t): return 'django_orm'
    return None
def qstyle(lines):
    t=' '.join(lines)
    if re.search(r'\bf["\']',t): return 'f_string'
    if '.format(' in t: return 'format_method'
    if re.search(r'["\']\s*%\s*[\(\w]',t): return 'percent_format'
    if re.search(r'["\']\s*\+|\+\s*["\']|\+\s*str\(',t): return 'concatenation'
    return 'other'
def source(c):
    if re.search(r'request|\.args|\.form|\.GET|\.POST|cgi\.|FieldStorage|get_argument|self\.get\(',c): return 'web_request'
    if 'os.environ' in c: return 'environment'
    if re.search(r'\bopen\(|sys\.argv|csv\.',c): return 'file'
    return 'function_argument'
def fixtype(before,after):
    b=set(before.splitlines());a=[l for l in after.splitlines() if l not in b]
    added=' '.join(a)
    if re.search(r'\.(filter|query|objects)\b|\.delete\(\)|session\.query',added) : return 'orm_rewrite'
    if re.search(r'(\?|%s|:\w+|\$\d)',added) and re.search(r',\s*\(|,\s*\[|\bparams\b|values=',added): return 'parameterised_query'
    if re.search(r'\bint\(|\bfloat\(',added): return 'type_conversion'
    if re.search(r'\bnot in\b|\bin \(|ALLOWED|allowed|whitelist|\.get\(',added): return 'allow_list'
    return 'other'
def changed(before,after):
    bl=before.splitlines();al=after.splitlines();idx=[]
    for tag,i1,i2,j1,j2 in difflib.SequenceMatcher(None,bl,al).get_opcodes():
        if tag in('replace','delete'): idx+=list(range(i1+1,i2+1))
    return idx
rows=[];seen=set()
def add(group,origin,url,func_before,func_after):
    key=hashlib.md5(func_before.encode()).hexdigest()
    if key in seen: return
    seen.add(key)
    vl=changed(func_before,func_after);bl=func_before.splitlines()
    sink=None
    for i in vl:
        m=SINK.search(bl[i-1])
        if m: sink=m.group(1);break
    if not sink:
        m=SINK.search(func_before);sink=m.group(1) if m else None
    n=len(bl)
    rows.append(dict(group=group,origin=origin,url=url,before=func_before,after=func_after,vl=vl,sink=sink,
        db=db_api(func_before+func_after),qs=qstyle([bl[i-1] for i in vl]) ,src=source(func_before),ft=fixtype(func_before,func_after)))
# SVEN
for fn,split in (('sven89.jsonl','train'),('sven89_val.jsonl','val')):
    for l in open(fn):
        r=json.loads(l)
        sha=r['commit_link'].rstrip('/').split('/')[-1]
        add(sha[:12],f'real, SVEN {split}','https://'+r['commit_link'],r['func_src_before'],r['func_src_after'])
n_sven=len(rows)
# CrossVul (file-level -> changed functions)
def funcs(src):
    t=ast.parse(src);out={}
    lines=src.splitlines()
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min([n.lineno]+[d.lineno for d in n.decorator_list])
            out.setdefault(n.name,'\n'.join(lines[start-1:n.end_lineno]))
    return out
x=pd.read_pickle('py89.pkl');cv=0
for _,r in x.iterrows():
    try: fb,fa=funcs(r.vulnerable_code),funcs(r.fixed_code)
    except SyntaxError: continue
    for name,src in fb.items():
        if name in fa and fa[name]!=src and re.search(r'execute|SELECT|INSERT|UPDATE|DELETE|query',src,re.I) and len(src.splitlines())<=100:
            add('crossvul-'+r.file_pair_id,'real, CrossVul','https://zenodo.org/records/4734050',src,fa[name]);cv+=1
print('sven',n_sven,'crossvul',cv)
# CVEfixes: try function extraction
cf=pd.read_pickle('cf89.pkl');cfn=0
for _,r in cf.iterrows():
    try: fb,fa=funcs(r.vulnerable_code),funcs(r.fixed_code)
    except Exception: continue
    for name,src in fb.items():
        if name in fa and fa[name]!=src:
            add(r.cve_id,'real, CVEfixes',r.repo_url+'/commit/'+r.hash,src,fa[name]);cfn+=1
print('cvefixes funcs',cfn)
out=[];i=0
def mk(i,r,vuln):
    code=r['before'] if vuln else r['after']
    lines=code.splitlines()
    return [f'real_{i:04d}',r['group'],r['origin'],'real_vulnerable' if vuln else 'real_fixed',1 if vuln else 0,None,r['db'],len(lines),band(len(lines)),
        r['qs'] if vuln else None,r['src'] if vuln else None,r['ft'] if vuln else None,code,r['after'] if vuln else None,str(r['vl']) if vuln else '[]',r['sink'],ntok(code),r['url']]
for r in rows:
    out.append(mk(i,r,True));i+=1
    out.append(mk(i,r,False));i+=1
wb=openpyxl.Workbook();ws=wb.active;ws.title='real_rows'
ws.append(hdr)
for o in out: ws.append(o)
for c in ws[1]: c.font=Font(bold=True)
for k,wd in enumerate([11,14,20,16,6,18,12,8,8,16,18,20,70,70,12,18,9,50],1): ws.column_dimensions[get_column_letter(k)].width=wd
ws.freeze_panes='A2'
# highlight blanks
blank=PatternFill('solid',fgColor='FFF2CC')
bl=wb.create_sheet('blank_columns')
bl.append(['column','rows','blank','note'])
for ci,h in enumerate(hdr):
    nb=sum(1 for o in out if o[ci] is None or o[ci]=='')
    bl.append([h,len(out),nb,''])
wb.save('/home/user/ga3/dataset/sqli_real_dataset.xlsx')
print(len(out),'rows');
for ci,h in enumerate(hdr): print(h,sum(1 for o in out if o[ci] is None or o[ci]==''))
print(collections.Counter(o[6] for o in out if o[4]==1),collections.Counter(o[8] for o in out if o[4]==1),collections.Counter(o[9] for o in out if o[4]==1),collections.Counter(o[11] for o in out if o[4]==1))
