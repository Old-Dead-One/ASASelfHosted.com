# Trust Claims Audit

This table maps public trust claims to the code paths or mechanisms that enforce them.

| Public Claim | Enforcement Mechanism |
|-------------|-----------------------|
| Verification confirms identity, not quality | Signed heartbeats + public key verification |
| Verification cannot be faked remotely | Ed25519 signatures; private key never leaves owner |
| Old heartbeats cannot be reused | Replay protection on heartbeat endpoint |
| Verification does not grant placement | Directory ranking logic ignores payment state |
| Player data is not collected by default | Consent defaults OFF; no implicit collection |
| Both server owner and player must consent | Dual-consent enforcement in plugin + backend |
| Consent requires in-game action | Time-limited console commands executed in-game |
| Platform cannot grant consent | No server-side toggle enables collection |
| Consent revocation is immediate | Local consent files + enforcement on next event |
| No retroactive data collection | No buffering or backfill logic present |
| Certain data is never collected | Plugin contract explicitly excludes categories |

Use this when auditing trust pages (Verification, Consent) against **docs/TRUST_PAGES.md**.
