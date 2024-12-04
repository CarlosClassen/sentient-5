import json

class PromptManager:
    def __init__(self, settings_path, questions_path, logger):
        """
        Initialize PromptManager with settings and questions for dynamic prompt construction.
        """
        self.settings_path = settings_path
        self.questions_path = questions_path
        self.logger = logger
        self.logger.info("Initializing PromptManager.")
        self.settings = self.load_settings()
        self.questions = self.load_questions()
        self.language = self.settings.get("language", "en")  # Default to English
        self.stage_prompts = self.settings["stage_prompts"]
        self.assessment_state = {"completed_traits": []}  # State tracking

    def load_settings(self):
        """Load settings from a JSON file."""
        self.logger.info(f"Loading settings from: {self.settings_path}")
        with open(self.settings_path, "r") as file:
            return json.load(file)
        
    def load_questions_by_trait(self):
        """
        Load and return questions organized by trait from the questions.json file.
        """
        self.logger.info("Loading questions organized by trait.")
        try:
            return self.questions  # Ensure questions are preloaded during initialization
        except AttributeError:
            self.logger.error("Questions are not loaded correctly in PromptManager.")
            raise

    def load_questions(self):
        """Load questions from the questions JSON file."""
        self.logger.info(f"Loading questions from: {self.questions_path}")
        try:
            with open(self.questions_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.error(f"Questions file not found at {self.questions_path}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding questions JSON file at {self.questions_path}")
            raise

    # ======= Stage and Control Prompts =======
    def get_initial_greeting(self):
        """Return the initial greeting message from the settings."""
        try:
            initial_greeting = self.settings["stage_prompts"][self.language]["initial_greeting"]
            self.logger.info(f"Loaded initial greeting: {initial_greeting}")
            return initial_greeting
        except KeyError:
            self.logger.error("Initial greeting not found in settings.")
            return "Hello. I am Sentient-5. How do you feel today?"

    def get_prompt(self, stage, **kwargs):
        """
        Retrieve a stage-specific prompt.
        Replace placeholders with provided keyword arguments.
        """
        if stage not in self.stage_prompts[self.language]:
            raise ValueError(f"Stage '{stage}' not found for language '{self.language}'.")
        prompt = self.stage_prompts[self.language][stage]
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", value.strip() if value else "")
        return prompt

    def get_next_trait_and_question(self):
        """
        Select the next trait and its associated question for the assessment stage.
        """
        for trait, questions in self.questions.items():
            if trait not in self.assessment_state["completed_traits"]:
                # Mark trait as completed after the first question is retrieved
                self.assessment_state["completed_traits"].append(trait)
                return trait, questions[0]  # Return the first question for this trait
        return None, None  # No traits left

    def construct_control_prompt(self, stage, context, target=None):
        """
        Construct a control prompt based on the current stage and target.
        Args:
            stage (str): The current stage of the conversation.
            context (list): The conversation history.
            target (str, optional): The specific goal or question for the stage.
        Returns:
            str: The constructed control prompt.
        """
        self.logger.info(f"Constructing control prompt for stage: {stage}")
        
        if stage == "greeting":
            return (
                "You are Sentient-5, a conversational agent. "
                "Your role is to warmly greet the user, build rapport, and create an engaging atmosphere. "
                "Respond empathetically and naturally to the user's input."
            )
        elif stage == "assessment_transition":
            return (
                "You are transitioning the conversation from greeting to assessment. "
                "Use the context to seamlessly introduce the assessment process, starting with the following target: "
                f"'{target}'."
            )
        elif stage == "assessment_question":
            if not target:
                raise ValueError("Target question is required for 'assessment_question' stage.")
            return (
                f"You are conducting an assessment of the user. Based on the provided context, ask the following question "
                f"to evaluate the user's trait '{target}'. Ensure the tone is conversational and engaging."
            )
        elif stage == "katarsis":
            return (
                "You are explaining the findings from the assessment. Use the context to discuss how surveillance "
                "and emotion recognition could influence society and the user's life."
            )
        else:
            raise ValueError(f"Unknown stage for control prompt: {stage}")


    # ======= Conversation Management =======
    def package_exchange_metadata(self, trait, question, user_response, emotion):
        """
        Package user exchanges and metadata for assessment.
        """
        return {
            "trait": trait,
            "question": question,
            "response": user_response,
            "emotion": emotion
        }

    def generate_response(self, messages):
        """Generate a response using the dialog model."""
        self.logger.info("Generating response using the dialog model.")
        response = self.model_client.chat(model=self.model_name, messages=messages, stream=False)
        return response["message"]["content"].strip()

    # ======= Assessment and Katharsis =======
    def construct_analysis_prompt(self, trait, question, response, emotion):
        """
        Construct a prompt for analyzing user responses for a specific trait.
        """
        return (
            f"The user was asked: '{question}' about the trait '{trait}'. "
            f"Their response was: '{response}' with detected emotion: '{emotion}'. "
            "Provide a detailed evaluation of this response in the context of the trait."
        )

    def construct_reflection_prompt(self, assessment_results):
        """
        Construct a prompt for the Katharsis stage.
        """
        traits_summary = "\n".join(
            [f"- {result['trait']}: {result['analysis']}" for result in assessment_results]
        )
        return (
            "Based on the following analysis:\n"
            f"{traits_summary}\n"
            "Summarize the user's personality and reflect on the implications of such analysis "
            "for emotion recognition in technology."
        )

    def get_first_question(self):
        """Retrieve the first question for the assessment stage."""
        self.logger.info("Fetching the first question for the assessment stage.")
        questions = self.load_questions_by_trait()
        if not questions:
            raise ValueError("No questions available in questions.json.")
        
        # Retrieve the first trait and question
        first_trait = next(iter(questions))
        first_question = questions[first_trait][0]
        self.logger.info(f"First question retrieved: {first_question} (Trait: {first_trait})")
        return first_question