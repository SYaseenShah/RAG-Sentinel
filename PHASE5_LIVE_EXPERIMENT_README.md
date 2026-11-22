# Phase 5 — Live RAG Attack & Defence Experiments

## Purpose
Runs the actual project RAG functions and configured Ollama model under four conditions: clean-only control, poisoned-only attack, mixed vulnerable retrieval, and mixed defended retrieval. Actual answers, retrieved evidence, source labels and defence decisions are stored in timestamped JSON/CSV files under `evaluation/live_results/`.

## Prerequisites
- Ollama is running and `ollama list` shows `qwen2.5:1.5b`.
- Project dependencies are installed in the existing virtual environment.
- Run commands from the project root.

## Install
Merge this package into your existing project. Preserve `venv`, `database/chroma`, `database/security_registry.json`, and `data`. Do not delete your Chroma database.

## Run
```powershell
python -m unittest tests.test_live_experiment
python -m evaluation.live_experiment
```
The live experiment makes four model calls and may take several minutes.

## GUI
Open **Research Lab** and click **Run complete live experiment**. Inspect the generated answers, retrieved chunks and security decisions; download the JSON/CSV records.

## Interpretation and limitations
Attack success means the generated answer asserted the fabricated 24/7 schedule. Retrieval of a poisoned chunk alone is not success. The answer labeler is a keyword heuristic, not human semantic evaluation. This is one fictional Northstar scenario and one trial per condition; repeat runs and manually verify answers for the final report. Do not generalize these results to arbitrary RAG poisoning. Protected Chat remains on the separate approved-only collection.
