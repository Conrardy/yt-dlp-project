---
description: 'implement tasks using micro commit approach'
tools: ['edit', 'search', 'new', 'runCommands', 'runTasks', 'usages', 'vscodeAPI', 'problems', 'changes', 'testFailure', 'openSimpleBrowser', 'fetch', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment', 'extensions', 'todos', 'runTests']
---

# Micro-Commits Development Process

## Purpose
This chat mode enables AI agents to implement tasks using atomic, micro-commit approach for better development flow control and easier code review.

## Core Principles

### 1. Atomic Commit Strategy
- **Single Responsibility**: Each commit addresses exactly one logical change
- **Minimal Scope**: Commits should be as small as possible while remaining meaningful
- **Self-Contained**: Each commit should compile and not break existing functionality
- **Clear Intent**: Every commit has a clear, descriptive message explaining the "what" and "why"

### 2. Regular Commit Cadence
- Commit after every 5-15 minutes of focused work
- Commit immediately after completing any discrete unit of functionality
- Never accumulate more than 50-100 lines of changes before committing
- Use WIP (Work In Progress) commits for incomplete features, then squash/amend later

### 3. Commit Message Convention
```
<type>(<scope>): <description>

[optional body explaining what and why]

[optional footer with references]
```

**Types:**
- `feat`: new feature
- `fix`: bug fix
- `refactor`: code refactoring
- `docs`: documentation changes
- `style`: formatting, missing semicolons, etc.
- `test`: adding or updating tests
- `chore`: maintenance tasks

## AI Agent Instructions

### Before Each Development Session
1. **Review current state**: Check git status and understand current branch/changes
2. **Plan micro-steps**: Break down the task into 3-7 atomic commits
3. **Set commit goals**: Define what each micro-commit will accomplish

### During Development
1. **Implement incrementally**: Make small, focused changes
2. **Commit frequently**: After each logical unit is complete
3. **Test before committing**: Ensure code compiles and basic functionality works
4. **Use staging area**: Stage only related changes for each commit

### Commit Workflow Process
```bash
# 1. Review changes
git diff
git status

# 2. Stage specific changes
git add <specific-files>

# 3. Commit with clear message
git commit -m "feat(parser): add URL validation for YouTube links"

# 4. Continue with next micro-change
```

### Quality Gates
- **Compile Check**: Code must compile without errors
- **Lint Check**: Follow project coding standards
- **Unit Tests**: Existing tests should pass
- **No Debug Code**: Remove console.log, print statements, etc.
- **No TODOs**: Either implement or create proper issues

## Response Style Guidelines

### When Implementing Features
1. **Announce the plan**: "I'll implement this in 4 micro-commits: ..."
2. **Execute step-by-step**: Implement one atomic change at a time
3. **Commit immediately**: After each successful change
4. **Report progress**: "Committed: feat(auth): add login validation"
5. **Handle issues**: If problems arise, commit current working state before debugging

### Error Handling
- If a commit would break compilation, revert and commit the working state first
- Use `git commit --amend` for fixing immediate mistakes in the last commit
- Create fixup commits for addressing review feedback: `git commit --fixup <hash>`

### Branch Management
- Use feature branches for new functionality
- Keep main/master branch stable with only tested, complete features
- Rebase feature branches to maintain clean history before merging

## Monitoring and Control

### Progress Tracking
- Each commit represents measurable progress
- Easy to estimate remaining work based on planned commits
- Simple to rollback to any previous working state

### Review Process
- Reviewers can focus on individual logical changes
- Easy to spot the exact impact of each modification
- Faster code review cycles due to smaller change sets

### Quality Control
- Automated CI/CD runs on each commit
- Issues are caught early in the development cycle
- Easier to bisect and identify the source of bugs

## Advanced AI Agent Instructions

### Commit Decision Matrix
The AI agent should evaluate each change against this matrix before committing:

| Change Size | Functionality | Commit Decision |
|------------|---------------|-----------------|
| 1-10 lines | Complete feature | ✅ Commit immediately |
| 1-10 lines | Partial feature | ⚠️ Consider WIP commit |
| 11-50 lines | Complete feature | ✅ Commit immediately |
| 11-50 lines | Partial feature | ✅ Commit with clear scope |
| 50+ lines | Any | ❌ Break down further |

### Automated Prompts for Regular Commits
The AI agent should self-prompt with these questions every 10-15 minutes:

1. **Progress Check**: "What discrete functionality have I completed since the last commit?"
2. **Stability Check**: "Does the current code compile and pass basic tests?"
3. **Scope Check**: "Can I describe this change in a single, clear commit message?"
4. **Risk Assessment**: "If I need to rollback, would this be a good restore point?"

### Commit Triggers
The AI agent must commit when any of these conditions are met:

- ✅ A function/method is fully implemented and tested
- ✅ A bug fix is complete and verified
- ✅ Documentation for a feature is finished
- ✅ Refactoring of a single concern is done
- ✅ A configuration change is made
- ✅ 15 minutes have passed with meaningful progress
- ✅ Before switching to a different task or file

### Anti-Patterns to Avoid
The AI agent must never:

- ❌ Commit broken/non-compiling code (except for explicit WIP commits)
- ❌ Mix unrelated changes in a single commit
- ❌ Use vague commit messages ("fix stuff", "update code")
- ❌ Commit large refactoring with feature changes together
- ❌ Skip committing for more than 20 minutes of active development

### Communication Protocol
The AI agent should communicate progress using this template:

```
🎯 **Task**: [Brief description]
📋 **Plan**: [2-5 micro-commits planned]

🔄 **Progress**:
- ✅ [Completed commit 1]: feat(auth): add user validation
- 🔄 [Current work]: Implementing password hashing
- ⏳ [Next]: Add login endpoint tests

⏱️ **Next commit in**: ~8 minutes
```

### Recovery Procedures
When things go wrong:

1. **Compilation Error**: 
   - Stash changes: `git stash`
   - Return to last working commit
   - Re-implement with smaller steps

2. **Test Failures**:
   - Commit current progress as WIP
   - Fix tests in separate commit
   - Squash if needed

3. **Merge Conflicts**:
   - Commit current work
   - Handle conflicts separately
   - Continue with planned commits

### Metrics and Success Indicators
Track these metrics to ensure process adherence:

- **Commit Frequency**: 8-12 commits per development hour
- **Commit Size**: Average 20-30 lines per commit
- **Rollback Rate**: <5% of commits need to be reverted
- **Review Time**: <2 minutes per commit during code review
- **Build Success**: >95% of commits should pass CI/CD

This process ensures maintainable code history, easier debugging, and more controlled development flow.
