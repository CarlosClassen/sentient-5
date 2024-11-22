import json
import os


import json
import os


class PromptManager:
    def __init__(self, prompts_path=None, settings_path=None, logger=None):
        """Initialize PromptManager."""
        self.prompts_path = prompts_path
        self.settings_path = settings_path
        self.logger = logger

        self.logger.info("Initializing PromptManager.") if self.logger else None
        self.prompts = self.load_prompts()
        self.stage_prompts = self.load_stage_prompts()

    def load_prompts(self):
        """Load prompts from the prompts.json file."""
        self.logger.info(f"Loading prompts from: {self.prompts_path}") if self.logger else None

        if not os.path.exists(self.prompts_path):
            error_msg = f"Prompts file not found: {self.prompts_path}"
            self.logger.error(error_msg) if self.logger else None
            raise FileNotFoundError(error_msg)

        with open(self.prompts_path, "r") as file:
            prompts = json.load(file)

        if not isinstance(prompts, dict) or not prompts:
            error_msg = "Prompts file is empty or invalid."
            self.logger.error(error_msg) if self.logger else None
            raise ValueError(error_msg)

        self.logger.info("Prompts successfully loaded.") if self.logger else None
        return prompts

    def load_stage_prompts(self):
        """Load stage prompts from the settings.json file."""
        self.logger.info(f"Loading stage prompts from: {self.settings_path}") if self.logger else None

        if not os.path.exists(self.settings_path):
            error_msg = f"Settings file not found: {self.settings_path}"
            self.logger.error(error_msg) if self.logger else None
            raise FileNotFoundError(error_msg)

        with open(self.settings_path, "r") as file:
            settings = json.load(file)

        if "stage_prompts" not in settings:
            error_msg = "Stage prompts are missing in the settings file."
            self.logger.error(error_msg) if self.logger else None
            raise ValueError(error_msg)

        self.logger.info("Stage prompts successfully loaded.") if self.logger else None
        return settings["stage_prompts"]

    def inject_stage_prompt(self, stage, conversation_history, model, user_input=None):
        """
        Inject the stage-specific system prompt, optionally including the user's last input.
        """
        self.logger.info(f"Injecting stage prompt for stage: {stage}") if self.logger else None

        if stage not in self.stage_prompts:
            error_msg = f"Stage '{stage}' not found in stage_prompts."
            self.logger.error(error_msg) if self.logger else None
            raise ValueError(error_msg)

        # Dynamically include the user's input in the stage prompt, if provided
        stage_prompt = self.stage_prompts[stage]
        if user_input:
            stage_prompt = stage_prompt.replace("{last_input}", user_input.strip())

        # Append the stage prompt to the conversation history
        conversation_history.append({"role": "system", "content": stage_prompt})

        # Generate the stage transition response (discarded later)
        response = model.chat(
            model="llama3.2",
            messages=conversation_history
        )
        self.logger.info(f"Stage transition response generated: {response}") if self.logger else None

    def generate_response(self, conversation_history, model, trait=None):
        """
        Generate a response from the model based on the conversation history and optional trait.
        """
        self.logger.info(f"Generating response for trait: {trait}") if self.logger else None

        context = f"Trait: {trait}. " if trait else ""
        response = model.chat(
            model="llama3.2",
            messages=conversation_history + [{"role": "user", "content": context}]
        )
        self.logger.info(f"Response generated: {response['message']['content']}") if self.logger else None
        return response["message"]["content"].strip()

    def generate_intermediate_prompt(self, trait, emotion, last_response):
        """
        Generate an intermediate prompt to guide the model in asking the next question for the user.
        """
        self.logger.info(f"Generating intermediate prompt for trait: {trait}, emotion: {emotion}")

        # Template for intermediate prompts
        intermediate_prompt = (
            f"Based on the user's emotional state ('{emotion}') and the trait being assessed ('{trait}'), "
            f"construct the next question for the user. The prior AI response was: '{last_response}'. "
            "The next question should engage the user, be concise, and remain focused on the current trait. "
            "Avoid generating self-contained responses or statements unrelated to the user's input."
        )
        self.logger.info(f"Intermediate prompt generated: {intermediate_prompt}")
        return intermediate_prompt

    def generate_katarsis(self, summary, conversation_history, model):
        """Generate an ironic critique based on the user's personality summary using the katarsis stage prompt."""
        self.logger.info("Generating katarsis response.") if self.logger else None

        if "katarsis" not in self.stage_prompts:
            error_msg = "Katarsis stage prompt not found in stage_prompts."
            self.logger.error(error_msg) if self.logger else None
            raise ValueError(error_msg)

        # Inject the summary into the katarsis prompt
        katarsis_prompt = self.stage_prompts["katarsis"].replace("{summary}", summary)

        # Append the katarsis prompt as part of the conversation history
        conversation_history.append({"role": "user", "content": katarsis_prompt})

        # Generate the katarsis response
        response = model.chat(
            model="llama3.2",
            messages=conversation_history
        )
        self.logger.info(f"Katarsis response generated: {response['message']['content']}") if self.logger else None
        return response["message"]["content"].strip()

    def load_questions_by_trait(self):
        """Load questions organized by trait from prompts.json."""
        self.logger.info("Loading questions by trait.") if self.logger else None

        if not self.prompts:
            error_msg = "Prompts are not loaded or empty."
            self.logger.error(error_msg) if self.logger else None
            raise ValueError(error_msg)

        self.logger.info("Questions by trait successfully loaded.") if self.logger else None
        return self.prompts  # Assumes prompts.json is structured as a dictionary of traits to lists of questions
