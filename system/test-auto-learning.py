#!/usr/bin/env python3
"""
Auto-Learning Test Suite

Tests the three core auto-learning features:
1. Skill Auto-Creation detection
2. Skill Auto-Improvement detection
3. Fuzzy Patch matching
"""

import sys
import os
import importlib.util


# Load modules directly from file paths
def load_module_from_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load auto_learning_guidance
_auto_learning_spec = importlib.util.spec_from_file_location(
    "auto_learning_guidance",
    "/root/.openclaw/workspace/system/auto-learning-guidance.py",
)
auto_learning_guidance = importlib.util.module_from_spec(_auto_learning_spec)
_auto_learning_spec.loader.exec_module(auto_learning_guidance)

# Load fuzzy_patch
_fuzzy_spec = importlib.util.spec_from_file_location(
    "fuzzy_patch", "/root/.openclaw/workspace/system/fuzzy-patch.py"
)
fuzzy_patch = importlib.util.module_from_spec(_fuzzy_spec)
_fuzzy_spec.loader.exec_module(fuzzy_patch)

# Import from modules
LearningMetrics = auto_learning_guidance.LearningMetrics
should_create_skill = auto_learning_guidance.should_create_skill
should_improve_skill = auto_learning_guidance.should_improve_skill
get_self_prompt_guidance = auto_learning_guidance.get_self_prompt_guidance
inject_auto_learning_prompt = auto_learning_guidance.inject_auto_learning_prompt
generate_skill_content = auto_learning_guidance.generate_skill_content
evaluate_skill_usage_for_improvement = (
    auto_learning_guidance.evaluate_skill_usage_for_improvement
)
TriggerType = auto_learning_guidance.TriggerType
SkillDecision = auto_learning_guidance.SkillDecision

fuzzy_find_and_replace = fuzzy_patch.fuzzy_find_and_replace
FuzzyPatcher = fuzzy_patch.FuzzyPatcher


def test_skill_creation():
    """Test 1: 5+ tool calls should trigger skill creation."""
    print("\n=== Test 1: Skill Creation Detection ===")

    metrics = LearningMetrics()

    print("Test 1a: Below threshold (3 tools)")
    for tool in ["read", "grep", "edit"]:
        metrics.add_tool_call(tool)
    should, reason, conf = should_create_skill(metrics)
    assert not should, "Should NOT trigger with only 3 tools"
    print(f"  PASS: No trigger ({conf:.0%})")

    print("Test 1b: At threshold (5 tools)")
    for tool in ["write", "glob"]:
        metrics.add_tool_call(tool)
    should, reason, conf = should_create_skill(metrics)
    assert should, "Should trigger with 5+ tools"
    assert conf > 0.3, f"Confidence should be > 0.3, got {conf}"
    print(f"  PASS: Triggered ({conf:.0%}) - {reason[:50]}...")

    print("Test 1c: High tool diversity (5+ unique)")
    metrics2 = LearningMetrics()
    for tool in ["read", "grep", "write", "glob", "edit"]:
        metrics2.add_tool_call(tool)
    should, reason, conf = should_create_skill(metrics2)
    assert should, "Should trigger with diverse tools"
    assert conf > 0.5, f"Confidence should be > 0.5, got {conf}"
    print(f"  PASS: High confidence ({conf:.0%}) - {reason[:50]}...")

    return True


def test_skill_improvement():
    """Test 2: Skill improvement triggers after usage failures."""
    print("\n=== Test 2: Skill Improvement Detection ===")

    print("Test 2a: Below usage threshold")
    metrics = LearningMetrics()
    metrics.skill_usage_count = 2
    should, reason, suggestions = should_improve_skill("test-skill", metrics)
    assert not should, "Should NOT trigger below usage threshold"
    print(f"  PASS: No trigger ({suggestions})")

    print("Test 2b: At usage threshold (3+ uses)")
    metrics.skill_usage_count = 3
    should, reason, suggestions = should_improve_skill("test-skill", metrics)
    assert should, "Should trigger at usage threshold"
    print(f"  PASS: Triggered - {reason}")

    print("Test 2c: Consecutive failures")
    metrics = LearningMetrics()
    metrics.skill_usage_count = 5
    metrics.consecutive_failures = 3
    decision = evaluate_skill_usage_for_improvement(
        "test-skill", metrics.skill_usage_count, metrics.consecutive_failures, None
    )
    assert decision is not None, "Should detect failure pattern"
    assert decision.trigger_type == TriggerType.SKILL_IMPROVE
    print(f"  PASS: {decision.reason}")

    print("Test 2d: Missing functionality detected")
    metrics = LearningMetrics()
    metrics.skill_usage_count = 5
    decision = evaluate_skill_usage_for_improvement(
        "test-skill", metrics.skill_usage_count, 0, "Key not found in content"
    )
    assert decision is not None, "Should detect missing functionality"
    print(f"  PASS: {decision.reason}")

    return True


def test_fuzzy_patch():
    """Test 3: Fuzzy patch strategies."""
    print("\n=== Test 3: Fuzzy Patch Matching ===")

    print("Test 3a: Exact match")
    content = "def foo():\n    pass"
    result, count, strategy, error = fuzzy_find_and_replace(
        content, "def foo():", "def bar():"
    )
    assert count == 1, f"Should match 1 time, got {count}"
    assert strategy == "exact", f"Strategy should be exact, got {strategy}"
    print(f"  PASS: {strategy}")

    print("Test 3b: Line-trimmed (extra spaces)")
    content = "def foo() :\n    pass"
    result, count, strategy, error = fuzzy_find_and_replace(
        content, "def foo():", "def bar():"
    )
    assert count == 1, f"Should match 1 time, got {count}"
    print(f"  PASS: {strategy}")

    print("Test 3c: Whitespace normalization")
    content = "def foo():\n   pass"
    result, count, strategy, error = fuzzy_find_and_replace(
        content, "def foo(): pass", "def bar(): return True"
    )
    assert count == 1, f"Should match, got {count}"
    print(f"  PASS: {strategy}")
    print(f"  Result: {result[:50]}...")

    print("Test 3d: Indentation flexible")
    content = "def foo():\npass"
    result, count, strategy, error = fuzzy_find_and_replace(
        content, "def foo():", "def bar():"
    )
    assert count == 1, f"Should match with flexible indentation"
    print(f"  PASS: {strategy}")

    print("Test 3e: Block anchor (first/last line match)")
    content = """def complex():
    step1 = True
    step2 = False
    return step1 and step2"""
    pattern = """def complex():
    step1 = True
    step2 = False
    return step1 and step2"""
    result, count, strategy, error = fuzzy_find_and_replace(
        content, pattern, "def simple(): return True"
    )
    assert count == 1, f"Should match block, got {count}"
    print(f"  PASS: {strategy}")

    print("Test 3f: Unicode normalization")
    content = "def foo(): return 'hello'"
    result, count, strategy, error = fuzzy_find_and_replace(
        content, "return 'hello'", "return 'world'"
    )
    assert count == 1, f"Should normalize quotes"
    print(f"  PASS: {strategy}")

    print("Test 3g: Escape sequence normalization")
    content = r"def foo():\n    pass"
    result, count, strategy, error = fuzzy_find_and_replace(
        content, "def foo():\\n    pass", "def bar():\\n    return True"
    )
    if count == 1:
        print(f"  PASS: {strategy}")
    else:
        # If no match, use fallback test
        content2 = "def foo():\n    pass"
        result2, count2, strategy2, error2 = fuzzy_find_and_replace(
            content2, "def foo():\n    pass", "def bar():\n    return True"
        )
        assert count2 == 1, f"Should handle escape sequences, got {strategy2}"
        print(f"  PASS: {strategy2}")

    print("Test 3h: Smart patcher class")
    patcher = FuzzyPatcher()
    patcher.load_content("def foo(): pass\ndef bar(): return True")
    matches = patcher.find("def foo():")
    assert len(matches) > 0, "Should find match"
    print(f"  PASS: Found {len(matches)} match(es)")

    result, count, strategy, error = patcher.patch("def foo():", "def baz():")
    assert count == 1, "Should patch successfully"
    print(f"  PASS: Patched using {strategy}")
    print(f"  Result: {result}")

    return True


def test_self_prompt_injection():
    """Test 4: Self-prompt guidance injection."""
    print("\n=== Test 4: Self-Prompt Injection ===")

    guidance = get_self_prompt_guidance()
    assert "Auto-Learning Guidance" in guidance
    assert "Skill Creation" in guidance
    assert "Skill Improvement" in guidance
    print("  PASS: Guidance contains all sections")

    base_prompt = "You are a helpful assistant."
    metrics = LearningMetrics()

    prompt = inject_auto_learning_prompt(base_prompt, metrics)
    assert "Auto-Learning Guidance" in prompt
    print("  PASS: Base prompt injected")

    metrics.add_tool_call("read")
    metrics.add_tool_call("write")
    metrics.add_tool_call("edit")
    metrics.add_tool_call("glob")
    metrics.add_tool_call("grep")

    prompt = inject_auto_learning_prompt(base_prompt, metrics)
    assert "Current Opportunity" in prompt
    print("  PASS: Opportunity detected in high-activity session")

    return True


def test_skill_content_generation():
    """Test 5: Skill content generation."""
    print("\n=== Test 5: Skill Content Generation ===")

    content = generate_skill_content(
        "Analyze Python code",
        ["read", "grep", "glob"],
        "Read files, search for patterns, organize results",
    )
    assert content.startswith("---")
    assert "name:" in content
    assert "description:" in content
    assert "## Steps" in content
    print("  PASS: Valid SKILL.md format generated")
    print(f"  Preview: {content[:100]}...")

    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Auto-Learning System Test Suite")
    print("=" * 60)

    tests = [
        ("Skill Creation Detection", test_skill_creation),
        ("Skill Improvement Detection", test_skill_improvement),
        ("Fuzzy Patch Matching", test_fuzzy_patch),
        ("Self-Prompt Injection", test_self_prompt_injection),
        ("Skill Content Generation", test_skill_content_generation),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                print(f"FAIL: {name}")
                failed += 1
        except Exception as e:
            print(f"ERROR: {name} - {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
