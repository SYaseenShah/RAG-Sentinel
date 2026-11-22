# RAG Sentinel GUI update

The updated `app/main.py` provides a consolidated Streamlit interface with:

- Security Overview dashboard and live document-state counters
- Secure Document Ingestion with multi-file PDF/TXT upload
- Administrator review queue and approved knowledge-base view
- Protected Chat using the approved-only Chroma collection
- Dedicated Quarantine Center
- Separate controlled Northstar Research Lab
- Evaluation & Reports page with a document decision log and research checklist

## Run

Activate your existing Python 3.11 virtual environment and run from the project root:

```powershell
streamlit run app/main.py
```

The update does not include the virtual environment or local Chroma/security-registry data. Keep your existing local `venv/`, `database/chroma/`, `database/security_registry.json`, and `data/` folders when replacing source files.

## Validation performed

- Python syntax compilation passed for `app/main.py`.
- `python -m tests.test_contradiction` passed.
- The Streamlit application was not launched in this build environment; run it locally to validate package versions, Ollama connectivity, and browser rendering.

## Completion status

The GUI and core controlled workflow are a strong working prototype, but the academic project is not complete until the full workflow is tested on the target PC, a labelled evaluation set is created, metrics are calculated, and the report/presentation/demo are prepared.
