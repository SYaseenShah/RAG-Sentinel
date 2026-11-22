# RAG Sentinel — Phase 1: Secure Ingestion

## What changed

- The normal chatbot now queries a dedicated Chroma collection named `rag_approved_knowledge`.
- PDF/TXT uploads are inspected before indexing.
- New documents enter `REVIEW REQUIRED`; an administrator must independently verify their source and approve the exact SHA-256 fingerprint.
- Instruction-override patterns and Northstar support-hours conflicts are quarantined.
- Quarantined and review documents are stored outside the approved vector collection.
- The existing Northstar attack simulator remains separate in the research collection for baseline comparisons.

## Run

Activate the existing Python 3.11 virtual environment, then from the project root run:

```powershell
streamlit run app/main.py
```

## First-use workflow

1. Open **Secure Knowledge Base**.
2. Upload one or more PDF/TXT files and click **Inspect and Process Uploads**.
3. New files should normally appear under **Administrator review queue**.
4. Independently verify the document using the source owner / official source outside this app.
5. Click **Approve after manual verification and index** only for a document you have actually verified.
6. Suspicious documents are listed under **Quarantine** and are not indexed.
7. Open **Secure AI Chat** and ask questions. It searches only the approved collection.
8. To demonstrate the Northstar conflict, first approve a genuine Northstar policy with its weekday 9–5 schedule, then upload a different Northstar document claiming 24/7 availability. The second document should be quarantined as a contradiction.

## Important prototype limitations

- The approval control is an administrator workflow for a local classroom demo; it is not protected by authentication or role-based access control.
- SHA-256 proves that a file is identical to a previously approved file; it does not prove who authored the file or whether the original content is true.
- The current contradiction rule is a narrow Northstar support-hours demonstration, not general semantic contradiction detection.
- PDF text extraction does not perform OCR on image-only/scanned PDFs.
- Rule-based indicators can produce false positives and false negatives. Risk scores are heuristic scores, not probabilities.
- The legacy attack simulator intentionally uses a separate research collection. It is not used by the normal secure chatbot.

## Local data

Uploaded documents and the approval registry are stored locally under `data/` and `database/security_registry.json`. These are excluded from Git by `.gitignore`.
