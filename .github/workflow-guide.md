# Git Workflow Guide

This document outlines the branching strategy and pull request workflow for this project.

## 🌳 Branch Strategy

### Main Branch
- **Purpose**: Stable, production-ready code
- **Protection**: Should be protected (recommended)
- **Merging**: Only via pull requests from feature branches
- **Status**: Always deployable

### Feature Branches
- **Naming Convention**: `task-1`, `task-2`, `task-3`, etc. for tasks, or `feature-*` for other features
- **Purpose**: Development of specific features or tasks
- **Lifecycle**: Created from `main`, developed independently, merged back via PR
- **Examples**: 
  - `task-1` - Data Collection and Preprocessing
  - `task-2` - Sentiment and Thematic Analysis
  - `feature-dashboard` - New dashboard feature

## 🔄 Workflow Process

### 1. Starting a New Task/Feature

```bash
# Ensure you're on main and it's up to date
git checkout main
git pull origin main

# Create and switch to a new feature branch
git checkout -b task-X

# Or for non-task features
git checkout -b feature-description
```

### 2. Development Workflow

```bash
# Make your changes
# ... edit files ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Descriptive commit message explaining the change"

# Push to remote
git push -u origin task-X
```

**Commit Message Guidelines**:
- Use clear, descriptive messages
- Start with a verb (e.g., "Add", "Fix", "Update", "Refactor")
- Keep first line under 72 characters
- Add detailed description if needed (use `git commit` without `-m`)

### 3. Creating a Pull Request

1. **Push your branch** to remote (if not already done)
   ```bash
   git push origin task-X
   ```

2. **Create PR on GitHub**:
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select `main` as base and `task-X` as compare
   - Fill out the PR template completely

3. **PR Description Requirements**:
   - ✅ **Scope**: What changes were made and why
   - ✅ **Testing**: What tests were run and results
   - ✅ **Impact**: Functional, data, and dependency impacts
   - ✅ **Checklist**: All items completed

### 4. PR Review Process

Even when working solo, treat PRs as review checkpoints:

1. **Self-Review**:
   - Review your own code as if reviewing someone else's
   - Check for:
     - Code quality and style
     - Test coverage
     - Documentation completeness
     - Edge cases handled
     - Performance considerations

2. **Review Checklist**:
   - [ ] Code follows project conventions
   - [ ] All tests pass
   - [ ] No obvious bugs or issues
   - [ ] Documentation is updated
   - [ ] PR description is complete

3. **Address Feedback** (if any):
   ```bash
   # Make additional changes
   git add .
   git commit -m "Address review feedback: ..."
   git push origin task-X
   ```

### 5. Merging the PR

Once the PR is approved and all checks pass:

1. **Merge on GitHub**:
   - Use "Squash and merge" or "Create a merge commit" (recommended: "Squash and merge" for cleaner history)
   - Delete the feature branch after merge (GitHub option)

2. **Update Local Repository**:
   ```bash
   # Switch back to main
   git checkout main
   
   # Pull the merged changes
   git pull origin main
   
   # Delete local feature branch (if merged)
   git branch -d task-X
   ```

## 📝 PR Description Template

Always use the PR template (`.github/pull_request_template.md`) which includes:

### Required Sections:

1. **Scope**
   - What the PR does
   - Related task/issue
   - Key changes
   - Files modified

2. **Testing**
   - Test coverage
   - Test results
   - Verification steps
   - Test data used

3. **Impact Analysis**
   - Functional impact
   - Data impact
   - Dependencies
   - Documentation updates

4. **Checklist**
   - Pre-merge checklist
   - Review checklist

## 🎯 Best Practices

### Branch Management
- ✅ Keep feature branches focused on a single task/feature
- ✅ Keep branches up to date with main (rebase or merge)
- ✅ Delete merged branches (local and remote)
- ✅ Use descriptive branch names

### Commit Practices
- ✅ Make small, logical commits
- ✅ Write clear commit messages
- ✅ Don't commit incomplete work
- ✅ Test before committing

### PR Practices
- ✅ Keep PRs focused and reasonably sized
- ✅ Complete the PR template thoroughly
- ✅ Self-review before requesting review
- ✅ Respond to feedback promptly
- ✅ Keep PRs up to date with main

### Code Quality
- ✅ Follow PEP 8 style guide
- ✅ Write tests for new features
- ✅ Update documentation
- ✅ Add type hints where appropriate
- ✅ Write clear docstrings

## 🔍 Example Workflow

### Example: Task-1 Development

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create task branch
git checkout -b task-1

# 3. Develop and commit
git add src/data_collection/
git commit -m "Add Google Play Store scraper"
git push origin task-1

git add src/data_processing/
git commit -m "Add data preprocessing pipeline"
git push origin task-1

# 4. Create PR on GitHub with complete description
# 5. Self-review and merge
# 6. Clean up
git checkout main
git pull origin main
git branch -d task-1
```

## 🚨 Handling Conflicts

If your feature branch falls behind main:

```bash
# Option 1: Merge main into feature branch
git checkout task-X
git merge main
# Resolve conflicts, then commit
git push origin task-X

# Option 2: Rebase feature branch onto main (cleaner history)
git checkout task-X
git rebase main
# Resolve conflicts, then continue
git rebase --continue
git push origin task-X --force-with-lease
```

## 📚 Additional Resources

- [Git Branching Model](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [GitHub Pull Request Best Practices](https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/)

---

**Remember**: Even when working solo, following this workflow creates:
- ✅ Clear, auditable history
- ✅ Better change isolation
- ✅ Review habits for collaboration
- ✅ Professional development practices

