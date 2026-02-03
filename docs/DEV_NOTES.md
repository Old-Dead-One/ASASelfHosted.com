# Development Notes

This file contains development context, decisions, and notes for the ASASelfHosted.com project.

**I will reference this file throughout our work together to maintain context and consistency.**

---

## Current Setup

### Port Configuration
- **Backend**: Running on port `5173`
- **Frontend**: Running on port `3000`
- **API Base URL**: `http://localhost:5173` (configured in frontend `.env`)

### Development Environment
- Backend: FastAPI + Python
- Frontend: Vite + React + TypeScript
- Both servers running successfully ✅
- CORS configured and working ✅

---

## Architecture Decisions

### API-First
- All functionality exposed via REST API
- Frontend is a thin client
- No business logic in React components

### Consent-First
- No data collection without explicit consent
- Consent is time-bound and revocable
- Both server owner AND player must agree where applicable

### Least Privilege
- Supabase RLS policies enforce permissions
- Backend uses service role key sparingly
- Most operations go through RLS, not service role

### Supabase as Source of Truth
- Authentication via Supabase Auth
- Database: Supabase Postgres
- Row Level Security (RLS) mandatory on all tables

---

## Development Workflow

### Before Starting New Features
1. Check this file for relevant context
2. Review `docs/design/PROJECT_STRUCTURE.md` for file organization
3. Follow architectural principles above

### When Making Decisions
- Document significant decisions here
- Note any deviations from original architecture
- Record trade-offs and reasoning

### Git Commit Reminders
**IMPORTANT:** After making large changes or multiple file edits, prompt to commit:
- After completing a major step/feature
- After editing 5+ files
- After implementing a new component/endpoint
- After database schema changes
- At natural stopping points in development

**Commit workflow:**
1. `git add .` - Stage changes
2. `git commit -m "Descriptive message"` - Create local backup
3. `git push` - Upload to GitHub

Always remind to commit after significant work to prevent data loss.

---

## Official Decisions

**See `DECISIONS.md`** for all official decisions (agent vs plugin, database model, subscription timing, cluster model, design direction, payment research, verification model, MVP scope). Do not duplicate them here.

---

## Notes & Context

<!-- Add your development notes below (one-off context, not full decisions) -->

---

## Quick Reference

### Key Files
- **`docs/WORKING_DOCS.md`** — Index of all working docs (start here)
- `DECISIONS.md` — Official decisions (override any doc mismatches)
- `docs/design/PROJECT_STRUCTURE.md` — File and folder structure
- `SPRINT_8_TODO.md` — Single backlog (all open items)
- `FinalCheck.md` — Pre-launch checklist
- `INSTALL.md` — Installation
- `README.md` — Project overview
- `docs/design/1_DESCRIPTION.txt` — Project description
- `docs/design/2_FEATURE_LIST.txt` — Definitive MVP scope
- `docs/design/3_TECH_STACK.txt` — Tech stack
- `docs/design/4_Dev_Plan.txt` — Development plan
- `docs/design/5_Appendix.txt` — Appendix (competitive reference, page architecture)

### Important Principles
1. **API-first**: Backend enforces rules, not UI
2. **Consent-first**: No silent data collection
3. **Least privilege**: RLS is the boss
4. **Supabase as source of truth**: Auth, DB, permissions

---

*Last updated: 2026-02-02*
