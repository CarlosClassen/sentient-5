import re


class ScoringSystem:
    def __init__(self, logger=None):
        """Initialize ScoringSystem."""
        self.traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
        self.scores = {trait: 0 for trait in self.traits}
        self.logger = logger

        self.logger.info("ScoringSystem initialized.") if self.logger else None

    def reset(self):
        """Reset scores for all traits."""
        self.logger.info("Resetting scores.")
        self.scores = {trait: 0 for trait in self.traits}

    def update_scores(self, response_content, user_input, emotion=None):
        """
        Update scores based on the model's response or fallback heuristics.

        Args:
        - response_content (str): The response from the model, which may include a numerical score.
        - user_input (str): The user's input for fallback heuristics.
        - emotion (str, optional): The user's emotional state to weigh the scores.
        """
        self.logger.info(f"Updating scores based on response: {response_content}")
        extracted_scores = self.extract_scores(response_content)

        if extracted_scores:
            # Update scores using extracted numerical values
            for trait, score in extracted_scores.items():
                self.scores[trait] += score
                self.logger.info(f"Updated '{trait}' with score: {score} (Total: {self.scores[trait]})")
        else:
            # Fallback to heuristic analysis
            self.logger.info("No numerical scores found. Falling back to heuristic analysis.")
            self.apply_fallback_heuristics(user_input, emotion)

    def extract_scores(self, response_content):
        """
        Extract numerical scores from the model's response.

        The model is expected to return scores in a format like: "Scores: 0 1 -1 0 1"

        Returns:
        - A dictionary of trait scores, or None if no scores are found.
        """
        self.logger.info(f"Extracting scores from response: {response_content}")
        score_pattern = r"Scores:\s*(-?\d(?:\s-?\d)*)"
        match = re.search(score_pattern, response_content)

        if match:
            score_values = list(map(int, match.group(1).split()))
            if len(score_values) == len(self.traits):
                extracted_scores = dict(zip(self.traits, score_values))
                self.logger.info(f"Extracted scores: {extracted_scores}")
                return extracted_scores

        self.logger.warning("No valid scores found in response.")
        return None

    def apply_fallback_heuristics(self, user_input, emotion=None):
        """
        Apply fallback heuristics based on keyword analysis and emotions.

        Args:
        - user_input (str): The user's input to analyze.
        - emotion (str, optional): The user's emotional state.
        """
        self.logger.info(f"Applying fallback heuristics on user input: {user_input} with emotion: {emotion}")

        # Sample keyword associations for traits
        keyword_associations = {
            "openness": ["creative", "curious", "adventurous"],
            "conscientiousness": ["organized", "responsible", "disciplined"],
            "extraversion": ["social", "outgoing", "energetic"],
            "agreeableness": ["kind", "empathetic", "cooperative"],
            "neuroticism": ["anxious", "nervous", "moody"],
        }

        for trait, keywords in keyword_associations.items():
            match_count = sum(user_input.lower().count(keyword) for keyword in keywords)
            self.scores[trait] += match_count
            self.logger.info(f"'{trait}' heuristic match count: {match_count} (Total: {self.scores[trait]})")

        # Optionally, use emotion to adjust scores
        if emotion:
            self.logger.info(f"Adjusting scores based on emotion: {emotion}")
            emotion_influence = {
                "happy": {"extraversion": 1, "agreeableness": 1},
                "sad": {"neuroticism": 1},
                "angry": {"neuroticism": 1, "agreeableness": -1},
                "neutral": {},
            }
            for trait, influence in emotion_influence.get(emotion, {}).items():
                self.scores[trait] += influence
                self.logger.info(f"Emotion adjustment: {trait} += {influence} (Total: {self.scores[trait]})")

    def summarize_scores(self):
        """Summarize the scores for all traits."""
        summary = "\n".join([f"{trait.capitalize()}: {score}" for trait, score in self.scores.items()])
        self.logger.info(f"Summarized scores: {summary}")
        return summary
