#!/usr/bin/env python3
"""
Fuzzy Patch Module

Provides fuzzy matching for text find-and-replace operations, inspired by
Hermes-agent's fuzzy_match.py with 9-strategy matching chain:

1. Exact match - Direct string comparison
2. Line-trimmed - Strip leading/trailing whitespace per line
3. Whitespace normalized - Collapse multiple spaces/tabs to single space
4. Indentation flexible - Ignore indentation differences entirely
5. Escape normalized - Convert \\n literals to actual newlines
6. Trimmed boundary - Trim first/last line whitespace only
7. Unicode normalized - Smart quotes, em/en dashes, ellipsis
8. Block anchor - Match first+last lines, use similarity for middle
9. Context-aware - 50% line similarity threshold

Usage:
    from fuzzy_patch import fuzzy_find_and_replace

    new_content, match_count, strategy, error = fuzzy_find_and_replace(
        content="def foo():\n    pass",
        old_string="def foo():",
        new_string="def bar():",
        replace_all=False
    )
"""

import re
from typing import Tuple, Optional, List, Callable
from difflib import SequenceMatcher

UNICODE_MAP = {
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u2014": "--",
    "\u2013": "-",
    "\u2026": "...",
    "\u00a0": " ",
}


def _unicode_normalize(text: str) -> str:
    """Normalizes Unicode characters to their standard ASCII equivalents."""
    for char, repl in UNICODE_MAP.items():
        text = text.replace(char, repl)
    return text


def fuzzy_find_and_replace(
    content: str, old_string: str, new_string: str, replace_all: bool = False
) -> Tuple[str, int, Optional[str], Optional[str]]:
    """
    Find and replace text using a chain of increasingly fuzzy matching strategies.

    Args:
        content: The file content to search in
        old_string: The text to find
        new_string: The replacement text
        replace_all: If True, replace all occurrences; if False, require uniqueness

    Returns:
        Tuple of (new_content, match_count, strategy_name, error_message)
        - If successful: (modified_content, number_of_replacements, strategy_used, None)
        - If failed: (original_content, 0, None, error_description)
    """
    if not old_string:
        return content, 0, None, "old_string cannot be empty"

    if old_string == new_string:
        return content, 0, None, "old_string and new_string are identical"

    strategies: List[Tuple[str, Callable]] = [
        ("exact", _strategy_exact),
        ("line_trimmed", _strategy_line_trimmed),
        ("whitespace_normalized", _strategy_whitespace_normalized),
        ("indentation_flexible", _strategy_indentation_flexible),
        ("escape_normalized", _strategy_escape_normalized),
        ("trimmed_boundary", _strategy_trimmed_boundary),
        ("unicode_normalized", _strategy_unicode_normalized),
        ("block_anchor", _strategy_block_anchor),
        ("context_aware", _strategy_context_aware),
    ]

    for strategy_name, strategy_fn in strategies:
        matches = strategy_fn(content, old_string)

        if matches:
            if len(matches) > 1 and not replace_all:
                return (
                    content,
                    0,
                    None,
                    (
                        f"Found {len(matches)} matches for old_string. "
                        f"Provide more context to make it unique, or use replace_all=True."
                    ),
                )

            new_content = _apply_replacements(content, matches, new_string)
            return new_content, len(matches), strategy_name, None

    return content, 0, None, "Could not find a match for old_string in the file"


def _apply_replacements(
    content: str, matches: List[Tuple[int, int]], new_string: str
) -> str:
    """Apply replacements at the given positions."""
    sorted_matches = sorted(matches, key=lambda x: x[0], reverse=True)

    result = content
    for start, end in sorted_matches:
        result = result[:start] + new_string + result[end:]

    return result


def _strategy_exact(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 1: Exact string match."""
    matches = []
    start = 0
    while True:
        pos = content.find(pattern, start)
        if pos == -1:
            break
        matches.append((pos, pos + len(pattern)))
        start = pos + 1
    return matches


def _strategy_line_trimmed(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 2: Match with line-by-line whitespace trimming."""
    pattern_lines = [line.strip() for line in pattern.split("\n")]
    pattern_normalized = "\n".join(pattern_lines)

    content_lines = content.split("\n")
    content_normalized_lines = [line.strip() for line in content_lines]

    return _find_normalized_matches(
        content, content_lines, content_normalized_lines, pattern, pattern_normalized
    )


def _strategy_whitespace_normalized(
    content: str, pattern: str
) -> List[Tuple[int, int]]:
    """Strategy 3: Collapse multiple whitespace to single space."""

    def normalize(s):
        return re.sub(r"[ \t]+", " ", s)

    pattern_normalized = normalize(pattern)
    content_normalized = normalize(content)

    matches_in_normalized = _strategy_exact(content_normalized, pattern_normalized)

    if not matches_in_normalized:
        return []

    return _map_normalized_positions(content, content_normalized, matches_in_normalized)


def _strategy_indentation_flexible(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 4: Ignore indentation differences entirely."""
    content_lines = content.split("\n")
    content_stripped_lines = [line.lstrip() for line in content_lines]
    pattern_lines = [line.lstrip() for line in pattern.split("\n")]

    return _find_normalized_matches(
        content,
        content_lines,
        content_stripped_lines,
        pattern,
        "\n".join(pattern_lines),
    )


def _strategy_escape_normalized(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 5: Convert escape sequences to actual characters."""

    def unescape(s):
        return s.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")

    pattern_unescaped = unescape(pattern)

    if pattern_unescaped == pattern:
        return []

    return _strategy_exact(content, pattern_unescaped)


def _strategy_trimmed_boundary(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 6: Trim whitespace from first and last lines only."""
    pattern_lines = pattern.split("\n")
    if not pattern_lines:
        return []

    pattern_lines[0] = pattern_lines[0].strip()
    if len(pattern_lines) > 1:
        pattern_lines[-1] = pattern_lines[-1].strip()

    modified_pattern = "\n".join(pattern_lines)
    content_lines = content.split("\n")

    matches = []
    pattern_line_count = len(pattern_lines)

    for i in range(len(content_lines) - pattern_line_count + 1):
        block_lines = content_lines[i : i + pattern_line_count]
        check_lines = block_lines.copy()
        check_lines[0] = check_lines[0].strip()
        if len(check_lines) > 1:
            check_lines[-1] = check_lines[-1].strip()

        if "\n".join(check_lines) == modified_pattern:
            start_pos, end_pos = _calculate_line_positions(
                content_lines, i, i + pattern_line_count, len(content)
            )
            matches.append((start_pos, end_pos))

    return matches


def _build_orig_to_norm_map(original: str) -> List[int]:
    """Build a list mapping each original character index to its normalized index."""
    result: List[int] = []
    norm_pos = 0
    for char in original:
        result.append(norm_pos)
        repl = UNICODE_MAP.get(char)
        norm_pos += len(repl) if repl is not None else 1
    result.append(norm_pos)
    return result


def _map_positions_norm_to_orig(
    orig_to_norm: List[int],
    norm_matches: List[Tuple[int, int]],
) -> List[Tuple[int, int]]:
    """Convert (start, end) positions in the normalised string to original positions."""
    norm_to_orig_start: dict[int, int] = {}
    for orig_pos, norm_pos in enumerate(orig_to_norm[:-1]):
        if norm_pos not in norm_to_orig_start:
            norm_to_orig_start[norm_pos] = orig_pos

    results: List[Tuple[int, int]] = []
    orig_len = len(orig_to_norm) - 1

    for norm_start, norm_end in norm_matches:
        if norm_start not in norm_to_orig_start:
            continue
        orig_start = norm_to_orig_start[norm_start]

        orig_end = orig_start
        while orig_end < orig_len and orig_to_norm[orig_end] < norm_end:
            orig_end += 1

        results.append((orig_start, orig_end))

    return results


def _strategy_unicode_normalized(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 7: Unicode normalisation."""
    norm_pattern = _unicode_normalize(pattern)
    norm_content = _unicode_normalize(content)
    if norm_content == content and norm_pattern == pattern:
        return []

    norm_matches = _strategy_exact(norm_content, norm_pattern)
    if not norm_matches:
        norm_matches = _strategy_line_trimmed(norm_content, norm_pattern)

    if not norm_matches:
        return []

    orig_to_norm = _build_orig_to_norm_map(content)
    return _map_positions_norm_to_orig(orig_to_norm, norm_matches)


def _strategy_block_anchor(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 8: Match by anchoring on first and last lines."""
    norm_pattern = _unicode_normalize(pattern)
    norm_content = _unicode_normalize(content)

    pattern_lines = norm_pattern.split("\n")
    if len(pattern_lines) < 2:
        return []

    first_line = pattern_lines[0].strip()
    last_line = pattern_lines[-1].strip()

    norm_content_lines = norm_content.split("\n")
    orig_content_lines = content.split("\n")

    pattern_line_count = len(pattern_lines)

    potential_matches = []
    for i in range(len(norm_content_lines) - pattern_line_count + 1):
        if (
            norm_content_lines[i].strip() == first_line
            and norm_content_lines[i + pattern_line_count - 1].strip() == last_line
        ):
            potential_matches.append(i)

    matches = []
    candidate_count = len(potential_matches)

    threshold = 0.50 if candidate_count == 1 else 0.70

    for i in potential_matches:
        if pattern_line_count <= 2:
            similarity = 1.0
        else:
            content_middle = "\n".join(
                norm_content_lines[i + 1 : i + pattern_line_count - 1]
            )
            pattern_middle = "\n".join(pattern_lines[1:-1])
            similarity = SequenceMatcher(None, content_middle, pattern_middle).ratio()

        if similarity >= threshold:
            start_pos, end_pos = _calculate_line_positions(
                orig_content_lines, i, i + pattern_line_count, len(content)
            )
            matches.append((start_pos, end_pos))

    return matches


def _strategy_context_aware(content: str, pattern: str) -> List[Tuple[int, int]]:
    """Strategy 9: Line-by-line similarity with 50% threshold."""
    pattern_lines = pattern.split("\n")
    content_lines = content.split("\n")

    if not pattern_lines:
        return []

    matches = []
    pattern_line_count = len(pattern_lines)

    for i in range(len(content_lines) - pattern_line_count + 1):
        block_lines = content_lines[i : i + pattern_line_count]

        high_similarity_count = 0
        for p_line, c_line in zip(pattern_lines, block_lines):
            sim = SequenceMatcher(None, p_line.strip(), c_line.strip()).ratio()
            if sim >= 0.80:
                high_similarity_count += 1

        if high_similarity_count >= len(pattern_lines) * 0.5:
            start_pos, end_pos = _calculate_line_positions(
                content_lines, i, i + pattern_line_count, len(content)
            )
            matches.append((start_pos, end_pos))

    return matches


def _calculate_line_positions(
    content_lines: List[str], start_line: int, end_line: int, content_length: int
) -> Tuple[int, int]:
    """Calculate start and end character positions from line indices."""
    start_pos = sum(len(line) + 1 for line in content_lines[:start_line])
    end_pos = sum(len(line) + 1 for line in content_lines[:end_line]) - 1
    if end_pos >= content_length:
        end_pos = content_length
    return start_pos, end_pos


def _find_normalized_matches(
    content: str,
    content_lines: List[str],
    content_normalized_lines: List[str],
    pattern: str,
    pattern_normalized: str,
) -> List[Tuple[int, int]]:
    """Find matches in normalized content and map back to original positions."""
    pattern_norm_lines = pattern_normalized.split("\n")
    num_pattern_lines = len(pattern_norm_lines)

    matches = []

    for i in range(len(content_normalized_lines) - num_pattern_lines + 1):
        block = "\n".join(content_normalized_lines[i : i + num_pattern_lines])

        if block == pattern_normalized:
            start_pos, end_pos = _calculate_line_positions(
                content_lines, i, i + num_pattern_lines, len(content)
            )
            matches.append((start_pos, end_pos))

    return matches


def _map_normalized_positions(
    original: str, normalized: str, normalized_matches: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """Map positions from normalized string back to original."""
    if not normalized_matches:
        return []

    orig_to_norm = []
    orig_idx = 0
    norm_idx = 0

    while orig_idx < len(original) and norm_idx < len(normalized):
        if original[orig_idx] == normalized[norm_idx]:
            orig_to_norm.append(norm_idx)
            orig_idx += 1
            norm_idx += 1
        elif original[orig_idx] in " \t" and normalized[norm_idx] == " ":
            orig_to_norm.append(norm_idx)
            orig_idx += 1
            if orig_idx < len(original) and original[orig_idx] not in " \t":
                norm_idx += 1
        elif original[orig_idx] in " \t":
            orig_to_norm.append(norm_idx)
            orig_idx += 1
        else:
            orig_to_norm.append(norm_idx)
            orig_idx += 1

    while orig_idx < len(original):
        orig_to_norm.append(len(normalized))
        orig_idx += 1

    norm_to_orig_start = {}
    norm_to_orig_end = {}

    for orig_pos, norm_pos in enumerate(orig_to_norm):
        if norm_pos not in norm_to_orig_start:
            norm_to_orig_start[norm_pos] = orig_pos
        norm_to_orig_end[norm_pos] = orig_pos

    original_matches = []
    for norm_start, norm_end in normalized_matches:
        if norm_start in norm_to_orig_start:
            orig_start = norm_to_orig_start[norm_start]
        else:
            orig_start = min(i for i, n in enumerate(orig_to_norm) if n >= norm_start)

        if norm_end - 1 in norm_to_orig_end:
            orig_end = norm_to_orig_end[norm_end - 1] + 1
        else:
            orig_end = orig_start + (norm_end - norm_start)

        while orig_end < len(original) and original[orig_end] in " \t":
            orig_end += 1

        original_matches.append((orig_start, min(orig_end, len(original))))

    return original_matches


class FuzzyPatcher:
    """Fuzzy patcher for editing skill files with fuzzy matching."""

    def __init__(self, content: str = ""):
        self.content = content

    def load_content(self, content: str) -> None:
        """Load file content for editing."""
        self.content = content

    def patch(
        self, old_string: str, new_string: str, replace_all: bool = False
    ) -> Tuple[str, int, Optional[str], Optional[str]]:
        """Apply fuzzy patch to loaded content."""
        result = fuzzy_find_and_replace(
            self.content, old_string, new_string, replace_all
        )
        self.content = result[0]
        return result

    def find(
        self, pattern: str, strategy_hint: Optional[str] = None
    ) -> List[Tuple[int, int]]:
        """Find pattern matches, optionally with strategy hint."""
        if strategy_hint:
            strategies_map = {
                "exact": _strategy_exact,
                "line_trimmed": _strategy_line_trimmed,
                "whitespace_normalized": _strategy_whitespace_normalized,
                "indentation_flexible": _strategy_indentation_flexible,
                "escape_normalized": _strategy_escape_normalized,
                "trimmed_boundary": _strategy_trimmed_boundary,
                "unicode_normalized": _strategy_unicode_normalized,
                "block_anchor": _strategy_block_anchor,
                "context_aware": _strategy_context_aware,
            }
            strategy_fn = strategies_map.get(strategy_hint, _strategy_exact)
            return strategy_fn(self.content, pattern)

        for strategy_name, strategy_fn in [
            ("exact", _strategy_exact),
            ("line_trimmed", _strategy_line_trimmed),
            ("whitespace_normalized", _strategy_whitespace_normalized),
            ("indentation_flexible", _strategy_indentation_flexible),
            ("unicode_normalized", _strategy_unicode_normalized),
            ("block_anchor", _strategy_block_anchor),
        ]:
            matches = strategy_fn(self.content, pattern)
            if matches:
                return matches

        return []


if __name__ == "__main__":
    print("Fuzzy Patch Test")
    print("=" * 50)

    test_content = """def foo():
    pass

def bar():
    return True"""

    print("\n1. Exact match:")
    new_content, count, strategy, error = fuzzy_find_and_replace(
        test_content, "def foo():", "def baz():", replace_all=False
    )
    print(f"  Strategy: {strategy}, Count: {count}")
    print(f"  Result:\n{new_content}")

    print("\n2. Line-trimmed match:")
    test_content2 = """def foo() :
        pass
"""
    new_content2, count2, strategy2, error2 = fuzzy_find_and_replace(
        test_content2, "def foo():", "def baz():"
    )
    print(f"  Strategy: {strategy2}, Count: {count2}")
    print(f"  Result:\n{new_content2}")

    print("\n3. Indentation-flexible match:")
    test_content3 = """def foo():
    pass
    more = True"""
    new_content3, count3, strategy3, error3 = fuzzy_find_and_replace(
        test_content3, "def foo():", "def baz():"
    )
    print(f"  Strategy: {strategy3}, Count: {count3}")
    print(f"  Result:\n{new_content3}")

    print("\n4. Test FuzzyPatcher class:")
    patcher = FuzzyPatcher()
    patcher.load_content("Hello  world\n\n\tGoodbye")
    matches = patcher.find("Hello world")
    print(f"  Found {len(matches)} matches")
