# ADR 002: Atomic Ledger Updates for Flight Session Billing

**Status:** Accepted
**Date:** See git history
**Area:** Financial Integrity

## Context & Problem Statement

When a flight session is registered, two operations must succeed together:

1. Creating the flight session record with its itinerary (segment) details.
2. Recording a negative financial transaction on the student's balance.

Partial failure would lead to inaccurate account balances or unbilled flight
hours. This coupling is the core integrity guarantee of the system.

## Decision

Creation of a flight session and its associated ledger debit are wrapped in a
**single SQLAlchemy session/transaction**. The debit path
(`sub_user_transaction_srv`) deliberately uses `db.session.flush()` instead of
`db.session.commit()`, so that the transaction and the balance update remain
uncommitted until `create_flight_session_srv` adds the flight session and
issues the final `db.session.commit()`. If anything fails, the whole block is
rolled back:

```python
try:
    new_transaction = sub_user_transaction_srv(email=user.email, transaction=...)
    new_flight_session.transaction_id = new_transaction.id
    db.session.add(new_flight_session)
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

## Consequences

**Pros**

- Guarantees financial data consistency; no "ghost" flight sessions without a
  corresponding billing record, and no balance changes without a session.
- The debit and the session are visible together atomically to other readers.

**Cons / Trade-offs**

- The ordering depends on careful, centralized service-based orchestration;
  a future endpoint that forgets to route through `create_flight_session_srv`
  could bypass the invariant.
- The single shared `db.session` couples flight and ledger concerns, which
  slightly reduces modularity in exchange for integrity.

## Precision Handling

Flight hours are calculated in **0.1h increments (6-minute blocks)**, matching
standard aviation logbook conventions. See
[`docs/financial-model.md`](../financial-model.md) for the exact rounding
algorithm and the decimal-precision caveat.