
from defence.detector import analyze_document
from defence.filtering import filter_trusted_documents
from defence.contradiction import detect_contradictions


def protect_retrieved_documents(documents):

    analyzed_documents = []

    # First layer: rule-based document analysis.
    for document in documents:

        source = document.get("source", "unknown")

        analysis = analyze_document(
            document["content"],
            source=source
        )

        analyzed_documents.append({
            **document,
            "security_analysis": analysis
        })

    # Second layer: compare claims between documents.
    conflicts = detect_contradictions(analyzed_documents)

    # Update the security analysis of conflicting documents.
    for conflict in conflicts:

        for document in analyzed_documents:

            if document.get("source") == conflict["source"]:

                analysis = document["security_analysis"]

                analysis["findings"].append(
                    "Contradiction detected: "
                    + conflict["reason"]
                )

                analysis["matched_categories"].append(
                    "semantic_contradiction"
                )

                analysis["risk_score"] = min(
                    analysis["risk_score"] + 30,
                    100
                )

                analysis["risk_level"] = (
                    "High"
                    if analysis["risk_score"] >= 50
                    else "Medium"
                )

                analysis["decision"] = "REJECTED"

    # Third layer: apply the trusted-source filtering policy.
    approved, rejected, review = filter_trusted_documents(
        analyzed_documents
    )

    return {
        "approved": approved,
        "rejected": rejected,
        "review": review,
        "analyzed": analyzed_documents,
        "contradictions": conflicts
    }
