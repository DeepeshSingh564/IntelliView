
def score_answer(answer_text: str, keywords: list, min_words: int = 30):
    answer = (answer_text or "").strip()
    words = answer.split()
    feedback_parts = []
    score = 0

    # Length heuristic
    if len(words) >= min_words:
        score += 2
        feedback_parts.append(f"Good length ({len(words)} words).")
    else:
        feedback_parts.append(f"Answer is short ({len(words)} words). Aim for {min_words}+ words.")

    # Keyword coverage
    lower_ans = answer.lower()
    matched = [kw for kw in (keywords or []) if kw.lower() in lower_ans]
    score += len(matched)
    if matched:
        feedback_parts.append("Covered keywords: " + ", ".join(matched) + ".")
    else:
        if keywords:
            feedback_parts.append("Missed key concepts: " + ", ".join(keywords[:3]) + ".")

    # Simple structure check
    sentences = [s for s in answer.split('.') if s.strip()]
    if len(sentences) >= 2:
        score += 1
        feedback_parts.append("Good structure (multiple sentences).")
    else:
        feedback_parts.append("Try structuring in 2–3 sentences with examples.")

    return score, " ".join(feedback_parts)
