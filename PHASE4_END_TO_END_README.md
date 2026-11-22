# Phase 4 — End-to-End Security Evaluation

## Goal
Measure whether conflicting candidate policy evidence can change a vulnerable answer route, and whether a defended evidence-routing rule excludes that candidate in favour of an administrator-approved reference.

## Files
- `evaluation/end_to_end_benchmark.csv`: 12 controlled synthetic scenarios (8 conflicts, 4 matching claims).
- `evaluation/end_to_end.py`: evaluation logic and sample-level results.
- `evaluation/run_end_to_end.py`: terminal runner.
- `tests/test_end_to_end.py`: automated tests.

## Run
```powershell
python -m evaluation.run_end_to_end
python -m unittest tests.test_end_to_end
```

## What is measured
- Accuracy, precision, recall, F1 and confusion matrix for detecting policy conflicts.
- Baseline attack success rate: fraction of poisoned cases where the candidate-preferred vulnerable route returns a wrong policy value.
- Defended attack success rate: fraction of poisoned cases where the defended evidence route returns a wrong policy value.

## Critical scope limitation
This is a deterministic, controlled evidence-routing benchmark. It does not execute the actual ChromaDB retrieval, Ollama generation, or Streamlit upload workflow. It is not a live end-to-end LLM attack test and does not establish real-world detection performance. The synthetic samples were authored around the supported regular-expression claim extractors; perfect scores are expected and must not be presented as generalization evidence.

The live application still needs a separate integration test using actual uploaded files, the real approved collection, and Ollama responses. Record the model, prompt, retrieved evidence, answer, and ground-truth result for each run. Do not claim the attack is successful merely because a poisoned chunk was retrieved.
