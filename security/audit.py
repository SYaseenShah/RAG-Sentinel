"""Append-only JSONL audit trail for this local academic prototype."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT_PATH=ROOT/'database'/'audit_log.jsonl'
ALLOWED_EVENTS={'login_success','login_failure','logout','user_created','upload_inspected','document_approved','research_experiment','evaluation_run','access_denied'}

def log_event(actor, event, details=None):
    if event not in ALLOWED_EVENTS: raise ValueError('Unsupported audit event.')
    AUDIT_PATH.parent.mkdir(parents=True,exist_ok=True)
    row={'timestamp':datetime.now(timezone.utc).isoformat(),'actor':(actor or 'anonymous')[:80],'event':event,'details':details or {}}
    # Avoid storing passwords, document contents, or secrets in audit details.
    forbidden={'password','content','secret','token'}
    if forbidden.intersection(str(k).lower() for k in row['details']): raise ValueError('Sensitive fields cannot be written to the audit log.')
    with AUDIT_PATH.open('a',encoding='utf-8') as f: f.write(json.dumps(row,ensure_ascii=False)+'\n')
    return row

def read_events(limit=200):
    if not AUDIT_PATH.exists(): return []
    rows=[]
    for line in AUDIT_PATH.read_text(encoding='utf-8').splitlines()[-max(1,min(int(limit),1000)):]:
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: continue
    return list(reversed(rows))
