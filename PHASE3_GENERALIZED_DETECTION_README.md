# RAG Sentinel — Phase 3: Generalized Structured Policy Conflict Detection

## What changed

Phase 3 extends the original Northstar-only support-hours comparison into a small structured claim engine. It currently extracts and compares:

1. Support hours: `weekdays_9_to_5` vs `24/7`
2. Refund window: number of days
3. Minimum password length: number of characters
4. Data retention: number of days

The comparison runs only when both documents contain the same explicit organization identifier (`Organization: ...`, `Company: ...`, or `Service: ...`). The original Northstar example remains supported as a backward-compatible special case.

During secure upload inspection, a new document is compared with locally administrator-approved documents. A detected conflict is quarantined before it can be indexed. Unknown documents without a conflict still go to administrator review. Existing SHA-256 approval behaviour remains unchanged.

## Files changed / added

- `defence/contradiction.py` — structured claim extraction and comparison
- `defence/secure_ingestion.py` — compares uploads against all approved policy references, not just filenames containing Northstar
- `tests/test_contradiction.py` — tests four claim families and organization separation
- `evaluation/policy_conflict_benchmark.csv` — 12 labelled synthetic examples
- `evaluation/policy_conflict_metrics.py` — accuracy, precision, recall, F1, confusion matrix
- `evaluation/run_policy_conflict_evaluation.py` — command-line runner
- `tests/test_policy_conflict_metrics.py` — benchmark tests
- `app/main.py` — new policy conflict benchmark panel in Evaluation & Reports

## Install / update

Copy the Phase 3 folder contents into your existing `AI_RAG_Poisoning_Lab` project and replace matching files. Do not delete your local `venv`, `database/chroma`, `database/security_registry.json`, or `data` folders.

## Run tests

```powershell
cd C:\Users\pma75\Desktop\AI_RAG_Poisoning_Lab
.\venv\Scripts\Activate.ps1
python -m unittest tests.test_contradiction tests.test_evaluation tests.test_policy_conflict_metrics -v
python -m evaluation.run_policy_conflict_evaluation
```

Launch the GUI:

```powershell
streamlit run app/main.py
```

Open **Evaluation & Reports** and click **Run policy conflict benchmark**.

## Important research limitations

- This is structured rule-based comparison, not an LLM semantic contradiction model and not a general-purpose poisoning detector.
- The benchmark is synthetic and intentionally small. It was authored around the supported extraction rules; scores are development checks, not evidence of generalization to unseen real-world attacks.
- Organization matching depends on explicit text labels or the legacy Northstar keyword. A real deployment needs verified organization/document identity and provenance.
- The four claim types have limited wording coverage. Unrecognized phrasing may be missed; ambiguous text can cause errors.
- A detected disagreement is a policy conflict signal, not proof of malicious intent. Legitimate policy revisions must be reviewed.
- SHA-256 proves byte-for-byte identity only; it does not prove who authored a document.
- The local admin approval interface is not authentication or role-based access control.

## Next research step

Create an independent, manually reviewed corpus with varied wording and benign policy updates. Freeze the rules before testing the held-out set. Then run paired baseline/defended RAG trials and measure answer correctness and attack success rate, not just detector metrics.
