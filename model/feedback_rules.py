CRITERIA_TITLES = {
    "task_response": "Task Response",
    "coherence_cohesion": "Coherence and Cohesion",
    "lexical_resource": "Lexical Resource",
    "grammar_range_accuracy": "Grammatical Range and Accuracy",
}


def message_for_score(criterion, score):
    if criterion == "task_response":
        if score < 5.5:
            return "Your position is not yet clear. Add more specific examples and develop each paragraph to directly address the question."
        elif score < 6.0:
            return "Your main ideas are present but lack strong support. Use more concrete examples and ensure each paragraph directly supports your position."
        elif score < 6.5:
            return "Your position is clear with some supporting details. Strengthen your examples and make sure all ideas directly relate to the question."
        elif score < 7.0:
            return "Your response is well-focused with relevant examples. Deepen your analysis and ensure seamless paragraph transitions to enhance clarity."
        elif score < 7.5:
            return "Your position is clearly stated and well-developed. Your examples are relevant and support your argument effectively."
        else:
            return "Excellent task response. Your position is clear, ideas are well-supported with specific examples, and all content directly addresses the question."

    elif criterion == "coherence_cohesion":
        if score < 5.5:
            return "Your essay needs clearer paragraph organization. Establish a logical structure and use linking words to guide the reader through your ideas."
        elif score < 6.0:
            return "You have a basic structure, but ideas jump around. Organize paragraphs logically and use clear transitions between them."
        elif score < 6.5:
            return "Your paragraphing is clear and ideas connect. Avoid repeating the same linking words and vary your transitions for better flow."
        elif score < 7.0:
            return "Your essay is well-organized with logical paragraph progression. Use more sophisticated transitions to enhance the natural flow between ideas."
        elif score < 7.5:
            return "Your organization is strong with clear, logical paragraph development. Transitions are appropriate and ideas flow naturally throughout."
        else:
            return "Excellent cohesion. Your essay is well-structured with seamless transitions, logical progression of ideas, and sophisticated linking devices."

    elif criterion == "lexical_resource":
        if score < 5.5:
            return "Too many repeated words limit your expression. Expand your vocabulary range and choose more precise words to convey your meaning."
        elif score < 6.0:
            return "You have adequate vocabulary but overuse some words. Replace repetitive words with synonyms and use more topic-relevant terms."
        elif score < 6.5:
            return "Your vocabulary is reasonably varied and mostly accurate. Work on natural collocations and increase the range of topic-specific words."
        elif score < 7.0:
            return "Your vocabulary use is solid with good variety and generally accurate collocations. Include more sophisticated or topic-specific terms to strengthen impact."
        elif score < 7.5:
            return "Your vocabulary is well-chosen, varied, and appropriately used. Collocations are mostly natural and show strong command of topic language."
        else:
            return "Excellent vocabulary range. Your word choices are precise and natural, collocations are sophisticated, and topic-specific terms are used expertly."

    else:  # grammar_range_accuracy
        if score < 5.5:
            return "Grammar errors are frequent and limit communication. Focus on sentence accuracy and practice using varied sentence structures correctly."
        elif score < 6.0:
            return "Basic sentences are mostly correct, but errors appear in longer structures. Simplify complex sentences while building accuracy with variety."
        elif score < 6.5:
            return "Most sentences are grammatically correct with some variety. Review errors in complex sentences and continue to expand sentence range safely."
        elif score < 7.0:
            return "Grammar is generally accurate with good sentence variety. Minor errors in complex structures are acceptable; keep strengthening complex sentence control."
        elif score < 7.5:
            return "Grammar is accurate and sentence structures are varied and well-controlled. Complex sentences are largely error-free and used effectively."
        else:
            return "Excellent grammar and sentence control. A wide range of structures is used accurately, including sophisticated complex sentences without errors."


def build_suggestions(raw_scores):
    return [
        {
            "criterion": criterion,
            "title": CRITERIA_TITLES[criterion],
            "message": message_for_score(criterion, raw_scores[criterion]),
        }
        for criterion in CRITERIA_TITLES
    ]
