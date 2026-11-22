# RAG Sentinel — Evaluation Module

## Run from project root

```powershell
python -m evaluation.run_evaluation
python -m unittest tests.test_evaluation
```

The benchmark contains 24 synthetic examples (12 clean, 12 poisoned). Labels are manually assigned ground truth for this controlled dataset. The evaluator calls the existing rule-based `analyze_document` function and treats its `REJECTED` decision as a positive poisoning prediction. It uses a registered source name to isolate content-pattern detection from the separate untrusted-source warning.

## Interpretation and limitations

- These metrics describe only this small, hand-authored benchmark and the current detector rules.
- The examples are not an independent public dataset and may overlap conceptually with the patterns used to write the rules.
- Results must not be presented as general RAG-poisoning detection accuracy.
- Expand the dataset, include unseen attack styles and benign edge cases, freeze the rules before testing, and use a held-out set for a stronger evaluation.
- The benchmark evaluates the content detector, not end-to-end LLM attack success, retrieval quality, or the full secure-ingestion workflow.
