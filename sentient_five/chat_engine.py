class ChatEngine:
    def __init__(self, ollama_model, settings_path, prompts_path, stimuli_path, prompt_manager, emotion_engine, scoring_system, logger):
        """Initialize ChatEngine."""
        self.model = ollama_model
        self.conversation_history = []
        self.current_stage = "greeting"
        self.prompt_manager = prompt_manager
        self.emotion_engine = emotion_engine
        self.scoring_system = scoring_system
        self.logger = logger

        self.logger.info("ChatEngine initialized.")

    def reset(self):
        """Reset the conversation engine state."""
        self.logger.info("Resetting ChatEngine.")
        self.conversation_history = []
        self.current_stage = "greeting"
        self.scoring_system.reset()

    def run_conversation(self, ui):
        """Run the conversation stages in sequence."""
        self.logger.info("Starting conversation loop.")
        ui.display_idle_screen()
        ui.display_loading_screen()

        self.logger.info(f"Injecting stage prompt for: {self.current_stage}")
        self.prompt_manager.inject_stage_prompt(self.current_stage, self.conversation_history, self.model)
        ui.display_message("Hello, I am Sentient-5. How are you feeling today?")

        while True:
            try:
                if self.current_stage == "greeting":
                    self.stage_greeting(ui)
                elif self.current_stage == "assessment":
                    self.transition_to_stage("assessment", ui)
                    self.stage_assessment(ui)
                elif self.current_stage == "katarsis":
                    self.transition_to_stage("katarsis", ui)
                    self.stage_katarsis(ui)
                    break
            except Exception as e:
                self.logger.exception("Error during conversation:")
                ui.display_message("An unexpected error occurred. Please restart the application.")
                break

    def transition_to_stage(self, stage, ui, user_input=None):
        if self.current_stage == stage:
            self.logger.warning(f"Already in stage: {stage}. Skipping transition.")
            return

        try:
            self.logger.info(f"Transitioning to stage: {stage}")
            self.prompt_manager.inject_stage_prompt(stage, self.conversation_history, self.model, user_input=user_input)
            self.current_stage = stage
        except Exception as e:
            self.logger.error(f"Error during stage transition: {e}")
            ui.display_message("An error occurred during stage transition. Please restart the application.")


    def log_emotion_after_response(self, response):
        """Log the emotion after Sentient-5's response."""
        self.logger.info(f"Logging emotion for response: {response}")
        try:
            img_path = self.emotion_engine.capture_image()
            emotion = self.emotion_engine.analyze_emotion(img_path)
            if emotion:
                self.emotion_engine.log_emotion(response, emotion)
                self.logger.info(f"Emotion logged: {emotion}")
            return emotion
        except Exception as e:
            self.logger.error(f"Error logging emotion: {e}")
            return "neutral"  # Default fallback emotion

    def stage_greeting(self, ui):
        """Greeting stage: Build rapport with the user."""
        self.logger.info("Entering greeting stage.")
        last_input = None

        for _ in range(2):  # Limit greeting to 2 exchanges
            # Get user input
            user_input = ui.get_user_input()
            if not user_input:
                self.logger.warning("No user input received; skipping to next iteration.")
                continue

            self.logger.info(f"User input received: {user_input}")
            self.conversation_history.append({"role": "user", "content": user_input})

            # For the final user input in the greeting stage, encapsulate with guidance
            if _ == 1:  # On the third (final) interaction
                self.logger.info("Encapsulating user input with plain response instruction.")
                instruction = (
                    f"You are now concluding the greeting phase. The user said: '{user_input}'. "
                    "Do not ask any new questions. Simply and plainly address their input, answering any earlier questions if applicable. "
                    "Your response should end this phase cleanly. Don't mention the word 'greeting phase' in your response."
                )
                response = self.prompt_manager.generate_response(
                    [{"role": "system", "content": instruction}], self.model
                )
            else:
                # Standard AI response generation
                response = self.prompt_manager.generate_response(self.conversation_history, self.model)

            self.logger.info(f"Sentient-5 response generated: {response}")
            self.conversation_history.append({"role": "sentient", "content": response})
            ui.display_message(response)

            # Log emotion for the response
            emotion = self.log_emotion_after_response(response)
            self.logger.info(f"Captured emotion for greeting: {emotion}")
            last_input = user_input

        # Transition to the next stage with the final user input
        self.prompt_manager.inject_stage_prompt(
            "assessment", self.conversation_history, self.model, user_input=last_input
        )
        self.current_stage = "assessment"

    def stage_assessment(self, ui):
        """Assessment stage with orientation questions, intermediate prompts, and trait scoring."""
        self.logger.info("Entering assessment stage.")
        last_input = None

        for trait, questions in self.prompt_manager.load_questions_by_trait().items():
            for question in questions:
                # Inject orientation question as part of the stage prompt
                self.logger.info(f"Asking orientation question for trait '{trait}': {question}")
                orientation_prompt = (
                    f"You are assessing the user's personality traits during the assessment stage. "
                    f"The current trait is '{trait}'. Using the following orientation question: '{question}', "
                    "formulate a question for the user to help evaluate this trait."
                )

                # Generate model's question to the user
                generated_question = self.prompt_manager.generate_response(
                    [{"role": "system", "content": orientation_prompt}],
                    self.model
                )
                self.logger.info(f"Generated question for user: {generated_question}")

                # User responds
                user_input = ui.get_user_input()
                if not user_input:
                    self.logger.warning("No user input received; skipping to next question.")
                    continue

                self.logger.info(f"User input received: {user_input}")
                self.conversation_history.append({"role": "user", "content": user_input})

                # Analyze emotion from the user's response
                emotion = self.log_emotion_after_response(user_input)
                self.logger.info(f"Emotion detected: {emotion}")

                # Craft an intermediate prompt to interpret traits
                intermediate_prompt = (
                    f"In our last exchange, the user's dominant emotion was '{emotion}'. "
                    f"Their response was: '{user_input}'. Considering the trait '{trait}', "
                    "analyze this response and describe what it reveals about the user's personality. "
                    "Focus on the trait and provide a detailed analysis."
                )
                self.logger.info(f"Intermediate prompt crafted: {intermediate_prompt}")

                # Generate trait estimation from the model
                trait_estimation = self.prompt_manager.generate_response(
                    [{"role": "system", "content": intermediate_prompt}],
                    self.model
                )
                self.logger.info(f"Trait estimation generated: {trait_estimation}")
                ui.display_message(trait_estimation)

                # Update scoring system based on user input and trait estimation
                self.scoring_system.update_scores(trait, user_input)
                last_input = user_input  # Capture the most recent input for the stage

        # Transition to the next stage with the last input
        self.prompt_manager.inject_stage_prompt(
            "katarsis", self.conversation_history, self.model, user_input=last_input
        )
        self.current_stage = "katarsis"



    def stage_katarsis(self, ui):
        """Katarsis stage summarizing personality insights."""
        self.logger.info("Entering katarsis stage.")
        try:
            summary = self.scoring_system.summarize_scores()
            self.logger.info(f"Personality summary generated: {summary}")
            ui.display_message("Here’s what I’ve learned about you:\n" + summary)

            critique = self.prompt_manager.generate_katarsis(summary, self.conversation_history, self.model)
            self.logger.info(f"Generated critique: {critique}")
            ui.display_message(critique)

            emotion = self.log_emotion_after_response(critique)
            self.logger.info(f"Emotion after critique: {emotion}")
        except Exception as e:
            self.logger.error(f"Error during katarsis stage: {e}")
            ui.display_message("An error occurred during the final stage. Please restart.")
