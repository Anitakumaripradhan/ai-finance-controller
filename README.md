# ReconAI — AI Finance Controller

ReconAI is an AI-assisted financial reconciliation system built for the Razorpay Buildathon.

It reconciles orders, payments, and settlements, detects financial exceptions, investigates suspicious cases, and maintains an audit trail for every investigation.

## Problem

Financial reconciliation often requires comparing records from multiple systems.

Manual reconciliation can result in:

- Amount mismatches
- Pending or failed payments
- Missing settlements
- Duplicate transactions
- Unresolved financial exceptions
- Limited visibility into why a transaction was flagged

## Solution

ReconAI automates the reconciliation workflow.

The system:

1. Reads orders, payments, and settlement records.
2. Matches records using deterministic reconciliation rules.
3. Detects mismatches and incomplete settlements.
4. Classifies exceptions by severity and reason.
5. Uses an AI investigation layer to recommend the next action.
6. Maintains an audit trail of investigation events.
7. Displays the results through an interactive dashboard.

## Architecture

```text
Orders
   │
   ├──────────────┐
   │              │
Payments          │
   │              │
   └──────┬───────┘
          │
     Settlements
          │
          ▼
 Reconciliation Engine
          │
     ┌────┴─────┐
     │          │
   MATCHED   EXCEPTION
     │          │
 AUTO-RESOLVE  ▼
          AI Investigation
               │
        ┌──────┴──────┐
        │             │
   FOLLOW_UP    REVIEW_REQUIRED
        │             │
        └──────┬──────┘
               ▼
        Exception Queue
               │
               ▼
          Audit Trail
               │
               ▼
      Streamlit Dashboard