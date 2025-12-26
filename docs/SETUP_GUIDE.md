# 🚀 Git Repository Setup Guide

## Step-by-Step Instructions for the IoT Room Selection Project

---

## Prerequisites

Make sure you have:
- [ ] Git installed (`git --version`)
- [ ] GitHub account created
- [ ] SSH key set up (recommended) or HTTPS access

---

## Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name:** `iot-room-selection`
   - **Description:** `IoT Room Selection Decision Support System - BPINFOR-124`
   - **Visibility:** Public (required for free GitHub Pages)
   - ❌ Do NOT initialize with README (we have one)
3. Click **Create repository**

---

## Step 2: Initialize Local Repository

Open terminal in your project folder and run:

```bash
# Navigate to project folder (or create it)
cd /path/to/your/projects
mkdir iot-room-selection
cd iot-room-selection

# Initialize git
git init

# Set your identity (if not already set globally)
git config user.name "Your Name"
git config user.email "your.email@uni.lu"
```

---

## Step 3: Add Project Files

Copy all files from the provided template, then:

```bash
# Check what files are present
ls -la

# You should see:
# - README.md
# - .gitignore
# - docs/
#   - index.html
#   - tasks.json

# Stage all files
git add .

# Verify what will be committed
git status
```

---

## Step 4: First Commit

```bash
git commit -m "Initial commit: Project structure + Gantt chart"
```

---

## Step 5: Connect to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
# Add remote (SSH - recommended)
git remote add origin git@github.com:YOUR_USERNAME/iot-room-selection.git

# OR use HTTPS if SSH isn't set up
git remote add origin https://github.com/YOUR_USERNAME/iot-room-selection.git

# Verify remote
git remote -v
```

---

## Step 6: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

---

## Step 7: Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** (tab at the top)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
5. Click **Save**
6. Wait 1-2 minutes

Your Gantt chart will be live at:
```
https://YOUR_USERNAME.github.io/iot-room-selection/
```

---

## Step 8: Add Collaborators

1. Go to repo **Settings** → **Collaborators**
2. Click **Add people**
3. Enter your teammates' GitHub usernames
4. They'll receive an invite email

---

## Step 9: Teammates Clone the Repo

Your teammates run:

```bash
git clone git@github.com:YOUR_USERNAME/iot-room-selection.git
cd iot-room-selection
```

---

## 📋 Daily Workflow

### Starting work:
```bash
git pull origin main
```

### After completing a task:

1. Edit `docs/tasks.json` - change status from `"todo"` to `"inprogress"` or `"done"`

2. Commit and push:
```bash
git add docs/tasks.json
git commit -m "Update: [Task Name] in progress"
git push origin main
```

3. Refresh the GitHub Pages site to see changes

### Adding new code:
```bash
git add .
git commit -m "feat: Implement [feature name]"
git push origin main
```

---

## ⚠️ Avoiding Conflicts

### Golden Rules:

1. **Always pull before editing:**
   ```bash
   git pull origin main
   ```

2. **Communicate:** Tell teammates when you're editing `tasks.json`

3. **Quick edits:** Edit → Commit → Push immediately

4. **Use GitHub web editor for quick status updates:**
   - Go to `docs/tasks.json` on GitHub
   - Click pencil icon ✏️
   - Edit and commit directly

### If you get a conflict:

```bash
# Pull with rebase
git pull --rebase origin main

# If conflict in tasks.json:
# 1. Open the file
# 2. Look for <<<<<<< and >>>>>>> markers
# 3. Keep the correct version
# 4. Remove the markers
# 5. Then:
git add docs/tasks.json
git rebase --continue
git push origin main
```

---

## 📁 Folder Structure After Setup

```
iot-room-selection/
├── .git/                    # Git internals (don't touch)
├── .gitignore
├── README.md
├── docs/
│   ├── index.html          # Gantt chart (GitHub Pages serves this)
│   └── tasks.json          # Edit this to update tasks!
├── backend/                 # Create when starting backend work
├── frontend/                # Create when starting frontend work
└── database/                # Create when setting up MongoDB
```

---

## 🔗 Quick Reference

| Action | Command |
|--------|---------|
| Check status | `git status` |
| Pull latest | `git pull origin main` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin main` |
| View history | `git log --oneline` |
| Undo last commit (keep files) | `git reset --soft HEAD~1` |

---

## ✅ Setup Checklist

- [ ] Git installed
- [ ] GitHub repo created
- [ ] Local repo initialized
- [ ] Files committed
- [ ] Pushed to GitHub
- [ ] GitHub Pages enabled
- [ ] Collaborators added
- [ ] Teammates cloned repo
- [ ] Everyone can access the Gantt chart URL

---

## 🆘 Need Help?

- Git basics: [git-scm.com/book](https://git-scm.com/book/en/v2)
- GitHub Pages: [docs.github.com/pages](https://docs.github.com/en/pages)
- SSH setup: [docs.github.com/authentication](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
