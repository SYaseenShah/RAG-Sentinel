# Explicitly approved sources for the Northstar experiment.
# In a real system, this registry must be maintained
# using verified source identities and provenance.

TRUSTED_SOURCES = {
    "northstar_official_policy.txt"
}


def filter_trusted_documents(documents):

    approved = []
    rejected = []
    review = []

    for document in documents:

        source = document.get("source", "")
        analysis = document.get("security_analysis", {})
        decision = analysis.get("decision")

        if decision == "APPROVED" and source in TRUSTED_SOURCES:
            approved.append(document)
        elif decision == "REVIEW REQUIRED":
            review.append(document)
        else:
            rejected.append(document)

    return approved, rejected, review