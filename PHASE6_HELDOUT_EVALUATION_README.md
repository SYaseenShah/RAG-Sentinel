# RAG Sentinel — Phase 6: Independent Held-out Evaluation

## Goal
Phase 6 adds a separately authored, labelled benchmark to evaluate the existing structured policy-claim comparison logic. It does **not** train a new model and does not claim semantic/NLI understanding.

## What is included
- `evaluation/phase6_heldout_dataset.csv`: 40 labelled synthetic cases.
- `evaluation/phase6_heldout.py`: reproducible evaluator and CSV result writer.
- `tests/test_phase6_heldout.py`: unit tests.
- Evaluation & Reports GUI integration with metrics, confusion matrix, details and CSV download.

## Dataset composition
- 8 support-hours cases (4 conflicts, 4 matching controls)
- 8 refund-window cases (4 conflicts, 4 matching controls)
- 8 password-minimum cases (4 conflicts, 4 matching controls)
- 8 data-retention cases (4 conflicts, 4 matching controls)
- 4 different-organization guard cases
- 4 unsupported-topic guard cases

The dataset is independently authored for this phase and is synthetic. It is not a public dataset, not real organizational policy, and not a statistically representative sample of real-world attacks. Keep it separate from the earlier Northstar development example when describing your methodology.

## Install / merge
Extract this ZIP and merge the `AI_RAG_Poisoning_Lab` folder into your existing project. Preserve your existing `venv`, `database/chroma`, `database/security_registry.json`, and `data` folders. Replace `app/main.py` with the included version and add the new evaluation/test files.

## Run
PowerShell:

```powershell
cd C:\Users\pma75\Desktop\AI_RAG_Poisoning_Lab
.\\venv\\Scripts\\Activate.ps1
python -m unittest tests.test_phase6_heldout
python -m evaluation.phase6_heldout
streamlit run app/main.py
```

Then open **Evaluation & Reports** and click **Run Phase 6 held-out benchmark**.

## How to interpret
- A conflict is counted when `compare_policy_claims()` returns one or more supported structured claim differences for the same explicitly named organization.
- A matching policy, a different organization, or an unsupported claim topic should not be reported as a conflict.
- Precision, recall and F1 are calculated over the labelled cases; the confusion matrix is included for transparency.
- Do not tune the detector against these cases and then describe them as an untouched test set. If you change the rules based on these results, create a new, separately labelled test set for the next evaluation.

## Research limitation
The current parser uses regular expressions and a small set of supported claim types. It is not semantic contradiction detection, cannot reliably interpret every paraphrase, and may miss negation, context, exceptions, tables, multilingual content, or complex policies. Report errors rather than hiding them.

## Phase 6 acceptance checklist
- [ ] Unit tests pass.
- [ ] Standalone benchmark runs and writes `evaluation/phase6_heldout_results.csv`.
- [ ] GUI benchmark runs and displays the confusion matrix.
- [ ] Save the resulting CSV with your experiment records.
- [ ] Include dataset provenance and limitations in the final report.
