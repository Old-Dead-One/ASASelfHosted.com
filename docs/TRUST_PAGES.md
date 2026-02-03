# Trust Pages — Content and Acceptance Criteria

**Scope:** Design + content specification for /verification and /consent.
**Status:** Required for launch readiness.

---

## Purpose

This doc defines the **required design intent, content structure, and non-negotiable claims** for:

1. **Verification Explained** (/verification)
2. **Consent & Privacy by Design** (/consent)

These pages are trust surfaces and defensive documentation that must accurately reflect how the platform and plugin actually behave.

If a statement on these pages is not enforced by code, it does not ship.

---

## Guiding Principles

1. **Plain-language first** — Assume the reader is technical-curious, not a developer.
2. **Truth over persuasion** — Explain limits and non-capabilities explicitly.
3. **Consent is not implied** — Any data collection must be described as opt-in, explicit, and reversible.
4. **No future promises** — Do not reference planned features, paid tiers, or the agent client.
5. **Verifiability** — A reader should be able to reconcile every claim with the plugin contract, backend behavior, and UI affordances.

---

## Page 1 — Verification Explained

**URL:** `/verification`

**Goal:** Explain what verification means, how it works, and what it does not do, without implying endorsement, ranking bias, or control.

### Required Content Structure

- **Plain-language overview:** What “Verified” means, why verification exists, who controls it (server owner). Verification confirms identity, not quality or playstyle; does not guarantee uptime, population, or moderation; is optional.
- **What verification confirms:** Server identity, map identity, cluster membership (when applicable), heartbeat authenticity (signed payloads). Emphasize proof, not trust.
- **What verification does NOT do (required, visually distinct):** Does not grant featured placement; does not bypass rules or moderation; does not allow remote control; does not collect player data by default; does not affect rankings via payment.
- **How verification works (technical, readable):** Public/private key pairs, signed heartbeats, replay protection, why verification cannot be faked remotely.
- **Relationship to badges & rankings:** Badges are data-driven; verification is a prerequisite for some badges, not all; rankings are not purchasable. No pricing references.

### Explicit Exclusions (Must Not Appear)

- No references to Stripe, “premium placement,” competitors, or roadmap promises.

---

## Page 2 — Consent & Privacy by Design

**URL:** `/consent`

**Goal:** Demonstrate that data collection is impossible without explicit, in-game consent, and that consent is enforceable, revocable, and minimal by design.

### Required Content Structure

- **Plain-language summary:** What data can be collected, when, who must approve. **Required statement (or equivalent):** “If you did not explicitly grant permission in-game, we do not have your data.”
- **Dual-consent model:** Server owner consent controls eligibility; player consent controls personal data; both must agree; if either says no, nothing is collected.
- **In-game authorization:** Consent requires a generated console command; commands are time-limited and must be run in-game; the platform cannot grant consent on a user’s behalf.
- **What data may be collected (with consent):** Aggregate player counts, player session duration (opt-in), optional hashed identifiers (opt-in), public profile display (opt-in). **Never collected:** Chat logs, inventory, tribe data, EOS session data, character saves.
- **Revocation & enforcement:** Consent can be revoked at any time; revocation takes effect immediately; no retroactive or temporary buffering.
- **Explicit non-capabilities (required):** Cannot enable permissions remotely; cannot collect data pending consent; cannot infer consent from UI actions; cannot collect data by default; cannot bypass in-game authorization.

### Relationship to Privacy Policy

- This page explains **how** privacy is enforced; the Privacy Policy explains **legal posture**. Both must agree.

---

## Design & UX Requirements (Both Pages)

- Accessible without authentication
- Linked from footer (and optionally About)
- No dark patterns
- No expandable sections hiding critical info
- Readable on mobile

---

## Acceptance Criteria

Trust pages are **done** when:

- Content matches actual platform behavior
- No claims depend on future work
- Language is plain, accurate, and defensive
- Pages are linked and discoverable
- No contradictions with plugin consent spec, backend enforcement, or UI affordances

---

**Audit:** Use docs/Trust_Claims_Audit.md to verify claims against code.
