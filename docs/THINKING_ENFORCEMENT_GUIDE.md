# ULTRA THINK MODE - Enforcement Guide

**Status**: ✅ FULLY IMPLEMENTED
**Last Updated**: 2025-11-17
**Purpose**: Ensure Claude Code uses `<thinking>` blocks for all complex tasks

---

## 📋 Overview

This system enforces the use of ULTRA THINK MODE (extensive `<thinking>` blocks) through multiple layers:

1. **User Prompt Hook** - Reminds at input time
2. **Thinking Enforcer Script** - Verifies after response
3. **Assistant Response Hook** - Provides completion notification

---

## 🔧 Components

### 1. User Prompt Submit Hook

**File**: [.claude/hooks/user-prompt-submit.bat](.claude/hooks/user-prompt-submit.bat)

**Function**:
- Displays ULTRA THINK MODE reminder when user submits a prompt
- Shows CLAUDE.md compliance rules
- Prepares thinking enforcement

**Trigger**: Every user prompt submission

### 2. Thinking Enforcer Script

**File**: [.claude/scripts/thinking_enforcer.py](.claude/scripts/thinking_enforcer.py)

**Function**:
- Analyzes Claude's response for `<thinking>` blocks
- Counts thinking blocks and total thinking content
- Provides warnings if no thinking detected

**Usage**:
```bash
py .claude/scripts/thinking_enforcer.py <response_file>
```

**Exit Codes**:
- `0`: Thinking blocks found (OK)
- `1`: No thinking blocks (WARNING)

### 3. Assistant Response Hook

**File**: [.claude/hooks/assistant-response.bat](.claude/hooks/assistant-response.bat)

**Function**:
- Runs after Claude completes a response
- Automatically calls thinking_enforcer.py
- Displays task completion summary
- Shows thinking compliance status

**Trigger**: After every Claude response

---

## 🎯 How It Works

```
User submits prompt
    ↓
[user-prompt-submit.bat] displays ULTRA THINK MODE reminder
    ↓
Claude processes and responds (with <thinking> blocks)
    ↓
[assistant-response.bat] runs automatically
    ↓
Calls [thinking_enforcer.py] to verify thinking blocks
    ↓
Displays completion notification + thinking status
```

---

## ✅ Verification

### Test Thinking Enforcer

Create a test file with thinking content:

```bash
echo "<thinking>This is a test thinking block</thinking>" > test_response.txt
py .claude/scripts/thinking_enforcer.py test_response.txt
```

**Expected Output**:
```
==============================================================
  ULTRA THINK MODE - Verification
==============================================================
[OK] Thinking blocks found: 1
     Total thinking content: 52 characters

[SUCCESS] ULTRA THINK MODE is active
```

### Test Without Thinking

```bash
echo "This is a response without thinking" > test_response.txt
py .claude/scripts/thinking_enforcer.py test_response.txt
```

**Expected Output**:
```
==============================================================
  ULTRA THINK MODE - Verification
==============================================================
[WARNING] No thinking blocks detected!

REMINDER: You should use <thinking> blocks for:
  1. Complex problem analysis
  2. Multi-step reasoning
  3. Edge case consideration
  4. CLAUDE.md compliance check

This is just a reminder - not blocking execution
```

---

## 📊 Integration with CLAUDE.md

This enforcement system supports **Rule 1: ULTRA THINK MODE** from CLAUDE.md:

```markdown
## 🧠 Rule 1: ULTRA THINK MODE (必須・常時有効)

**このルールは全ての会話で自動的に適用されます。**

### 必須事項（MANDATORY）

**全てのタスクで以下を実行：**

1. **Extended Thinking（拡張思考）を使用**
```

The hooks ensure this rule is always visible and enforced.

---

## 🔄 Automatic Enforcement Flow

### Every Session

1. **Session Start**: Hooks are loaded automatically
2. **User Input**: `user-prompt-submit.bat` displays reminder
3. **Claude Response**: Assistant uses `<thinking>` blocks
4. **Response Complete**: `assistant-response.bat` verifies compliance

### Compliance Scoring

- **Thinking blocks present**: +5 points to compliance score
- **No thinking blocks**: -5 points + warning reminder
- **Score tracked**: In `.claude/enforcement/logs/compliance_scores.jsonl`

---

## 🛠️ Troubleshooting

### Hook Not Running

**Check if hooks are executable**:
```bash
ls -la .claude/hooks/
```

All `.bat` files should be readable.

### Thinking Enforcer Not Found

**Verify script location**:
```bash
ls -la .claude/scripts/thinking_enforcer.py
```

If missing, recreate using this guide.

### Response Log Not Found

The assistant-response hook looks for:
```
%USERPROFILE%\.claude\logs\last_response.txt
```

This file may not exist in all environments. The hook gracefully handles missing files.

---

## 📝 Manual Testing

### Test User Prompt Hook

```bash
.claude/hooks/user-prompt-submit.bat
```

Should display ULTRA THINK MODE reminder.

### Test Assistant Response Hook

```bash
.claude/hooks/assistant-response.bat
```

Should display task completion notification.

---

## 🎓 Best Practices

### When to Use Thinking Blocks

Always use `<thinking>` for:

1. **Complex Analysis**: Multi-step reasoning required
2. **Problem Decomposition**: Breaking down large tasks
3. **Edge Cases**: Considering unusual scenarios
4. **Rule Compliance**: Checking CLAUDE.md requirements
5. **Decision Making**: Weighing multiple options
6. **Error Prevention**: Anticipating potential issues

### Thinking Block Format

```xml
<thinking>
1. Understand the problem:
   - User wants X
   - Current state is Y
   - Need to achieve Z

2. Consider approaches:
   - Option A: Pros/Cons
   - Option B: Pros/Cons

3. Choose best approach: A because...

4. Check compliance:
   - CLAUDE.md Rule X: ✓
   - CLAUDE.md Rule Y: ✓

5. Plan implementation:
   - Step 1: ...
   - Step 2: ...
</thinking>
```

---

## 📈 Compliance Metrics

Track thinking usage in compliance logs:

```bash
cat .claude/enforcement/logs/compliance_scores.jsonl | grep thinking
```

Goal: 95%+ of responses should include thinking blocks for complex tasks.

---

## 🔗 Related Documentation

- **CLAUDE.md**: Main rules document
- **8-Layer Enforcement System**: `.claude/enforcement/SYSTEM_READY.md`
- **Session Monitoring**: `.claude/enforcement/README.md`

---

## ✨ Summary

This thinking enforcement system ensures Claude Code consistently uses deep reasoning through:

- ✅ **Visual Reminders**: At every prompt
- ✅ **Automatic Verification**: After every response
- ✅ **Completion Notifications**: With compliance status
- ✅ **Non-Blocking**: Warnings only, doesn't block workflow
- ✅ **Compliance Tracking**: Integrated with 8-layer system

**Result**: Higher quality responses with proper reasoning and CLAUDE.md compliance.
