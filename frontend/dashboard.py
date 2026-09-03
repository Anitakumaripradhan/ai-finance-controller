import requests
import pandas as pd
import streamlit as st


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="ReconAI",
    page_icon="💰",
    layout="wide"
)


# -----------------------------
# API Configuration
# -----------------------------

API_URL = "http://127.0.0.1:8000"


# -----------------------------
# Load Reconciliation Data
# -----------------------------

@st.cache_data(ttl=10)
def load_reconciliation():

    response = requests.get(
        f"{API_URL}/reconcile",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# -----------------------------
# Load Exception Data
# -----------------------------

@st.cache_data(ttl=10)
def load_exceptions():

    response = requests.get(
        f"{API_URL}/exceptions",
        timeout=10
    )

    response.raise_for_status()

    return response.json()

@st.cache_data(ttl=10)
def load_audit():

    response = requests.get(
        f"{API_URL}/audit",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# -----------------------------
# Header
# -----------------------------

st.title("ReconAI")
st.subheader("AI Finance Controller")

st.write(
    "Automated reconciliation of orders, payments and settlements "
    "with AI-assisted investigation of exceptions."
)


# -----------------------------
# Fetch Data
# -----------------------------

try:

    reconciliation_data = load_reconciliation()
    exception_data = load_exceptions()
    audit_data = load_audit()

    records = reconciliation_data["reconciliation"]
    exceptions = exception_data["exceptions"]
    audit_logs = audit_data["audit_logs"]

except Exception as e:

    st.error(
        "Unable to connect to ReconAI API. "
        "Make sure FastAPI is running."
    )

    st.stop()


# -----------------------------
# Calculate Metrics
# -----------------------------

total_records = len(records)

matched = sum(
    1 for record in records
    if record["status"] == "MATCHED"
)

pending = sum(
    1 for record in records
    if record["status"] == "PENDING"
)

mismatched = sum(
    1 for record in records
    if record["status"] == "MISMATCH"
)


# -----------------------------
# KPI Cards
# -----------------------------

st.markdown("### Reconciliation Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Transactions",
    total_records
)

col2.metric(
    "Matched",
    matched
)

col3.metric(
    "Pending",
    pending
)

col4.metric(
    "Mismatches",
    mismatched
)


st.divider()


# -----------------------------
# Status Distribution
# -----------------------------

st.markdown("### Transaction Status")

status_data = pd.DataFrame(
    {
        "Status": [
            "Matched",
            "Pending",
            "Mismatch"
        ],
        "Transactions": [
            matched,
            pending,
            mismatched
        ]
    }
)

st.bar_chart(
    status_data.set_index("Status")
)


st.divider()


# -----------------------------
# Exception Queue
# -----------------------------

st.markdown("### Exception Queue")

st.write(
    f"{len(exceptions)} transactions require attention."
)


if exceptions:

    exception_table = []

    for item in exceptions:

        exception_table.append(
            {
                "Order ID": item["order_id"],
                "Status": item["status"],
                "Severity": item["severity"],
                "Reason": item["reason_code"],
                "AI Decision": item["ai_decision"],
                "Confidence": f'{item["confidence"] * 100:.0f}%',
                "Discrepancy": (
                    f'₹{item["discrepancy_amount"]:.2f}'
                )
            }
        )

    df = pd.DataFrame(exception_table)

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

else:

    st.success(
        "No exceptions found. All transactions are reconciled."
    )


st.divider()


# -----------------------------
# AI Investigation Details
# -----------------------------

# -----------------------------
# AI Investigation Details
# -----------------------------

st.markdown("### AI Investigation")

if exceptions:

    order_ids = [
        item["order_id"]
        for item in exceptions
    ]

    selected_order = st.selectbox(
        "Select an exception to investigate",
        order_ids
    )

    selected_item = next(
        item
        for item in exceptions
        if item["order_id"] == selected_order
    )

    st.markdown(
        f"#### Investigation: {selected_item['order_id']}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Status",
            selected_item["status"]
        )

    with col2:

        st.metric(
            "Severity",
            selected_item["severity"]
        )

    with col3:

        st.metric(
            "AI Confidence",
            f'{selected_item["confidence"] * 100:.0f}%'
        )

    st.markdown("#### Reconciliation Details")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        st.write(
            f'**Order ID:** {selected_item["order_id"]}'
        )

        st.write(
            f'**Payment ID:** {selected_item["payment_id"]}'
        )

        st.write(
            f'**Settlement ID:** {selected_item["settlement_id"]}'
        )

        st.write(
            f'**Reason Code:** {selected_item["reason_code"]}'
        )

    with detail_col2:

        st.write(
            f'**AI Decision:** {selected_item["ai_decision"]}'
        )

        st.write(
            f'**Discrepancy:** '
            f'₹{selected_item["discrepancy_amount"]:.2f}'
        )

    st.markdown("#### AI Explanation")

    st.info(
        selected_item["explanation"]
    )

else:

    st.success(
        "No exceptions require investigation."
    )
    
# -----------------------------
# Audit Trail
# -----------------------------

st.divider()

st.markdown("### Audit Trail")

if audit_logs:

    audit_table = []

    for log in audit_logs:

        audit_table.append(
            {
                "Time": str(log["created_at"]),
                "Exception ID": log["exception_id"],
                "Action": log["action"],
                "Actor": log["actor"],
                "Details": log["details"]
            }
        )

    audit_df = pd.DataFrame(audit_table)

    st.dataframe(
        audit_df,
        width="stretch",
        hide_index=True
    )

else:

    st.info("No audit events recorded yet.")
    
# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "ReconAI — AI Finance Controller | "
    "Automated reconciliation + AI-assisted exception investigation"
)