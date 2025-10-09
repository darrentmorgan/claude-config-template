---
description: Review completed work for quality, best practices, and issues
argument-hint: [modified-files]
model: claude-sonnet-4-5-20250929
---

# Review Phase

Comprehensive code review of changes made during `/build`.

## Variables

- MODIFIED_FILES: $1 (optional - comma-separated list of files to review)

## Purpose

Delegate to code-reviewer-pro agent to perform thorough code review.

## Workflow

1. If MODIFIED_FILES not provided, detect modified files via git status
2. Delegate to code-reviewer-pro agent via Task tool
3. Agent reviews each file for:
   - Code quality and best practices
   - Type safety (TypeScript)
   - Security vulnerabilities
   - Performance issues
   - Consistency with existing patterns
   - Test coverage
   - Documentation
4. Agent outputs structured review report to `.claude/.review-report.md`
5. If issues found → automatically suggest `/fix`
6. If no issues → mark as complete

## Critical Rules for code-reviewer-pro

**IMPORTANT: code-reviewer-pro agent restrictions:**

- **CANNOT** delegate to other agents
- **CANNOT** modify files (read-only review)
- **CAN** only use: Read, Grep, Glob (no Write, Edit, or Task)
- **MUST** output review report in specified format
- **MUST** mark severity for each issue (critical, warning, suggestion)

## Instructions to code-reviewer-pro

```
You are performing a code review of the following files:
{MODIFIED_FILES}

For each file:
1. Read the entire file using Read tool
2. Check for issues in these categories:
   - Code Quality: Readability, maintainability, complexity
   - Type Safety: Any 'any' types, missing type annotations
   - Security: SQL injection, XSS, auth issues, secrets
   - Performance: Inefficient algorithms, memory leaks
   - Best Practices: Following project conventions
   - Testing: Test coverage for new/changed code
   - Documentation: JSDoc comments, README updates

CRITICAL RULES:
- You CANNOT use Task, Write, or Edit tools
- You CAN use: Read, Grep, Glob only
- Output findings to .claude/.review-report.md
- Use the review report format below

After review, save report to .claude/.review-report.md in this format:

# Code Review Report

## Summary
- Files reviewed: X
- Issues found: Y
- Critical: Z
- Warnings: A
- Suggestions: B

## Issues

### File: src/components/Login.tsx

#### Issue 1: Missing error handling (CRITICAL)
**Line:** 56
**Current:**
```typescript
const user = await authService.login(email, password);
```
**Problem:** No try/catch block for async operation
**Fix:** Wrap in try/catch and show error to user
**Severity:** CRITICAL

### File: src/services/authService.ts

#### Issue 2: Using 'any' type (WARNING)
**Line:** 23
**Current:**
```typescript
const response: any = await fetch('/api/login');
```
**Problem:** Bypasses type safety
**Fix:** Define proper response interface
**Severity:** WARNING

## Recommendations

1. Add error boundaries for async operations
2. Define TypeScript interfaces for all API responses
3. Add unit tests for authService.login method

## Decision

- [X] Issues found - recommend /fix
- [ ] No issues - approve changes
```

## Output Format

After review completes:

```
✅ Code Review Complete

Files reviewed: 3
Issues found: 2
  - Critical: 1 (error handling)
  - Warnings: 1 (type safety)
  - Suggestions: 0

See .claude/.review-report.md for details

Next: /fix (issues found)
```

OR if no issues:

```
✅ Code Review Complete - NO ISSUES FOUND

Files reviewed: 3
All checks passed:
  ✓ Code quality
  ✓ Type safety
  ✓ Security
  ✓ Best practices

Workflow complete!
```

## Next Step

- If issues found → System suggests `/fix`
- If no issues → Workflow marked as complete
