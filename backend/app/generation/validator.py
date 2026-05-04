# app/generation/validator.py
"""
Paper structure validator.

Validates a generated paper against the expected question_structure.
Returns a list of human-readable error strings — empty list means valid.

Called after full paper assembly and after targeted section repair.
"""
from __future__ import annotations

from typing import List


def validate_paper(
    sections: List[dict],
    question_structure: List[dict],
    expected_total_marks: int,
) -> List[str]:
    """
    Check a generated paper for structural correctness.

    Validates:
    - Total marks match expected
    - All expected sections are present
    - Each section has the correct question count
    - Topic diversity (> 50% unique topics across the paper)

    Args:
        sections:              The "sections" list from the generated PaperOutput.
        question_structure:    The question_structure list from the pattern.
        expected_total_marks:  The total marks the paper should add up to.

    Returns:
        List of error strings (empty = valid).
    """
    errors: List[str] = []

    # ── Marks total ───────────────────────────────────────────────────────
    actual_total = sum(
        q.get("marks", 0)
        for s in sections
        for q in s.get("questions", [])
    )
    if actual_total != expected_total_marks:
        errors.append(
            f"Mark total mismatch: expected {expected_total_marks}, got {actual_total}"
        )

    # ── Section presence ──────────────────────────────────────────────────
    expected_section_names = {s["section"] for s in question_structure}
    actual_section_names   = {s["section"] for s in sections}
    missing = expected_section_names - actual_section_names
    if missing:
        errors.append(f"Missing sections: {sorted(missing)}")

    # ── Question counts ───────────────────────────────────────────────────
    actual_by_name = {s["section"]: s for s in sections}
    for exp in question_structure:
        name = exp["section"]
        actual_section = actual_by_name.get(name)
        if actual_section is None:
            continue  # already caught above
        actual_count   = len(actual_section.get("questions", []))
        expected_count = exp.get("question_count", 0)
        if actual_count != expected_count:
            errors.append(
                f"Section {name}: expected {expected_count} questions, got {actual_count}"
            )

    # ── Topic diversity ───────────────────────────────────────────────────
    all_topics = [
        q.get("topic", "")
        for s in sections
        for q in s.get("questions", [])
        if q.get("topic")
    ]
    if all_topics:
        unique_ratio = len(set(all_topics)) / len(all_topics)
        if unique_ratio < 0.5:
            errors.append(
                f"Low topic diversity ({unique_ratio:.0%} unique topics) — "
                f"paper may be repetitive"
            )

    return errors