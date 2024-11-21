import json
import os


class PromptManager:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this script
        self.prompts = self.load_prompts()
        self.stage_prompts = self.load_stage_prompts()

    def load_prompts(self):
        """Load prompts from the prompts.json file."""
        prompts_path = os.path.join(self.base_path, "data", "prompts.json")
        with open(prompts_path, "r") as file:
            return json.load(file)

    def load_stage_prompts(self):
        """Load stage prompts from the settings.json file."""
        settings_path = os.path.join(self.base_path, "data", "settings.json")
        with open(settings_path, "r") as file:
            settings = json.load(file)
            return settings["stage_prompts"]

    def inject_stage_prompt(self, stage, conversation_history, model, user_input=None):
        """Inject the stage-specific system prompt, optionally including the user's last input."""
        if stage not in self.stage_prompts:
            raise ValueError(f"Stage '{stage}' not found in stage_prompts.")

        # Dynamically include the user's input in the stage prompt, if provided
        stage_prompt = self.stage_prompts[stage]
        if user_input:
            stage_prompt = stage_prompt.replace("{last_input}", user_input.strip())

        # Append the stage prompt to the conversation history
        conversation_history.append({"role": "system", "content": stage_prompt})

        # Generate the stage transition response (discarded later)
        model.chat(
            model="llama3.2",
            messages=conversation_history
        )



    def generate_response(self, conversation_history, model, trait=None):
        """Generate a response from the model."""
        context = f"Trait: {trait}. " if trait else ""
        response = model.chat(
            model="llama3.2",  # Specify the model name here explicitly
            messages=conversation_history + [{"role": "user", "content": context}]
        )
        return response["message"]["content"].strip()

    def load_questions_by_trait(self):
        """Load questions organized by trait from prompts.json."""
        if not self.prompts:
            raise ValueError("Prompts are not loaded or empty.")
        return self.prompts  # Assumes prompts.json is structured as a dictionary of traits to lists of questions
    
    def generate_katarsis(self, summary, conversation_history, model):
        """Generate an ironic critique based on the user's personality summary using the katarsis stage prompt."""
        # Retrieve the katarsis stage prompt from settings
        if "katarsis" not in self.stage_prompts:
            raise ValueError("Katarsis stage prompt not found in stage_prompts.")

        # Inject the summary into the katarsis prompt
        katarsis_prompt = self.stage_prompts["katarsis"].replace("{summary}", summary)

        # Append the katarsis prompt as part of the conversation history
        conversation_history.append({"role": "user", "content": katarsis_prompt})
        
        # Generate the katarsis response
        response = model.chat(
            model="llama3.2",
            messages=conversation_history
        )
        
        # Return the stripped response content
        return response["message"]["content"].strip()


