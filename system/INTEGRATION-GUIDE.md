# OpenClaw Auto-Learning Integration Guide

## Overview

This guide explains how to integrate Hermes's three core auto-learning features into OpenClaw:

1. **Skill Auto-Creation** - Agent autonomously creates skills after complex tasks
2. **Skill Auto-Improvement** - Agent autonomously improves skills after usage failures
3. **Fuzzy Patch** - Fuzzy matching for skill edits (no exact string required)

## Files to Integrate

### File 1: auto-learning-guidance.py
Location: `/root/.openclaw/workspace/system/auto-learning-guidance.py`

**Purpose**: Provides decision framework for when to create/improve skills

**Integration Points**:
- Import into your agent loop
- Track LearningMetrics per conversation
- Call should_create_skill() after tool execution
- Call should_improve_skill() after skill usage
- Inject get_self_prompt_guidance() into system prompt

### File 2: fuzzy-patch.py
Location: `/root/.openclaw/workspace/system/fuzzy-patch.py`

**Purpose**: Enables fuzzy skill editing without exact string matching

**Integration Points**:
- Replace your edit tool's find-and-replace logic
- Use FuzzyPatcher class for skill file edits
- Works with skill_manager_tool for patches

## Integration Steps

### Step 1: Import the Modules

```python
import sys
sys.path.insert(0, "/root/.openclaw/workspace/system")

from auto_learning_guidance import (
    LearningMetrics,
    should_create_skill,
    should_improve_skill,
    get_self_prompt_guidance,
    inject_auto_learning_prompt,
    generate_skill_content,
    analyze_task_complexity,
)
```

### Step 2: Track Metrics

```python
session_metrics = LearningMetrics()

# In your tool execution loop:
def handle_tool_call(tool_name, result):
    success = check_success(result)  # Your success detection
    session_metrics.add_tool_call(tool_name, success)
```

### Step 3: Check Skill Creation

```python
should, reason, conf = should_create_skill(session_metrics)
if should and conf > 0.7:
    # Prompt agent to create skill
    prompt_skill_creation(task_description, session_metrics.tool_sequence, reason)
```

### Step 4: Check Skill Improvement

```python
should, reason, suggestions = should_improve_skill(skill_name, session_metrics, failure_context)
if should:
    # Prompt agent to improve skill
    prompt_skill_improvement(skill_name, suggestions)
```

### Step 5: Use Fuzzy Patch for Editing

```python
from fuzzy_patch import FuzzyPatcher

patcher = FuzzyPatcher()
patcher.load_content(skill_content)

# No exact match needed:
result, count, strategy, error = patcher.patch(
    "def foo():",  # Can be slightly different
    "def bar():",
)
```

## System Prompt Injection

Add this to your base system prompt:

```
## Auto-Learning Guidance

You can autonomously create and improve skills:

### Skill Creation Trigger
- 5+ tool calls in a session
- 3+ unique tools used  
- Reusable pattern detected

### Skill Improvement Trigger  
- Same skill used 3+ times
- Consecutive failures (3+)
- Clear improvement available

### Fuzzy Editing
When editing skills, you can use fuzzy matching - the system will find similar text automatically.
Don't worry about exact whitespace or indentation matching.
```

## Configuration

Default thresholds (in auto_learning_guidance.py):

```python
SKILL_CREATE_THRESHOLD = 5       # Tool calls before considering creation
SKILL_IMPROVE_USAGE_THRESHOLD = 3 # Uses before considering improvement
CONSECUTIVE_FAILURE_THRESHOLD = 3 # Failures triggering improvement
TOOL_DIVERSITY_THRESHOLD = 3        # Unique tools for pattern detection
TIME_WINDOW_SECONDS = 300           # Time window for task grouping
```

Adjust these in your configuration to make the agent more or less aggressive about skill creation.

## Testing

Test with the test-auto-learning.py file:

```bash
cd /root/.openclaw/workspace/system
python test_auto_learning.py
```

## Integration Checklist

- [ ] Import modules in agent initialization
- [ ] Add LearningMetrics tracking to session state
- [ ] Integrate should_create_skill() check after tool calls
- [ ] Integrate should_improve_skill() check after skill usage
- [ ] Inject auto-learning guidance into system prompt
- [ ] Use FuzzyPatcher in skill editing tools
- [ ] Test with complex task (5+ tools)
- [ ] Test skill improvement scenario
- [ ] Verify fuzzy patch works

## Example: OpenClaw skill_edit Integration

To use fuzzy-patch with your skill editing:

```python
async def edit_skill(skill_name: str, old_text: str, new_text: str):
    # Load skill content
    skill_path = find_skill(skill_name)
    content = skill_path.read_text()
    
    # Use fuzzy patch
    from fuzzy_patch import FuzzyPatcher
    patcher = FuzzyPatcher()
    patcher.load_content(content)
    
    result, count, strategy, error = patcher.patch(old_text, new_text)
    if error:
        raise ValueError(f"Fuzzy patch failed: {error}")
    
    # Save
    skill_path.write_text(result)
    return {"replacements": count, "strategy": strategy}
```

## Advanced: Custom Strategies

Add custom fuzzy matching strategies:

```python
from fuzzy_patch import _strategy_exact, _strategy_line_trimmed

def _strategy_my_custom(content: str, pattern: str):
    # Your custom matching logic
    # ...
    return matches

strategies = [
    ("exact", _strategy_exact),
    ("my_custom", _strategy_my_custom),
    ("line_trimmed", _strategy_line_trimmed),
    # ...
]
```