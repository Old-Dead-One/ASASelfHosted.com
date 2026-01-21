# Git Repository Setup Guide

**Follow these steps carefully to avoid losing your code.**

## Step-by-Step Instructions

### Step 1: Verify Your Code is Safe
✅ **DO THIS FIRST** - Make sure all your work is saved and you're in the project directory.

### Step 2: Initialize Git (Local Only)
This creates a git repository on your computer. **This does NOT touch GitHub yet.**

### Step 3: Create GitHub Repository (Online)
Create an empty repository on GitHub.com (don't initialize it with README).

### Step 4: Connect Local to GitHub
Link your local repository to the GitHub one.

### Step 5: Push Your Code
Upload your code to GitHub safely.

---

## Important Safety Rules

1. **NEVER run `git reset --hard`** without being 100% sure
2. **NEVER delete `.git` folder** - this is your entire repository history
3. **ALWAYS commit before pushing** - this creates a local backup
4. **Check `.gitignore`** - make sure `.env` files are ignored (they are!)

---

## What Gets Committed

✅ **Safe to commit:**
- All your code files
- Configuration files (package.json, requirements.txt, etc.)
- Documentation files
- Migration SQL files

❌ **NEVER committed (protected by .gitignore):**
- `.env` files (contain secrets!)
- `node_modules/` (can be reinstalled)
- `__pycache__/` (Python cache)
- `.venv/` (Python virtual environment)
- Build outputs (`dist/`, `build/`)

---

## Commit Reminders

**After significant changes, always commit:**
- After completing a major step/feature
- After editing 5+ files
- After implementing new components/endpoints
- After database schema changes
- At natural stopping points

**Quick commit commands:**
```bash
git add .
git commit -m "Description of changes"
git push
```

---

*Follow the steps in order. If you're unsure, stop and ask.*
