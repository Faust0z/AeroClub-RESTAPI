# Financial Model

## Ledger design

Every user receives a **`Balances`** row at registration (initialized to `0`).
A user's balance is a running total derived from a series of **`Transactions`**
(appended to, never modified):

- **Credit (positive):** an admin adds funds via `sum_user_transaction_srv`
  (e.g. `Cash`, `Transfer`, `Check`). `balance.balance += transaction.amount`.
- **Debit (negative):** automatically created when a flight session is
  registered (payment type `"Flight Session"`).
  `balance.balance -= transaction.amount`.

There are **no upper or lower limits** enforced on a balance; overdrafts and
excessive credit are handled via administrative policy rather than software
constraints.

## Flight session billing (atomic)

Registering a flight session (`POST /v1/flight_sessions/`) performs, in a
**single database transaction**:

1. Build the `FlightSessions` record + one or more `Itineraries` (segments).
2. Compute each itinerary cost and sum to `total_session_cost`.
3. Create a debit `Transaction` for that cost bound to the student's balance
   (via `sub_user_transaction_srv`, which **flushes** rather than commits).
4. Link the transaction to the session and issue the final commit.

If any step fails, the whole session + debit are rolled back; no unbilled
flights, and no balance changes without a session. See
[adr/002-financial-transaction-integrity.md](adr/002-financial-transaction-integrity.md).

## Cost algorithm (0.1h / 6-minute increments)

Flight hours are billed in **0.1h blocks (6 minutes)**, per aviation logbook
conventions. For each itinerary the billed hours are computed as:

1. Compute the elapsed time between `departure_time` and `arrival_time` in
   seconds using exact `Decimal` arithmetic.
2. Convert to hours and round up to the nearest `0.1h` block (6 minutes):
   `blocks = ceil(elapsed_seconds / (3600 * 0.1))`, then
   `billed_hours = blocks * 0.1`.
3. `itinerary_cost = billed_hours * plane.fare`, quantized to 2 decimal
   places (`ROUND_HALF_UP`).
4. `total_session_cost = Σ itinerary_cost`.

```python
delta = arrival_time - departure_time
elapsed_seconds = Decimal(delta.days * 86400 + delta.seconds) + Decimal(delta.microseconds) / Decimal(1_000_000)

blocks = (elapsed_seconds / Decimal(3600) / Decimal("0.1")).to_integral_value(rounding=ROUND_CEILING)
billed_hours = blocks * Decimal("0.1")

cost = billed_hours * Decimal(plane.fare)
return cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**Validation:** `departure_time >= arrival_time` raises `BadTimeInput` (400),
and is also rejected at the schema layer.

## Precision handling

All monetary arithmetic in the cost calculation uses Python's
`decimal.Decimal`, which matches the exact `NUMERIC(10, 2)` storage used by the
database. Amounts are only rounded at the final quantization step
(`ROUND_HALF_UP`), so intermediate calculations avoid float drift.

## Financial data model at a glance

```
Planes (fare NUMERIC(10,2)) ──► Itineraries ──► FlightSessions ──► Transactions ──► Balances ──► Users
                                                                    ▲
                                               PaymentTypes (e.g. "Flight Session")
```

- A `Transactions.amount` is signed: positive for credits, negative for debits.
- `FlightSessions.transaction_id` links a session to its generated debit.
- `Itineraries` reference a `plane` (and its `fare`), an `itinerary_type`,
  departure/arrival times, `landings_amount`, and associated `airport_codes`.