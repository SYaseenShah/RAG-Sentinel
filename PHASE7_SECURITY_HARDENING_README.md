# Phase 7 — Security Hardening

## What this phase adds
- First-run administrator setup; the setup screen is disabled after the first account is created.
- PBKDF2-HMAC-SHA256 password hashing with per-user random salts (passwords are never stored in plaintext).
- Three roles: `admin`, `analyst`, and `viewer`.
- Role-based workspace navigation. Only admins can approve staged documents, view quarantine, manage accounts, and inspect audit logs. Analysts can upload/inspect, use the research lab, and run evaluations. Viewers can access the overview and protected chat.
- JSONL audit events for authentication, failed sign-in, logout, upload inspection, document approval, research runs, and evaluation runs.
- Unit tests for password hashing, password policy, duplicate accounts, role checks, and audit logging.

## Install / run
No new third-party dependencies are required.

```powershell
cd C:\Users\pma75\Desktop\AI_RAG_Poisoning_Lab
.\venv\Scripts\Activate.ps1
python -m unittest tests.test_phase7_security
streamlit run app/main.py
```

On first launch, create an administrator. Use a unique password of at least 12 characters containing uppercase, lowercase, and a number. Then sign in.

## Roles
| Capability | Admin | Analyst | Viewer |
|---|---:|---:|---:|
| Security overview | Yes | Yes | Yes |
| Protected Chat | Yes | Yes | Yes |
| Upload / inspect documents | Yes | Yes | No |
| Approve staged documents | Yes | No | No |
| Quarantine Center | Yes | No | No |
| Research Lab / evaluation | Yes | Yes | No |
| Create accounts / view audit | Yes | No | No |

## Files created
- `security/auth.py` — account store, password hashing, authentication and role helpers.
- `security/audit.py` — structured local JSONL audit events.
- `database/users.json` — generated on first account setup; do not commit it.
- `database/audit_log.jsonl` — generated as events occur; do not commit it.
- `tests/test_phase7_security.py` — automated security helper tests.

## Important limitations
This is an academic localhost prototype, not production identity management. Streamlit session state is not a substitute for a hardened identity provider or server-side session controls. The local JSON account store and JSONL audit log are not tamper-proof, have no account lockout/MFA/password reset, and do not provide multi-process transaction guarantees. Do not expose this app to the public internet. For deployment, use HTTPS, a vetted identity provider, MFA, server-side authorization, secret management, database-backed accounts, rate limiting, and centralized append-only audit storage.
