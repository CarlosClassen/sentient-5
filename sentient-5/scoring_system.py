class ScoringSystem:
    def __init__(self):
        self.traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
        self.scores = {trait: 0 for trait in self.traits}

    def reset(self):
        self.scores = {trait: 0 for trait in self.traits}

    def update_scores(self, trait, user_input):
        """Update scores based on Ollama's analysis of user input."""
        scoring_prompt = (
            f"On a scale of -1 to +1, score the user's response for trait '{trait}': {user_input}"
        )
        response = self.model.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": scoring_prompt}]
        )
        score = int(response["message"]["content"].strip())
        self.scores[trait] += score

    def summarize_scores(self):
        return "\n".join([f"{trait.capitalize()}: {score}" for trait, score in self.scores.items()])
