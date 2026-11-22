# RAG Sentinel — Phase 2: Research Evaluation

This phase adds a labelled synthetic benchmark and reproducible metric calculation to the Evaluation & Reports page.

## Files added
- `evaluation/benchmark_dataset.csv`: 24 labelled synthetic text samples.
- `evaluation/metrics.py`: accuracy, precision, recall, F1 and confusion-matrix calculation.
- `evaluation/run_evaluation.py`: command-line benchmark runner.
- `tests/test_evaluation.py`: unit tests for dataset and metric outputs.

## Install / run
Use the existing Python 3.11 virtual environment. From the project root:

```powershell
.\venv\Scripts\Activate.ps1
python -m evaluation.run_evaluation
python -m unittest tests.test_evaluation
streamlit run app/main.py
```

Then open **Evaluation & Reports** and click **Run labelled benchmark**.

## Research integrity
The benchmark is deliberately small and synthetic. It is a development baseline only, not evidence of general-purpose poisoning detection. Report the exact dataset size, rule set, and limitations. Do not claim these numbers represent performance on real-world or unseen attacks.
