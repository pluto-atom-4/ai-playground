# GitHub Copilot Instructions

**Purpose:** Suppress excessive file generation, maintain clean project structure, and use Git Bash for terminal operations.

---

## File & Documentation Generation

### Directory Rules
- **Output directory:** `generated/docs-copilot/` (auto-created)
- All generated files go to this subdirectory by default
- **Maximum files per session:** 1
- **Require explicit user request** before generating

### Suppress in Root
❌ `COMPLETION-SUMMARY.*`, `FINAL-.*`, `IMPLEMENTATION.*`, `*-COMPLETE.*`, `*-STATUS.*`, `*-SUMMARY.*`, `*-REPORT.*`, `QUICK_REFERENCE.*`, `INDEX.*`, `MANIFEST.*`, `CONFIGURATION.*`, `DELIVERABLES.*`

### Preserve in Root Only
✅ `README.md`, `README-*.md`, `SETUP.md`, `CONTRIBUTING.md`, `LICENSE`

### Correct File Paths
```
✅ generated/docs-copilot/QUICKSTART.md
✅ generated/docs-copilot/CHECKLIST.md
✅ generated/docs-copilot/API_REFERENCE.md
```

---

## Code Generation Rules

- Confirm before creating new files
- Prefer modifying existing files
- Keep changes focused and minimal

---

## Shell & Terminal Configuration

### Default Shell: bash.exe (Git Bash)

| Operation | Shell | Notes |
|-----------|-------|-------|
| ✅ Git operations | bash | POSIX paths: `/c/Users/...` |
| ✅ npm/node commands | bash | Auto-convert Windows paths |
| ✅ Python development | bash | |
| ✅ File/directory operations | bash | |
| ✅ Script execution | bash | |
| ❌ cmd.exe | | Avoid for grep, sed, awk, complex pipes |

### Git Configuration
- **Default branch:** main
- **Commit template:** `fix: {description}`
- **Auto-stage:** disabled

### Bash Environment
```
SHELL=bash
TERM=cygwin
Path conversion: C:\ → /c/
```

---

## Key Principles

1. **Minimal generation** - Create only what's necessary
2. **Single source of truth** - `README.md` is primary documentation
3. **No redundant files** - One comprehensive document > many partial ones
4. **Git Bash always** - Use `bash.exe` for all terminal operations
5. **Keep root clean** - Generated content → `generated/docs-copilot/`

