"""Phase 6 held-out policy-claim benchmark.

The cases are synthetic and independently authored for Phase 6. This evaluates
only the supported structured claim rules in defence.contradiction; it is not
an external/public dataset or a semantic contradiction model.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import csv

from defence.contradiction import compare_policy_claims

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "evaluation" / "phase6_heldout_dataset.csv"
RESULTS_PATH = ROOT / "evaluation" / "phase6_heldout_results.csv"

@dataclass(frozen=True)
class Case:
    case_id: str
    category: str
    reference: str
    candidate: str
    expected_conflict: bool
    note: str


def _make_cases():
    rows = []
    def add(cid, cat, org, ref, cand, conflict, note):
        rows.append(Case(cid, cat, f"Organization: {org}\n{ref}", f"Organization: {org}\n{cand}", conflict, note))
    # Four conflicts and four matching controls for each supported claim type.
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Refunds are processed within 14 days.","Refunds are processed within 30 days."),
        ("Maple Store","Refunds are processed within 7 days.","Refunds are processed within 21 days."),
        ("Orion Market","Refunds are processed within 10 days.","Refunds are processed within 45 days."),
        ("Pine Retail","Refunds are processed within 15 days.","Refunds are processed within 5 days."),
    ],1): add(f"RF-C{i}","refund_window",org,ref,cand,True,"Different explicit refund windows")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Refunds are processed within 14 days.","Refunds are processed within 14 days."),
        ("Maple Store","Refunds are processed within 7 days.","Refunds are processed within 7 days."),
        ("Orion Market","Refunds are processed within 10 days.","Refunds are processed within 10 days."),
        ("Pine Retail","Refunds are processed within 15 days.","Refunds are processed within 15 days."),
    ],1): add(f"RF-M{i}","refund_window",org,ref,cand,False,"Matching explicit refund windows")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Passwords must be at least 12 characters.","Passwords must be at least 8 characters."),
        ("Maple Store","Password minimum of 14 characters.","Password minimum of 10 characters."),
        ("Orion Market","Passwords require minimum 16 characters.","Passwords require minimum 12 characters."),
        ("Pine Retail","Passwords must be at least 10 characters.","Passwords must be at least 6 characters."),
    ],1): add(f"PW-C{i}","password_minimum",org,ref,cand,True,"Different explicit password minimums")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Passwords must be at least 12 characters.","Passwords must be at least 12 characters."),
        ("Maple Store","Password minimum of 14 characters.","Password minimum of 14 characters."),
        ("Orion Market","Passwords require minimum 16 characters.","Passwords require minimum 16 characters."),
        ("Pine Retail","Passwords must be at least 10 characters.","Passwords must be at least 10 characters."),
    ],1): add(f"PW-M{i}","password_minimum",org,ref,cand,False,"Matching explicit password minimums")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Records are retained for 90 days.","Records are retained for 180 days."),
        ("Maple Store","Customer data is stored for 30 days.","Customer data is stored for 60 days."),
        ("Orion Market","We keep records for 365 days.","We keep records for 730 days."),
        ("Pine Retail","Data retention is 45 days.","Data retention is 15 days."),
    ],1): add(f"DR-C{i}","data_retention",org,ref,cand,True,"Different explicit retention periods")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Records are retained for 90 days.","Records are retained for 90 days."),
        ("Maple Store","Customer data is stored for 30 days.","Customer data is stored for 30 days."),
        ("Orion Market","We keep records for 365 days.","We keep records for 365 days."),
        ("Pine Retail","Data retention is 45 days.","Data retention is 45 days."),
    ],1): add(f"DR-M{i}","data_retention",org,ref,cand,False,"Matching explicit retention periods")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Support is available Monday to Friday, 9 AM to 5 PM.","Support is available 24/7."),
        ("Maple Store","Helpdesk operates Monday to Friday, 9:00 AM to 5:00 PM.","Helpdesk is available 24 hours a day."),
        ("Orion Market","Service hours are Monday through Friday, 9 AM–5 PM.","Service is available around the clock."),
        ("Pine Retail","Office hours are Monday to Friday, 9 AM to 5 PM.","Office support is available seven days a week."),
    ],1): add(f"SH-C{i}","support_hours",org,ref,cand,True,"Different explicit support-hour claims")
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","Support is available Monday to Friday, 9 AM to 5 PM.","Support is available Monday to Friday, 9:00 AM to 5:00 PM."),
        ("Maple Store","Helpdesk operates Monday to Friday, 9:00 AM to 5:00 PM.","Helpdesk operates Monday to Friday, 9 AM to 5 PM."),
        ("Orion Market","Office hours Monday to Friday 9 AM to 5 PM.","Office hours Monday to Friday 9:00 AM to 5:00 PM."),
        ("Pine Retail","Service hours Monday to Friday 9 AM to 5 PM.","Service hours Monday to Friday 9 AM to 5 PM."),
    ],1): add(f"SH-M{i}","support_hours",org,ref,cand,False,"Matching explicit support-hour claims")
    # Guard cases: differing organizations must not be compared.
    for i,(reforg,candorg,ref,cand) in enumerate([
        ("Cedar Clinic","Maple Store","Refunds are processed within 14 days.","Refunds are processed within 30 days."),
        ("Orion Market","Pine Retail","Passwords must be at least 12 characters.","Passwords must be at least 8 characters."),
        ("Maple Store","Cedar Clinic","Records are retained for 90 days.","Records are retained for 180 days."),
        ("Pine Retail","Orion Market","Support is available Monday to Friday, 9 AM to 5 PM.","Support is available 24/7."),
    ],1):
        rows.append(Case(f"ORG-G{i}","organization_guard",f"Organization: {reforg}\n{ref}",f"Organization: {candorg}\n{cand}",False,"Different organizations; no comparison expected"))
    # Guard cases: unsupported claim types are deliberately out of scope.
    for i,(org,ref,cand) in enumerate([
        ("Cedar Clinic","The clinic has three branches.","The clinic has five branches."),
        ("Maple Store","The store is located downtown.","The store is located uptown."),
        ("Orion Market","The service uses a blue logo.","The service uses a green logo."),
        ("Pine Retail","The company was founded in 2010.","The company was founded in 2015."),
    ],1): add(f"OUT-G{i}","unsupported_claim",org,ref,cand,False,"Unsupported topic; no structured comparison expected")
    return rows

CASES = _make_cases()

def evaluate_phase6():
    details=[]; tp=fp=tn=fn=0
    for case in CASES:
        conflicts=compare_policy_claims(case.candidate,case.reference,candidate_source=case.case_id,reference_source="phase6_reference")
        predicted=bool(conflicts)
        if case.expected_conflict and predicted: tp+=1
        elif case.expected_conflict and not predicted: fn+=1
        elif not case.expected_conflict and predicted: fp+=1
        else: tn+=1
        details.append({"case_id":case.case_id,"category":case.category,"expected_conflict":case.expected_conflict,"predicted_conflict":predicted,"correct":case.expected_conflict==predicted,"detected_topics":";".join(x["type"] for x in conflicts),"note":case.note})
    total=len(details); accuracy=(tp+tn)/total if total else 0
    precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0
    RESULTS_PATH.parent.mkdir(parents=True,exist_ok=True)
    with RESULTS_PATH.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(details[0]));w.writeheader();w.writerows(details)
    return {"sample_count":total,"positive_count":sum(c.expected_conflict for c in CASES),"accuracy":accuracy,"precision":precision,"recall":recall,"f1":f1,"confusion_matrix":{"tn":tn,"fp":fp,"fn":fn,"tp":tp},"details":details,"results_path":str(RESULTS_PATH.relative_to(ROOT)),"dataset_path":str(DATASET_PATH.relative_to(ROOT))}

if __name__ == "__main__":
    result=evaluate_phase6()
    print({k:v for k,v in result.items() if k!="details"})
