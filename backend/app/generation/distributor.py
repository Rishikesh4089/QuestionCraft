# app/generation/distributor.py
"""
Deterministic topic distribution across question slots.

Given a TopicTree and a question_structure list, this module produces
an ordered list of QuestionSlots — one per question in the paper.
Each slot is fully specified: section, topic, subtopic, bloom level, marks.

Determinism is guaranteed by using a seeded random.Random instance.
The same inputs always produce the same slot assignment — useful for
reproducible test runs and debugging.
"""
from __future__ import annotations

import logging
import random
from typing import Dict, List

from  app.schemas.paper import QuestionSlot
from  app.schemas.rag import TopicTree

logger = logging.getLogger(__name__)

_BLOOM_MAP: Dict[str, List[str]] = {
    "Easy":   ["Remember", "Understand"],
    "Medium": ["Apply", "Analyze"],
    "Hard":   ["Evaluate", "Create"],
    "Mixed":  ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"],
}

_DEFAULT_TOPIC = {
    "topic": "Core Concepts",
    "subtopics": ["Fundamentals", "Applications", "Examples"],
    "weight": 1,
    "bloom_affinity": ["Remember", "Understand", "Apply"],
}


def distribute_topics(
    topic_tree: TopicTree,
    question_structure: List[dict],
    difficulty: str = "Mixed",
    seed: int = 42,
) -> List[QuestionSlot]:
    """
    Map topics to question slots.

    Algorithm:
      1. Flatten all topics with weights from the TopicTree.
      2. Weighted-sample (with replacement) to fill total slot count.
      3. For each section/slot: assign topic, subtopic (cycling for variety),
         and a bloom level (filtered by difficulty).

    Args:
        topic_tree:         Extracted from the syllabus.
        question_structure: List of section defs from the paper pattern.
        difficulty:         "Easy" | "Medium" | "Hard" | "Mixed"
        seed:               RNG seed for reproducibility.

    Returns:
        Ordered list of QuestionSlot objects.
    """
    rng = random.Random(seed)
    bloom_pool = _BLOOM_MAP.get(difficulty, _BLOOM_MAP["Mixed"])

    # Flatten TopicTree into a simple list with weights
    flat: List[dict] = []
    for unit in topic_tree.units:
        for topic in unit.topics:
            eligible_bloom = [b for b in (topic.bloom_affinity or bloom_pool) if b in bloom_pool]
            flat.append({
                "topic": topic.name,
                "subtopics": topic.subtopics or [topic.name],
                "weight": topic.estimated_weight,
                "bloom_affinity": eligible_bloom or bloom_pool,
            })

    if not flat:
        flat = [_DEFAULT_TOPIC.copy()]

    total_slots = sum(s.get("question_count", 1) for s in question_structure)
    weights = [t["weight"] for t in flat]

    # Weighted sample — deterministic via seeded RNG
    selected = rng.choices(flat, weights=weights, k=total_slots)

    slots: List[QuestionSlot] = []
    topic_iter = iter(selected)

    for section_def in question_structure:
        section_name = section_def.get("section", "A")
        q_count      = section_def.get("question_count", 1)
        marks_each   = section_def.get("marks_each", 5)
        q_type       = section_def.get("question_type", "General")

        for i in range(q_count):
            t = next(topic_iter)
            # Cycle through subtopics so consecutive questions in the same
            # section don't all land on the same subtopic
            subtopic = t["subtopics"][i % len(t["subtopics"])]
            bloom    = rng.choice(t["bloom_affinity"])

            slots.append(QuestionSlot(
                section=section_name,
                slot_index=i,
                topic=t["topic"],
                subtopic=subtopic,
                bloom_level=bloom,
                marks=marks_each,
                question_type=q_type,
                difficulty=difficulty,
            ))

    logger.info(
        f"Distributed {len(slots)} slots across {len(question_structure)} sections "
        f"(difficulty={difficulty}, seed={seed})"
    )
    return slots