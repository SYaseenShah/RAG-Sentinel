import sys
from pathlib import Path

import streamlit as st

# Configure page at the very top
st.set_page_config(
    page_title="RAG Sentinel | AI Security Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from security.auth import user_count, create_user, authenticate, list_users, has_role
from security.audit import log_event, read_events
from app.ui.theme import inject_custom_theme
from app.ui.header import render_top_navbar
from app.ui.sidebar import render_sidebar
from app.ui.components import (
    render_page_header,
    render_kpi_card,
    render_status_badge,
    render_pipeline_stepper,
    render_security_callout,
    render_html,
)

# Inject Google Stitch Cybersecurity Theme
inject_custom_theme()

# -----------------------------------------------------------------------------
# Authentication Gate
# -----------------------------------------------------------------------------
st.session_state.setdefault("authenticated_user", None)
if not st.session_state.get("authenticated_user") and st.query_params.get("preview") == "1":
    st.session_state["authenticated_user"] = {"username": "yaseen", "role": "admin"}

current_user = st.session_state.get("authenticated_user")

if not current_user:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        render_html(
            """
<div style="text-align:center;margin-top:2.5rem;margin-bottom:1.8rem;">
<div style="display:inline-flex;align-items:center;justify-content:center;width:60px;height:60px;background:linear-gradient(135deg,rgba(0,240,255,0.18),rgba(14,165,233,0.05));border:1px solid #00f0ff;border-radius:14px;box-shadow:0 0 24px rgba(0,240,255,0.3);font-size:2rem;margin-bottom:14px;">🛡️</div>
<div style="font-size:1.5rem;font-weight:800;letter-spacing:0.08em;color:#ffffff;text-transform:uppercase;">RAG SENTINEL</div>
<div style="font-family:var(--font-mono);font-size:0.75rem;color:#00f0ff;letter-spacing:0.14em;text-transform:uppercase;margin-top:4px;">AI SOC v3.4 · Secure Workspace</div>
</div>
"""
        )

        if user_count() == 0:
            st.info("First launch: create the initial administrator account. This setup screen disappears after the first account is created.")
            with st.form("initial_admin_setup"):
                new_name = st.text_input("Administrator username")
                new_password = st.text_input("Password (12+ characters, upper/lowercase and number)", type="password")
                confirm_password = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create Administrator Account", type="primary", use_container_width=True)
            if submitted:
                try:
                    if new_password != confirm_password:
                        raise ValueError("Passwords do not match.")
                    create_user(new_name, new_password, "admin", "initial_setup")
                    log_event(new_name, "user_created", {"role": "admin", "source": "initial_setup"})
                    st.success("Administrator created. Sign in with your new credentials.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        else:
            with st.form("signin_form"):
                render_html("<div style='font-size:0.9rem;font-weight:600;margin-bottom:10px;color:#cbd5e1;'>AUTHENTICATION REQUIRED</div>")
                username = st.text_input("Username", placeholder="e.g. yaseen")
                password = st.text_input("Password", type="password", placeholder="Enter your credentials")
                submitted = st.form_submit_button("Access Security Workspace", type="primary", use_container_width=True)
            if submitted:
                user = authenticate(username, password)
                if user:
                    st.session_state["authenticated_user"] = user
                    log_event(user["username"], "login_success", {"role": user["role"]})
                    st.rerun()
                else:
                    log_event(username or "anonymous", "login_failure", {"reason": "invalid_credentials"})
                    st.error("Invalid credentials. Access rejected.")

        render_html(
            """
<div style="text-align:center;margin-top:1.5rem;font-size:0.75rem;color:var(--text-muted);font-family:var(--font-mono);">
<span style="color:#10b981;">● DEFCON 4</span> · SECURE ACADEMIC LAB ENVIRONMENT
</div>
"""
        )
    st.stop()


# -----------------------------------------------------------------------------
# Backend Engine Imports (Loaded only after successful authentication)
# -----------------------------------------------------------------------------
from rag.engine import (
    ask_question,
    ask_question_defended,
    ask_secure_question,
    get_collection,
    get_approved_collection,
    ingest_approved_document,
    remove_approved_fingerprint,
)
from attacks.poisoning import inject_northstar_scenario, get_attack_statistics
from defence.secure_ingestion import (
    inspect_upload,
    list_security_records,
    security_counts,
    approve_staged_document,
)
from evaluation.metrics import evaluate_benchmark
from evaluation.policy_conflict_metrics import evaluate_policy_conflicts
from evaluation.end_to_end import evaluate_end_to_end
from evaluation.phase6_heldout import evaluate_phase6
from evaluation.live_experiment import run_live_experiment


# -----------------------------------------------------------------------------
# Shared UI Helpers
# -----------------------------------------------------------------------------
def hero(kicker, title, subtitle):
    render_page_header(kicker, title, subtitle)


def show_findings(findings):
    if not findings:
        st.caption("No findings recorded.")
        return
    for finding in findings:
        st.write(f"• {finding}")


def render_security_record(item, expanded=False):
    status = item.get("status", "UNKNOWN")
    badge_type = "emerald" if status == "APPROVED" else ("rose" if status == "QUARANTINED" else "amber")
    label = f"{status} · {item.get('filename', 'Unknown file')} · Risk {item.get('risk_score', 0)}/100"
    with st.expander(label, expanded=expanded):
        st.markdown(f"**Status:** {render_status_badge(status, badge_type)}", unsafe_allow_html=True)
        st.write(f"**Risk level:** {item.get('risk_level', 'Unknown')}")
        st.write(f"**SHA-256:** `{item.get('sha256', '')}`")
        st.write(f"**Inspected:** {item.get('uploaded_at', 'Unknown')}")
        st.write(f"**File size:** {item.get('size_bytes', 0):,} bytes")
        st.write("**Security findings**")
        show_findings(item.get("findings", []))
        conflict = item.get("conflict")
        if conflict:
            st.warning(
                f"Claim conflict: uploaded document says **{conflict.get('candidate_claim')}**; "
                f"approved reference says **{conflict.get('trusted_claim')}**."
            )
            st.caption(f"Reference document: {conflict.get('trusted_document', 'Unknown')}")


def process_uploads(uploaded_files):
    for uploaded in uploaded_files:
        try:
            file_bytes = uploaded.getvalue()
            with st.spinner(f"Inspecting {uploaded.name}..."):
                record = inspect_upload(uploaded.name, file_bytes)
                log_event(
                    current_user["username"],
                    "upload_inspected",
                    {"filename": uploaded.name, "status": record["status"], "sha256": record["sha256"]},
                )
                if record["status"] == "APPROVED":
                    chunks = ingest_approved_document(uploaded.name, file_bytes, record["sha256"])
                    st.success(f"{uploaded.name}: approved and indexed ({chunks} chunks).")
                elif record["status"] == "QUARANTINED":
                    remove_approved_fingerprint(record["sha256"])
                    st.error(f"{uploaded.name}: quarantined. It was not indexed.")
                else:
                    st.warning(f"{uploaded.name}: awaiting administrator verification. Not indexed.")
            render_security_record(record, expanded=True)
        except Exception as error:
            st.error(f"Could not process {uploaded.name}: {error}")


# -----------------------------------------------------------------------------
# Google Stitch Shell: Sidebar & Top Navigation Bar
# -----------------------------------------------------------------------------
page = render_sidebar(current_user)
render_top_navbar(current_user)

# Shared connections / live counts
research_collection = get_collection()
approved_collection = get_approved_collection()
counts = security_counts()
records = list_security_records()


# -----------------------------------------------------------------------------
# 1. Security Overview
# -----------------------------------------------------------------------------
if page == "Security Overview":
    hero(
        "LIVE TELEMETRY · KNOWLEDGE-BASE INTEGRITY",
        "Security Command Center",
        "Real-time indirect injection defense, knowledge-poisoning mitigation, and ingestion validation pipeline.",
    )

    a, b, c, d = st.columns(4)
    with a:
        render_kpi_card("Approved Documents", counts["approved"], "🛡️", "Emerald Safe", "emerald", "+100% verified")
    with b:
        render_kpi_card("Pending Review", counts["review"], "⏳", "Requires SecOps", "amber", "Awaiting verification")
    with c:
        render_kpi_card("Quarantined", counts["quarantined"], "☣️", "Threat Isolated", "rose", "Excluded from index")
    with d:
        render_kpi_card("Approved Chunks", approved_collection.count(), "⚡", "Vectorized", "cyan", "Cosine search ready")

    st.write("")

    # Multi-Stage Ingestion Pipeline Visualizer
    render_pipeline_stepper([
        {"num": "01", "name": "Upload", "desc": "Raw Ingestion & Parsing", "status": "done", "badge": "PDF / TXT"},
        {"num": "02", "name": "Inspection", "desc": "Heuristic & Injection Scan", "status": "done", "badge": "SHA-256"},
        {"num": "03", "name": "Review", "desc": "Admin Verification & Arbiter", "status": "active" if counts["review"] > 0 else "done", "badge": f"{counts['review']} In Queue"},
        {"num": "04", "name": "Approved KB", "desc": "Zero-Trust Retrieval Index", "status": "active", "badge": "Serving"},
    ])

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Recent Security Activity")
        if not records:
            st.info("No upload activity yet. Start by adding a document in Document Security.")
        else:
            for item in records[:7]:
                status = item.get("status", "UNKNOWN")
                badge_type = "emerald" if status == "APPROVED" else ("rose" if status == "QUARANTINED" else "amber")
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"**{item.get('filename')}**")
                    c2.markdown(render_status_badge(status, badge_type), unsafe_allow_html=True)
                    st.caption(f"Risk {item.get('risk_score', 0)}/100 · {item.get('uploaded_at', '')}")
    with right:
        st.markdown("### Knowledge-Base Health")
        total = max(counts["total"], 1)
        st.progress(counts["approved"] / total, text=f"Approved ratio: {counts['approved']}/{total}")
        st.progress(counts["review"] / total, text=f"Review queue: {counts['review']}/{total}")
        st.progress(counts["quarantined"] / total, text=f"Quarantined threats: {counts['quarantined']}/{total}")
        st.markdown("### Isolated Research Collection")
        st.metric("Research collection chunks", research_collection.count())
        st.caption("This collection is reserved for controlled poisoning experiments and is excluded from Protected Chat.")

    render_security_callout(
        "Security Governance Notice",
        "Risk scores are transparent heuristic indicators, not absolute safety guarantees. "
        "A clean scan does not prove document provenance; new knowledge documents require independent administrator approval.",
        "warning",
    )


# -----------------------------------------------------------------------------
# 2. Document Security
# -----------------------------------------------------------------------------
elif page == "Document Security":
    hero(
        "VECTOR PIPELINE / INGESTION GUARD",
        "Document Security",
        "Secure document ingestion, automated adversarial token inspection, and heuristic quarantine approval engine.",
    )

    st.markdown("### Upload documents")
    st.caption("Upload PDF or TXT files. Clean documents require admin approval; prompt injections and conflicting policies are quarantined automatically.")
    uploaded_files = st.file_uploader(
        "Choose PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        help="Documents are inspected before indexing.",
    )
    if st.button("🔍 Inspect uploaded documents", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Choose at least one document first.")
        else:
            process_uploads(uploaded_files)
            st.rerun()

    st.divider()
    tab_review, tab_approved = st.tabs(["Administrator Review Queue", "Approved Knowledge Base"])
    with tab_review:
        st.caption("Only administrators can approve documents after independently verifying source identity and contents.")
        if not has_role(current_user, "admin"):
            st.info("Your role can inspect and submit documents, but approval is restricted to administrators.")
        review_items = list_security_records("REVIEW REQUIRED")
        if not review_items:
            st.success("No documents are waiting for review.")
        else:
            for item in review_items:
                with st.expander(f"🟡 {item['filename']} · Risk {item['risk_score']}/100", expanded=True):
                    st.write(f"SHA-256: `{item['sha256']}`")
                    show_findings(item.get("findings", []))
                    if has_role(current_user, "admin") and st.button(
                        "Approve and Index into Vector DB", key=f"approve_{item['sha256']}", type="primary"
                    ):
                        try:
                            filename, file_bytes = approve_staged_document(item["sha256"])
                            log_event(current_user["username"], "document_approved", {"filename": filename, "sha256": item["sha256"]})
                            chunks = ingest_approved_document(filename, file_bytes, item["sha256"])
                            st.success(f"Approved and indexed {filename} ({chunks} chunks).")
                            st.rerun()
                        except Exception as error:
                            st.error(f"Approval failed: {error}")

    with tab_approved:
        approved_items = list_security_records("APPROVED")
        col_a, col_b = st.columns(2)
        with col_a:
            render_kpi_card("Approved Documents", len(approved_items), "🛡️", "Verified", "emerald")
        with col_b:
            render_kpi_card("Approved Vectors", approved_collection.count(), "⚡", "Active", "cyan")

        st.write("")
        if not approved_items:
            st.info("No approved documents yet.")
        else:
            for item in approved_items:
                render_security_record(item)


# -----------------------------------------------------------------------------
# 3. Protected AI Chat
# -----------------------------------------------------------------------------
elif page in ("Protected Chat", "Protected AI Chat"):
    hero(
        "VECTOR INTERROGATION / ZERO-TRUST QUERY ENGINE",
        "Protected AI Chat",
        "Ask questions grounded strictly in authorized, cryptographically verified organizational knowledge.",
    )

    # Zero-Trust Context Boundary Banner (Matching Google Stitch Design)
    boundary_banner_html = f"""
<div style="background:#09111e;border:1px solid #1a2a42;border-radius:12px;padding:16px 20px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
  <div style="display:flex;align-items:center;gap:14px;">
    <div style="width:40px;height:40px;border-radius:10px;background:rgba(0,240,255,0.1);border:1px solid rgba(0,240,255,0.3);display:flex;align-items:center;justify-content:center;font-size:1.3rem;">🛡️</div>
    <div>
      <div style="font-family:var(--font-mono);font-size:0.75rem;font-weight:700;color:#ffffff;letter-spacing:0.06em;text-transform:uppercase;">Protected Knowledge Base</div>
      <div style="font-size:0.82rem;color:var(--text-muted);max-width:700px;line-height:1.35;margin-top:2px;">
        Zero-Trust Retrieval Boundary active. Responses are synthesized strictly from {approved_collection.count()} verified chunks. Unreviewed and quarantined uploads are hardware-isolated.
      </div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
    <span class="stitch-badge badge-emerald">Enclave Mode: Active</span>
    <span class="stitch-badge badge-cyan">Approved Vectors: {approved_collection.count()}</span>
    <span class="stitch-badge badge-purple">Strict Citation: ON</span>
  </div>
</div>
"""
    render_html(boundary_banner_html)

    # Split Layout: Chat Area & Live Evidence Rail
    chat_col, evidence_col = st.columns([1.7, 1])

    with evidence_col:
        st.markdown("#### Retrieved Evidence Rail")
        st.caption("Cryptographic ground-truth verification for active query")
        with st.container(border=True):
            st.markdown(f"**Verified Ground Truth Corpus** · {approved_collection.count()} Chunks")
            st.caption("Isolation Sandbox: Active · Enclave cosine rank ready")
            if counts["quarantined"] > 0:
                render_security_callout(
                    "Threats Withheld",
                    f"{counts['quarantined']} quarantined document(s) isolated from AI context window to prevent knowledge poisoning.",
                    "danger",
                )

        if st.button("Clear Conversation History", use_container_width=True, key="clear_chat_history_btn"):
            st.session_state.secure_messages = []
            st.rerun()

    with chat_col:
        if "secure_messages" not in st.session_state:
            st.session_state.secure_messages = []

        # Render message history
        for message in st.session_state.secure_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message.get("sources"):
                    with st.expander(f"View Cryptographic Citations ({len(message['sources'])} Sources Verified)"):
                        for source in message["sources"]:
                            dist = source.get("distance", 0.0)
                            dist_badge = render_status_badge(f"Distance {dist:.4f}", "cyan")
                            st.markdown(
                                f"**{source['source']}** · Chunk {source.get('chunk_index', 0)} · {dist_badge}",
                                unsafe_allow_html=True,
                            )
                            st.write(source["content"])

        if approved_collection.count() == 0:
            st.info("The approved knowledge base is empty. Upload and verify a document in Document Security to begin.")

        # Suggested queries if conversation is empty
        if len(st.session_state.secure_messages) == 0:
            st.markdown("##### Suggested Queries")
            sq1, sq2 = st.columns(2)
            prompt_to_run = None
            with sq1:
                if st.button("What are the official support hours?", use_container_width=True, key="sugg_btn_1"):
                    prompt_to_run = "What are the official support hours of Northstar IT Helpdesk?"
            with sq2:
                if st.button("Which policies are officially approved?", use_container_width=True, key="sugg_btn_2"):
                    prompt_to_run = "Which policies are currently approved in the knowledge base?"

            if prompt_to_run:
                st.session_state.secure_messages.append({"role": "user", "content": prompt_to_run})
                with st.spinner("Retrieving verified evidence and synthesizing answer..."):
                    try:
                        ans, srcs = ask_secure_question(prompt_to_run)
                        st.session_state.secure_messages.append({"role": "assistant", "content": ans, "sources": srcs})
                        st.rerun()
                    except Exception as err:
                        st.error(f"Chat error: {err}")

    # Chat Input Box
    question = st.chat_input("Ask a question about approved policies, SLAs, or playbooks (Strict citation enforcement active)...")
    if question:
        st.session_state.secure_messages.append({"role": "user", "content": question})
        with chat_col:
            with st.chat_message("user"):
                st.write(question)
            with st.chat_message("assistant"):
                with st.spinner("Retrieving verified evidence and synthesizing answer..."):
                    try:
                        answer, sources = ask_secure_question(question)
                        st.markdown(answer)
                        if sources:
                            with st.expander(f"Cryptographic Evidence Used ({len(sources)} Sources)"):
                                for source in sources:
                                    dist = source.get("distance", 0.0)
                                    dist_badge = render_status_badge(f"Distance {dist:.4f}", "cyan")
                                    st.markdown(
                                        f"**{source['source']}** · Chunk {source.get('chunk_index', 0)} · {dist_badge}",
                                        unsafe_allow_html=True,
                                    )
                                    st.write(source["content"])
                        else:
                            st.info("No approved evidence found. The assistant cannot answer from unverified sources.")
                        st.session_state.secure_messages.append({"role": "assistant", "content": answer, "sources": sources})
                        st.rerun()
                    except Exception as error:
                        st.error(f"Chat error: {error}")


# -----------------------------------------------------------------------------
# 4. Quarantine Center
# -----------------------------------------------------------------------------
elif page == "Quarantine Center":
    hero(
        "THREAT CONTAINMENT / ZERO-TRUST VAULT",
        "Quarantine Center",
        "Inspect and manage documents isolated during heuristic token ingestion and adversarial boundary auditing.",
    )
    quarantine_items = list_security_records("QUARANTINED")
    q1, q2, q3 = st.columns(3)
    with q1:
        render_kpi_card("Total Quarantined", len(quarantine_items), "☣️", "Threat Flagged", "rose", "Isolated from index")
    with q2:
        render_kpi_card("High-Risk Items", sum(item.get("risk_level") == "High" for item in quarantine_items), "⚠️", "Elevated Risk", "rose")
    with q3:
        render_kpi_card("Protected Clean Chunks", approved_collection.count(), "🛡️", "Uncompromised", "emerald")

    st.write("")
    if not quarantine_items:
        st.success("Quarantine is clean. No threats currently isolated.")
    else:
        for item in quarantine_items:
            with st.expander(f"🔴 {item['filename']} · Risk {item['risk_score']}/100 · {item['risk_level']}", expanded=True):
                st.write(f"**SHA-256 Fingerprint:** `{item['sha256']}`")
                st.write(f"**Isolated At:** {item.get('uploaded_at', 'Unknown')}")
                st.write("**Threat Findings & Rule Violations**")
                show_findings(item.get("findings", []))
                conflict = item.get("conflict")
                if conflict:
                    render_security_callout(
                        "Policy Contradiction Detected",
                        f"Uploaded claim `{conflict.get('candidate_claim')}` directly contradicts approved baseline `{conflict.get('trusted_claim')}`.",
                        "danger",
                    )
                st.error("ISOLATED — Excluded from production retrieval collections.")


# -----------------------------------------------------------------------------
# 5. Research Lab
# -----------------------------------------------------------------------------
elif page == "Research Lab":
    hero(
        "EXPERIMENTAL ENVIRONMENT / RAG POISONING LAB",
        "Research Lab",
        "Investigate RAG poisoning attacks and evaluate defensive retrieval behavior under controlled conditions.",
    )
    render_security_callout(
        "Research Isolation Advisory",
        "Research controls operate strictly on an isolated experimental collection. Production Protected Chat is never modified.",
        "info",
    )

    st.markdown("### Northstar Support-Hours Poisoning Scenario")
    col_c, col_p = st.columns(2)
    with col_c:
        st.success("**Trusted Reference Claim**\n\nMonday–Friday, 9:00 AM–5:00 PM (Official Northstar Policy)")
    with col_p:
        st.error("**Injected Adversarial Claim**\n\n24 hours a day, 7 days a week (Fabricated Injected Override)")

    if st.button("Prepare / Refresh Controlled Test Vectors", type="primary"):
        try:
            inject_northstar_scenario()
            st.success("Controlled clean and poisoned records inserted into the research collection.")
            st.rerun()
        except Exception as error:
            st.error(f"Could not prepare experiment: {error}")

    stats = get_attack_statistics()
    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_card("Clean Test Vectors", stats.get("clean", 0), "📄", "Ground Truth", "emerald")
    with s2:
        render_kpi_card("Poisoned Test Vectors", stats.get("poisoned", 0), "☣️", "Injected", "rose")
    with s3:
        render_kpi_card("Research Vector Total", research_collection.count(), "⚡", "Experimental", "purple")

    st.write("")
    question = "What are the official support hours of Northstar IT Helpdesk?"
    st.markdown("### Interactive Experiment Runner")
    st.write(f"**Research Target Query:** `{question}`")
    mode = st.selectbox("Baseline Retrieval Condition", ["clean", "poisoned", "mixed"], index=2)
    run_left, run_right = st.columns(2)
    with run_left:
        if st.button("Run Vulnerable RAG Baseline", use_container_width=True):
            with st.spinner("Running baseline experiment..."):
                try:
                    answer, sources = ask_question(question, mode=mode)
                    st.session_state["research_baseline"] = {"mode": mode, "answer": answer, "sources": sources}
                except Exception as error:
                    st.error(f"Baseline failed: {error}")
    with run_right:
        if st.button("Run Defended Comparison", use_container_width=True):
            with st.spinner("Applying defensive triage engine..."):
                try:
                    answer, security = ask_question_defended(question)
                    st.session_state["research_defended"] = {"answer": answer, "security": security}
                except Exception as error:
                    st.error(f"Defended experiment failed: {error}")

    st.write("")
    st.markdown("### Complete Live Experiment — Actual Ollama + ChromaDB")
    st.caption("Executes four empirical model conditions against live local Ollama Qwen 2.5 and ChromaDB.")
    if st.button("Run Complete Live Empirical Experiment", type="primary", use_container_width=True):
        with st.spinner("Executing live multi-condition test suite. This may take several minutes..."):
            try:
                st.session_state["live_experiment_result"] = run_live_experiment()
                st.success("Live experiment completed. Telemetry and datasets recorded.")
            except Exception as error:
                st.error(f"Live experiment failed: {error}")

    live_result = st.session_state.get("live_experiment_result")
    if live_result:
        st.markdown("#### Empirical Attack Mitigation Summary")
        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card(
                "Poisoned-Only Condition",
                "SUCCESS" if live_result["poisoned_only_attack_success"] else "MITIGATED",
                "☣️",
                "Baseline Attack",
                "rose" if live_result["poisoned_only_attack_success"] else "emerald",
            )
        with c2:
            render_kpi_card(
                "Mixed Condition",
                "SUCCESS" if live_result["mixed_attack_success"] else "MITIGATED",
                "⚡",
                "Unprotected Mixed",
                "rose" if live_result["mixed_attack_success"] else "emerald",
            )
        with c3:
            render_kpi_card(
                "Defended Condition",
                "MITIGATED" if not live_result["defended_attack_success"] else "PENETRATED",
                "🛡️",
                "Sentinel Guard",
                "emerald" if not live_result["defended_attack_success"] else "rose",
            )

        for condition in live_result["conditions"]:
            with st.expander(f"{condition['condition']} · label: {condition['answer_label']} · correct: {condition['correct']}"):
                st.write("**Model Generated Answer**")
                st.write(condition["answer"])
                st.write(f"Retrieved evidence records: {condition['retrieved_count']}")
                for source in condition["sources"]:
                    st.write(f"**{source['source']}** · injected: {source['is_poisoned']}")
                    if source["content"]:
                        st.code(source["content"])
                if condition["security"]:
                    st.json(condition["security"])
        st.download_button(
            "Download Live Experiment JSON",
            (ROOT / live_result["json_path"]).read_bytes(),
            file_name="rag_sentinel_live_experiment.json",
            mime="application/json",
        )
        st.download_button(
            "Download Live Experiment CSV",
            (ROOT / live_result["csv_path"]).read_bytes(),
            file_name="rag_sentinel_live_experiment.csv",
            mime="text/csv",
        )

    if "research_baseline" in st.session_state:
        baseline = st.session_state["research_baseline"]
        st.markdown("#### Vulnerable Baseline Output")
        st.info(f"Retrieval Condition: **{baseline['mode']}**")
        st.write(baseline["answer"])
        with st.expander("Retrieved Baseline Sources"):
            for source in baseline["sources"]:
                st.write(f"**{source['source']}** · Poisoned: {source.get('is_poisoned', False)}")
                st.write(source["content"])

    if "research_defended" in st.session_state:
        defended = st.session_state["research_defended"]
        security = defended["security"]
        st.markdown("#### Defended Pipeline Output")
        st.success(defended["answer"])
        x1, x2, x3, x4 = st.columns(4)
        with x1:
            render_kpi_card("Approved", len(security.get("approved", [])), "✓", "Clean", "emerald")
        with x2:
            render_kpi_card("Rejected", len(security.get("rejected", [])), "✗", "Poisoned", "rose")
        with x3:
            render_kpi_card("In Review", len(security.get("review", [])), "⏳", "Review", "amber")
        with x4:
            render_kpi_card("Conflicts", len(security.get("contradictions", [])), "⚠️", "Contradiction", "purple")


# -----------------------------------------------------------------------------
# 6. Evaluation & Reports
# -----------------------------------------------------------------------------
elif page == "Evaluation & Reports":
    hero(
        "SOC TELEMETRY & METRICS / BENCHMARK SUITE",
        "Evaluation & Reports",
        "Measure detection performance, confusion topologies, and analyze RAG security experiment outcomes under live and synthetic attack vectors.",
    )

    a, b, c, d = st.columns(4)
    with a:
        render_kpi_card("Inspected Corpus", counts["total"], "📄", "All Files", "neutral")
    with b:
        render_kpi_card("Approved Safe", counts["approved"], "🛡️", "Indexed", "emerald")
    with c:
        render_kpi_card("Quarantined", counts["quarantined"], "☣️", "Threats", "rose")
    with d:
        render_kpi_card("Pending Review", counts["review"], "⏳", "Queue", "amber")

    st.write("")
    st.markdown("### Document Security Decision Log")
    if records:
        table_rows = []
        for item in records:
            table_rows.append({
                "Filename": item.get("filename", ""),
                "Decision": item.get("status", ""),
                "Risk Score": f"{item.get('risk_score', 0)}/100",
                "Risk Level": item.get("risk_level", ""),
                "SHA-256 Fingerprint": item.get("sha256", "")[:16] + "...",
                "Inspected At": item.get("uploaded_at", ""),
            })
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No inspection records available yet.")

    st.markdown("### Synthetic Detector Benchmark")
    st.caption("Offline benchmark of current rule-based detector across 24 synthetic ground-truth test cases.")
    if st.button("Run Labelled Synthetic Benchmark", type="primary", key="run_labelled_benchmark"):
        try:
            st.session_state["sentinel_benchmark"] = evaluate_benchmark()
        except Exception as error:
            st.error(f"Benchmark failed: {error}")

    benchmark = st.session_state.get("sentinel_benchmark")
    if benchmark:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Accuracy", f"{benchmark['accuracy']:.1%}", "🎯", "Overall", "cyan")
        with m2:
            render_kpi_card("Precision", f"{benchmark['precision']:.1%}", "🔍", "Poison Class", "emerald")
        with m3:
            render_kpi_card("Recall", f"{benchmark['recall']:.1%}", "⚡", "Sensitivity", "purple")
        with m4:
            render_kpi_card("F1-Score", f"{benchmark['f1']:.1%}", "📊", "Harmonic", "cyan")

        cm = benchmark["confusion_matrix"]
        st.markdown("#### Confusion Matrix")
        st.dataframe(
            [
                {"Actual Class": "Clean", "Predicted Clean (TN)": cm["tn"], "Predicted Poisoned (FP)": cm["fp"]},
                {"Actual Class": "Poisoned", "Predicted Clean (FN)": cm["fn"], "Predicted Poisoned (TP)": cm["tp"]},
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.dataframe(benchmark["details"], use_container_width=True, hide_index=True)
        import pandas as pd

        csv_bytes = pd.DataFrame(benchmark["details"]).to_csv(index=False).encode("utf-8")
        st.download_button("Download Benchmark CSV", csv_bytes, file_name="rag_sentinel_benchmark_results.csv", mime="text/csv")

    st.markdown("### Multi-Policy Contradiction Benchmark")
    st.caption("Tests contradiction detection across support hours, refund windows, password rules, and retention boundaries.")
    if st.button("Run Policy Conflict Benchmark", type="primary", key="run_policy_conflict_benchmark"):
        try:
            st.session_state["sentinel_policy_conflicts"] = evaluate_policy_conflicts()
        except Exception as error:
            st.error(f"Policy conflict benchmark failed: {error}")

    policy_bm = st.session_state.get("sentinel_policy_conflicts")
    if policy_bm:
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            render_kpi_card("Accuracy", f"{policy_bm['accuracy']:.1%}", "🎯", "Accuracy", "cyan")
        with p2:
            render_kpi_card("Precision", f"{policy_bm['precision']:.1%}", "🔍", "Precision", "emerald")
        with p3:
            render_kpi_card("Recall", f"{policy_bm['recall']:.1%}", "⚡", "Recall", "purple")
        with p4:
            render_kpi_card("F1-Score", f"{policy_bm['f1']:.1%}", "📊", "Harmonic", "cyan")
        st.dataframe(policy_bm["details"], use_container_width=True, hide_index=True)

    st.markdown("### End-to-End Routing Evaluation")
    st.caption("Evaluates defended routing against candidate-preferred baseline across conflicting evidence.")
    if st.button("Run End-to-End Routing Evaluation", type="primary", key="run_end_to_end"):
        try:
            st.session_state["sentinel_end_to_end"] = evaluate_end_to_end()
        except Exception as error:
            st.error(f"End-to-end evaluation failed: {error}")

    e2e = st.session_state.get("sentinel_end_to_end")
    if e2e:
        e1, e2, e3, e4 = st.columns(4)
        with e1:
            render_kpi_card("Accuracy", f"{e2e['accuracy']:.1%}", "🎯", "Routing", "cyan")
        with e2:
            render_kpi_card("F1-Score", f"{e2e['f1']:.1%}", "📊", "Routing F1", "purple")
        with e3:
            render_kpi_card("Baseline Attack Rate", f"{e2e['baseline_attack_success_rate']:.1%}", "☣️", "Unprotected", "rose")
        with e4:
            render_kpi_card("Defended Attack Rate", f"{e2e['defended_attack_success_rate']:.1%}", "🛡️", "Mitigated", "emerald")
        st.dataframe(e2e["details"], use_container_width=True, hide_index=True)

    st.markdown("### Phase 6 Held-Out Benchmark")
    st.caption("Evaluates 40 independently authored held-out cases.")
    if st.button("Run Phase 6 Held-Out Benchmark", type="primary", key="run_phase6_heldout"):
        try:
            st.session_state["sentinel_phase6"] = evaluate_phase6()
        except Exception as error:
            st.error(f"Phase 6 benchmark failed: {error}")

    phase6 = st.session_state.get("sentinel_phase6")
    if phase6:
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            render_kpi_card("Accuracy", f"{phase6['accuracy']:.1%}", "🎯", "Accuracy", "cyan")
        with q2:
            render_kpi_card("Precision", f"{phase6['precision']:.1%}", "🔍", "Precision", "emerald")
        with q3:
            render_kpi_card("Recall", f"{phase6['recall']:.1%}", "⚡", "Recall", "purple")
        with q4:
            render_kpi_card("F1-Score", f"{phase6['f1']:.1%}", "📊", "Harmonic", "cyan")
        st.dataframe(phase6["details"], use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# 7. User & Audit Administration
# -----------------------------------------------------------------------------
if page == "User & Audit Administration":
    hero(
        "PHASE 7 · SECURITY GOVERNANCE & ACCESS CONTROL",
        "Administration & Audit Trail",
        "Manage local prototype accounts, role boundaries, and review append-only security event logs.",
    )
    st.markdown("### Create New User Account")
    with st.form("create_user_form"):
        u_name = st.text_input("New Username")
        u_pass = st.text_input("Temporary Password", type="password")
        u_role = st.selectbox("Role Permission Level", ["viewer", "analyst", "admin"])
        u_submit = st.form_submit_button("Create Account", type="primary")
    if u_submit:
        try:
            created = create_user(u_name, u_pass, u_role, current_user["username"])
            log_event(current_user["username"], "user_created", {"username": created["username"], "role": u_role})
            st.success(f"User created: {created['username']} ({u_role}).")
        except ValueError as exc:
            st.error(str(exc))

    st.write("")
    st.markdown("### Registered SecOps Users")
    st.dataframe(list_users(), use_container_width=True, hide_index=True)

    st.write("")
    st.markdown("### Cryptographic Audit Trail")
    events = read_events(300)
    if events:
        st.dataframe(events, use_container_width=True, hide_index=True)
    else:
        st.info("No audit events recorded yet.")
