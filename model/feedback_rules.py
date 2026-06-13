CRITERIA_TITLES = {
    "task_response": "Task Response",
    "coherence_cohesion": "Coherence and Cohesion",
    "lexical_resource": "Lexical Resource",
    "grammar_range_accuracy": "Grammatical Range and Accuracy",
}


def message_for_score(criterion, score):
    if criterion == "task_response":
        if score < 6:
            return "Develop your main ideas with clearer support and more specific examples."
        if score < 7:
            return "Make your position clearer and connect each paragraph more directly to the question."
        return "Your response addresses the question well. Keep your position and examples focused."

    if criterion == "coherence_cohesion":
        if score < 6:
            return "Use clearer paragraphing and make the relationship between ideas easier to follow."
        if score < 7:
            return "Improve transitions between paragraphs and avoid repeating the same linking words."
        return "The essay is organized well. Check that each paragraph develops one clear idea."

    if criterion == "lexical_resource":
        if score < 6:
            return "Reduce repeated words and choose vocabulary that is more accurate for the topic."
        if score < 7:
            return "Use more natural collocations and a wider range of topic-specific vocabulary."
        return "Vocabulary use is strong. Keep word choice precise and natural."

    if score < 6:
        return "Check sentence grammar carefully before using longer or more complex structures."
    if score < 7:
        return "Use a wider range of sentence structures while keeping grammar accurate."
    return "Grammar control is good. Review small errors in complex sentences."


def build_suggestions(raw_scores):
    return [
        {
            "criterion": criterion,
            "title": CRITERIA_TITLES[criterion],
            "message": message_for_score(criterion, raw_scores[criterion]),
        }
        for criterion in CRITERIA_TITLES
    ]
