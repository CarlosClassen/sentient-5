class DialogEngine:
    def __init__(self, ollama_model, model_name, prompt_manager, emotion_engine, assessment_engine, logger):
        self.model_client = ollama_model
        self.model_name = model_name
        self.prompt_manager = prompt_manager
        self.emotion_engine = emotion_engine
        self.assessment_engine = assessment_engine
        self.conversation_history = []
        self.current_stage = "greeting"
        self.logger = logger
        self.logger.info("DialogEngine initialized.")

    def run_conversation(self, ui):
        self.logger.info("Starting dialog loop.")
        ui.display_idle_screen()
        ui.display_loading_screen()
        while self.current_stage in ["greeting", "assessment"]:
            if self.current_stage == "greeting":
                self.stage_greeting(ui)
            elif self.current_stage == "assessment":
                self.stage_assessment(ui)

    def reset(self):
        """Reset the dialog engine state."""
        self.logger.info("Resetting DialogEngine.")
        self.conversation_history = []
        self.current_stage = "greeting"

    def stage_greeting(self, ui):
        """Greeting stage: Build rapport with the user."""
        self.logger.info("Entering greeting stage.")
        
        # Load initial greeting from PromptManager
        initial_greeting = self.prompt_manager.get_initial_greeting()
        self.logger.info(f"Initial system greeting: {initial_greeting}")
        self.conversation_history.append({"role": "sentient", "content": initial_greeting})
        ui.display_message(initial_greeting)

        for _ in range(2):  # Two exchanges for greeting
            user_input = ui.get_user_input()
            if not user_input:
                self.logger.warning("No user input received; skipping.")
                continue

            self.logger.info(f"User input received: {user_input}")
            self.conversation_history.append({"role": "user", "content": user_input})

            # Construct a control prompt for the greeting stage
            greeting_prompt = self.prompt_manager.construct_control_prompt(
                stage="greeting",
                context=self.conversation_history,
            )
            self.logger.info("Sending control prompt for greeting stage.")

            # Package prompt into the correct format for the model
            messages = [{"role": "system", "content": greeting_prompt}] + self.conversation_history

            # Generate a response
            response = self.generate_response(messages)
            self.logger.info(f"Dialog response generated: {response}")
            self.conversation_history.append({"role": "sentient", "content": response})
            ui.display_message(response)

            # Transition to assessment stage
            self.current_stage = "assessment"

    def stage_assessment(self, ui):
        """Assessment stage: Ask trait-specific questions dynamically."""
        self.logger.info("Entering assessment stage.")

        while True:
            # Fetch the next trait and question dynamically
            trait, question = self.prompt_manager.get_next_trait_and_question()
            if not trait or not question:
                self.logger.info("All traits assessed. Transitioning to Katharsis stage.")
                self.current_stage = "katharsis"
                break

            # Construct the control prompt for the question
            control_prompt = self.prompt_manager.construct_control_prompt(
                stage="assessment_question",
                context=self.conversation_history,
                target=question
            )
            self.logger.info(f"Control prompt for assessment question: {control_prompt}")

            # Generate the question dynamically
            messages = [{"role": "system", "content": control_prompt}] + self.conversation_history
            response = self.generate_response(messages)
            self.logger.info(f"Generated question for '{trait}': {response}")
            ui.display_message(response)

            # Capture user response
            user_input = ui.get_user_input("Your response:")
            if not user_input:
                self.logger.warning("No user input received; skipping to next question.")
                continue

            self.logger.info(f"User response: {user_input}")
            emotion = self.log_emotion_after_response(user_input)

            # Package metadata for the assessment engine
            metadata = self.prompt_manager.package_exchange_metadata(trait, question, user_input, emotion)
            self.logger.info(f"Metadata prepared: {metadata}")
            self.assessment_engine.process_metadata(metadata)

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})

    def stage_katharsis(self, ui):
        """Final reflection stage using assessment results."""
        self.logger.info("Entering Katharsis stage.")

        # Retrieve assessment results
        assessment_results = self.assessment_engine.scoring_system.get_results()
        self.logger.info(f"Assessment results: {assessment_results}")

        # Construct the reflection prompt
        katharsis_prompt = self.prompt_manager.construct_reflection_prompt(assessment_results)
        self.logger.info(f"Katharsis prompt constructed: {katharsis_prompt}")

        # Generate the Katharsis message dynamically
        messages = [{"role": "system", "content": katharsis_prompt}]
        reflection = self.generate_response(messages)
        ui.display_message(reflection)


    def generate_response(self, messages):
        """Generate a response using the dialog model."""
        self.logger.info("Generating response using the dialog model.")
        response = self.model_client.chat(model=self.model_name, messages=messages, stream=False)
        return response["message"]["content"]

    def log_emotion_after_response(self, response):
        """Log emotion for Sentient-5's responses."""
        try:
            img_path = self.emotion_engine.capture_image()
            emotion = self.emotion_engine.analyze_emotion(img_path)
            self.emotion_engine.log_emotion(response, emotion)
            return emotion
        except Exception as e:
            self.logger.error(f"Error logging emotion: {e}")
            return "neutral"
