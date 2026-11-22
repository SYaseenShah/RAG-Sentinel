
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.engine import (
    ingest_document,
    ask_question,
    get_collection
)


st.set_page_config(
    page_title="RAG Security Lab",
    page_icon="🛡️",
    layout="wide"
)


# Custom styling
st.markdown("""
<style>

.stApp {
    background-color: #0b1120;
    color: #e2e8f0;
}

section[data-testid="stSidebar"] {
    background-color: #111c30;
}

h1, h2, h3 {
    color: #38bdf8;
}

div[data-testid="stMetric"] {
    background: #142238;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263b55;
}

.stButton > button {
    background: #0891b2;
    color: white;
    border-radius: 8px;
    border: none;
}

</style>
""", unsafe_allow_html=True)


# Sidebar navigation
st.sidebar.title("🛡️ RAG SECURITY LAB")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Knowledge Base",
        "AI Chat"
    ]
)


collection = get_collection()


# Dashboard
if page == "Dashboard":

    st.title("Security Research Dashboard")

    st.caption(
        "RAG Poisoning Attack & Defence Research Platform"
    )

    total_chunks = collection.count()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Indexed Chunks",
        total_chunks
    )

    col2.metric(
        "AI Model",
        "Qwen 2.5"
    )

    col3.metric(
        "Vector Database",
        "ChromaDB"
    )

    st.divider()

    st.subheader("System Overview")

    st.success("RAG engine connected to the vector database.")

    st.info(
        "Attack simulation, defence detection and "
        "security analytics will be added in upcoming modules."
    )


# Knowledge Base
elif page == "Knowledge Base":

    st.title("Knowledge Base Management")

    st.write(
        "Upload PDF or TXT documents to build your RAG knowledge base."
    )

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if st.button("Process Documents"):

        if not uploaded_files:
            st.warning("Please upload at least one document.")

        else:

            for file in uploaded_files:

                try:

                    with st.spinner(
                        f"Processing {file.name}..."
                    ):

                        chunks = ingest_document(
                            file.name,
                            file.getvalue()
                        )

                    st.success(
                        f"{file.name}: {chunks} chunks indexed."
                    )

                except Exception as error:

                    st.error(
                        f"Error processing {file.name}: {error}"
                    )

    st.divider()

    st.subheader("Database Statistics")

    st.metric(
        "Total Indexed Chunks",
        collection.count()
    )


# AI Chat
elif page == "AI Chat":

    st.title("RAG AI Assistant")

    st.caption(
        "Ask questions about your uploaded knowledge base."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("sources"):

                with st.expander("View retrieved sources"):

                    for source in message["sources"]:

                        st.write(
                            f"**{source['source']}** "
                            f"| Chunk {source['chunk_index']}"
                        )

                        st.write(source["content"])

    question = st.chat_input(
        "Ask something about your documents..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):

            with st.spinner("Searching knowledge base..."):

                try:

                    answer, sources = ask_question(question)

                    st.markdown(answer)

                    if sources:

                        with st.expander("Retrieved Sources"):

                            for source in sources:

                                st.write(
                                    f"**{source['source']}** "
                                    f"| Chunk {source['chunk_index']}"
                                )

                                st.write(source["content"])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as error:

                    st.error(f"RAG error: {error}")
