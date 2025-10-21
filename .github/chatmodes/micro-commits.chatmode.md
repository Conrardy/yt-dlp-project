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
- ✅ A task item in todos.md is completed

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

### Task Tracking Integration

#### Todos.md Update Process
The AI agent must update `.current/todos.md` as part of the commit workflow:

1. **Before Each Development Session**:
   - Review current todos.md to understand active tasks
   - Identify which tasks will be worked on
   - Plan micro-commits aligned with task items

2. **During Development**:
   - Track progress on specific todo items
   - Mark sub-tasks as completed when functionality is working
   - Update task status in real-time

3. **Task Completion Workflow**:
   ```bash
   # 1. Complete the functionality
   git add <implementation-files>
   git commit -m "feat(config): implement default configuration class"
   
   # 2. Update todos.md immediately after
   # Change: - [ ] Task description
   # To:     - [x] Task description
   git add .current/todos.md
   git commit -m "docs(todos): mark configuration class task as completed"
   ```

4. **Todo Update Rules**:
   - ✅ Mark task as `[x]` only when fully implemented and tested
   - 🔄 Add progress notes for partial completion: `- [ ] Task (⚠️ 60% complete)`
   - 📝 Move completed tasks to "✅ Tâches Complétées" section weekly
   - 🆕 Add new discovered sub-tasks during implementation
   - 🔄 Update task descriptions if scope changes during development

#### Task-Commit Mapping
Each commit should reference related todo items:

```
feat(downloader): implement basic audio download functionality

- Completes: "Créer la classe AudioDownloader"
- Progress on: "Implémenter la méthode de téléchargement avec YT-DLP"
- Related: todos.md line 23-25
- Refs: TODO-2.1, TODO-2.2
```

#### Progress Tracking Template
```
🎯 **Current Todo Section**: [Section name from todos.md]
📋 **Active Tasks**: 
   - [ ] Task 1 (🔄 in progress)
   - [x] Task 2 (✅ completed this session)
   - [ ] Task 3 (⏳ next)

🔄 **Commits This Session**:
- ✅ feat(config): add default settings - completes TODO-1.1
- ✅ docs(todos): update task status - maintenance
- 🔄 [Current work]: Implementing URL validation

⏱️ **Next todo update**: After current function completion
```

### Recovery Procedures
When things go wrong:

1. **Compilation Error**: 
   - Stash changes: `git stash`
   - Return to last working commit
   - Re-implement with smaller steps
   - Update todos.md to reflect any scope changes

2. **Test Failures**:
   - Commit current progress as WIP
   - Fix tests in separate commit
   - Update todos.md with testing progress
   - Squash if needed

3. **Merge Conflicts**:
   - Commit current work
   - Handle conflicts separately
   - Continue with planned commits
   - Sync todos.md with merged changes

4. **Task Scope Changes**:
   - Commit current working state
   - Update todos.md with revised task breakdown
   - Commit todos.md changes separately
   - Continue with updated plan

### Metrics and Success Indicators
Track these metrics to ensure process adherence:

- **Commit Frequency**: 8-12 commits per development hour
- **Commit Size**: Average 20-30 lines per commit
- **Rollback Rate**: <5% of commits need to be reverted
- **Review Time**: <2 minutes per commit during code review
- **Build Success**: >95% of commits should pass CI/CD
- **Todo Sync Rate**: todos.md updated within 2 commits of task completion
- **Task Completion Accuracy**: <5% of marked tasks need status revision

### Todos.md Maintenance Rules

#### Weekly Maintenance (Sundays)
1. **Archive Completed Tasks**: Move all `[x]` items to "✅ Tâches Complétées" section
2. **Review Progress**: Update task priorities based on completed work
3. **Clean Up**: Remove outdated or irrelevant tasks
4. **Reorganize**: Reorder tasks by current priority
5. **Commit Changes**: `docs(todos): weekly maintenance and task reorganization`

#### Daily Best Practices
- **Morning Review**: Check todos.md before starting development
- **End-of-Day Update**: Ensure all completed work is marked in todos.md
- **Scope Adjustments**: Update task descriptions if implementation differs from plan
- **New Task Discovery**: Add new sub-tasks discovered during implementation

#### Task Status Conventions
- `[ ]` - Not started
- `[x]` - Completed and tested
- `[~]` - In progress (use sparingly, prefer frequent commits)
- `[!]` - Blocked or needs attention
- `[-]` - Cancelled or obsolete

This process ensures maintainable code history, easier debugging, controlled development flow, and accurate project tracking through synchronized task management.
