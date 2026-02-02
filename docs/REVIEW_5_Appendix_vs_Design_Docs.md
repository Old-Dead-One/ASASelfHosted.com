# Review: 5_Appendix.txt vs Numbered Design Docs

**Reviewed:** 5_Appendix.txt (Appendix D — Competitive Reference & Page Architecture Rationale) against 1_DESCRIPTION.txt, 2_FEATURE_LIST.txt, 3_TECH_STACK.txt, 4_Dev_Plan.txt.

---

## Summary

The appendix is **consistent** with the other design docs. It validates the single-account model, dashboard-centric UX, server/cluster/player page categories, and trust exclusions (no live player tracking, no paid ranking). A few small gaps and one clarification are noted below.

---

## Alignments

| Appendix section | Design doc | Verdict |
|-----------------|------------|--------|
| **D.2 Single account type** (player + owner, one account) | 4_Dev_Plan: single auth, “Player (Auth)” and “Owner (Auth)” as dashboard sections | ✓ Same model: one account, contextual capabilities. |
| **D.3 Dashboard-centric** (/dashboard, My Servers, Clusters, Favorites, Keys, Consent) | 2_FEATURE_LIST: server owner dashboard, favorites, key generation, cluster management; 4_Dev_Plan: Dashboard (favorites), Owner dashboard (my servers), Agent setup | ✓ Dashboard is the post-login surface; MVP has servers, favorites, agent/keys; consent/keys can expand later. |
| **D.4.1 Server pages** (status, metadata, join paths, verification) | 1_DESCRIPTION, 2_FEATURE_LIST, 4_Dev_Plan: server page, join instructions, password, status, badges | ✓ Matches. |
| **D.4.2 Cluster pages (Phase 1.5+)** | 2_FEATURE_LIST: “Cluster pages” in Phase 1.5; 4_Dev_Plan: “Cluster pages” post-launch | ✓ Aligned. |
| **D.4.3 Player profiles consent-bound** | 2_FEATURE_LIST: “Optional public visibility”, “Player profiles” | ✓ Consent-first, optional visibility. |
| **D.5 Trust pages** (Verification Explained, Consent & Privacy) | 1_DESCRIPTION: trust, transparency; 2_FEATURE_LIST: badges data-driven, no paid placement | ✓ Philosophy aligned; see gap below on timing. |
| **D.6 Exclusions** (no live player tracking, no paid ranking) | 2_FEATURE_LIST: “No paid placement. Ever!”, “Badges are data-driven, not cosmetic purchases” | ✓ Explicitly aligned. |
| **D.7 Page map** (/directory, /server/{id}, /cluster/{id}, /dashboard, /verification, /consent, /docs, /about, /terms, /privacy, /status) | 4_Dev_Plan: Home, Directory, Server details, About, Terms/Privacy; 2_FEATURE_LIST: directory, server page, dashboard | ✓ Structure matches; some routes are MVP, some post-MVP. |

---

## Gaps and clarifications

1. **Trust pages (D.5) vs MVP**  
   Appendix marks “Verification Explained” and “Consent & Privacy by Design” as **required** trust pages. 4_Dev_Plan and 2_FEATURE_LIST don’t list them in MVP scope.  
   **Suggestion:** Either add these two pages to the MVP scope in 4_Dev_Plan (or a “Pre-launch” checklist), or add a line in 5_Appendix that they are required “by launch” rather than “by MVP” so the appendix doesn’t imply they’re in the first shippable slice.

2. **Carousels vs page map**  
   Appendix D.7 doesn’t show carousels (Newbie, Top 100, Hot). 2_FEATURE_LIST defines three homepage carousels.  
   **Clarification:** Carousels are content on `/` (or `/directory`), not separate routes. No change needed in the appendix; optional: add a short note in D.7 that “Home/directory may include carousels (Newbie, Top 100, Hot) as content, not routes.”

3. **Route naming**  
   Appendix uses `/directory/servers` and `/directory/clusters`. Current app uses `/` for home with the server list.  
   **Clarification:** If the product stays with “home = directory list” at `/`, the appendix’s “directory” can be read as the directory *experience* (list + filters), not strictly the path. If you later add `/directory/servers` and `/directory/clusters`, the appendix is already aligned.

4. **/status in D.7**  
   Appendix lists `/status` (likely “platform status” or status page). 4_Dev_Plan doesn’t mention it.  
   **Suggestion:** Either add “Platform status (optional)” to 4_Dev_Plan or note in the appendix that `/status` is optional/post-MVP.

---

## Conclusion

- **1_DESCRIPTION:** No conflicts; appendix supports “discovery, trust, consent, long-term platform” from the description.  
- **2_FEATURE_LIST:** Aligned on directory, server/cluster/player pages, dashboard, badges, carousels, exclusions; trust pages are the only “required vs MVP” nuance.  
- **3_TECH_STACK:** No overlap; appendix is structure/UX, not stack.  
- **4_Dev_Plan:** Aligned on account model, dashboard, server/cluster scope, agent/keys; small gap on required trust pages and optional `/status`.

**Recommendation:** Treat the appendix as valid and adopted. Optionally: (1) add “Verification Explained” and “Consent & Privacy” to a launch checklist or 4_Dev_Plan, and (2) add one sentence in 5_Appendix that carousels live on home/directory as content, not as separate routes. No architectural changes needed.
