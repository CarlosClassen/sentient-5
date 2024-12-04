class AssessmentEngine:
    def __init__(self, ollama_model, model_name, prompt_manager, scoring_system, emotion_engine, logger):
        """Initialize AssessmentEngine."""
        self.model_client = ollama_model
        self.model_name = model_name
        self.prompt_manager = prompt_manager
        self.scoring_system = scoring_system
        self.emotion_engine = emotion_engine
        self.assessment_results = []
        self.logger = logger
        self.logger.info("AssessmentEngine initialized.")


    def process_metadata(self, metadata):
        self.logger.info(f"Processing metadata: {metadata}")
        trait, question, user_response, emotion = metadata.values()
        analysis_prompt = self.prompt_manager.construct_analysis_prompt(trait, question, user_response, emotion)
        analysis_response = self.model_client.chat(
            model=self.model_name,
            messages=[{"role": "system", "content": analysis_prompt}],
            stream=False,
        )
        self.assessment_results.append({
            "trait": trait,
            "analysis": analysis_response["message"]["content"]
        })
        self.logger.info(f"Analysis complete for trait: {trait}")


    def run_assessment(self, ui):
        """Run the assessment stage."""
        self.logger.info("Starting assessment stage.")

        for trait, questions in self.prompt_manager.load_questions_by_trait().items():
            for question in questions:
                self.logger.info(f"Asking question for trait '{trait}': {question}")
                generated_question = self.generate_trait_question(trait, question)
                ui.display_message(generated_question)

                user_input = ui.get_user_input("Your response:")
                if not user_input:
                    self.logger.warning("No user input received; skipping to next question.")
                    continue

                self.logger.info(f"User response: {user_input}")
                emotion = self.log_emotion_after_response(user_input)
                trait_analysis = self.generate_trait_analysis(trait, user_input, emotion)
                ui.display_message(trait_analysis)

                self.scoring_system.update_scores(trait, trait_analysis)

    def generate_trait_question(self, trait, base_question):
        """Generate a user-facing question for assessing a trait."""
        self.logger.info(f"Generating question for trait: {trait}")
        question_prompt = (
            f"Using the base question '{base_question}', craft a concise question to assess the trait '{trait}'."
        )
        response = self.model_client.chat(
            model=self.model_name, 
            messages=[{"role": "system", "content": question_prompt}],
            stream=False
        )
        return response["message"]["content"]

    def generate_trait_analysis(self, trait, user_input, emotion):
        """Generate trait analysis based on user input and emotion."""
        analysis_prompt = (
            f"The user's response was: '{user_input}', with detected emotion: '{emotion}'. "
            f"Analyze this response in terms of the trait '{trait}'. Provide a detailed, standardized analysis."
        )
        response = self.model_client.chat(
            model=self.model_name,
            messages=[{"role": "system", "content": analysis_prompt}],
            stream=False
        )
        return response["message"]["content"]

    def log_emotion_after_response(self, user_input):
        """Analyze and log emotion for user input."""
        try:
            img_path = self.emotion_engine.capture_image()
            emotion = self.emotion_engine.analyze_emotion(img_path)
            self.emotion_engine.log_emotion(user_input, emotion)
            return emotion
        except Exception as e:
            self.logger.error(f"Error logging emotion: {e}")
            return "neutral"