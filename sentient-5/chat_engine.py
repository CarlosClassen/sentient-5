from prompt_manager import PromptManager
from scoring_system import ScoringSystem

class ChatEngine:
    def __init__(self, ollama_model):
        self.model = ollama_model
        self.conversation_history = []  # Shared memory for conversation
        self.current_stage = "greeting"
        self.prompt_manager = PromptManager()
        self.scoring_system = ScoringSystem()

    def reset(self):
        """Reset the conversation engine state."""
        self.conversation_history = []
        self.current_stage = "greeting"
        self.scoring_system.reset()

    def run_conversation(self, ui):
        """Run the conversation stages in sequence."""
        ui.display_idle_screen()
        ui.display_loading_screen()

        # Initial greeting stage setup
        self.prompt_manager.inject_stage_prompt(self.current_stage, self.conversation_history, self.model)
        ui.display_message("Hello, I am Sentient-5. How are you feeling today?")

        while True:
            if self.current_stage == "greeting":
                self.stage_greeting(ui)
            elif self.current_stage == "assessment":
                self.transition_to_stage("assessment", ui)
                self.stage_assessment(ui)
            elif self.current_stage == "katarsis":
                self.transition_to_stage("katarsis", ui)
                self.stage_katarsis(ui)
                break

    def transition_to_stage(self, stage, ui, user_input=None):
        """Handle transition to a new stage, discarding the model's transition response."""
        self.prompt_manager.inject_stage_prompt(stage, self.conversation_history, self.model, user_input=user_input)
        # Discard the transition response from the model

        self.current_stage = stage

    def stage_greeting(self, ui):
        """Greeting stage: Build rapport with the user."""
        last_input = None
        for _ in range(3):  # Limit greeting to 3 exchanges
            user_input = ui.get_user_input()
            if not user_input:
                continue
            self.conversation_history.append({"role": "user", "content": user_input})
            response = self.prompt_manager.generate_response(self.conversation_history, self.model)
            self.conversation_history.append({"role": "sentient", "content": response})
            ui.display_message(response)
            last_input = user_input  # Capture the final input

        # Combine the last input with the stage prompt for assessment
        self.prompt_manager.inject_stage_prompt(
            "assessment", self.conversation_history, self.model, user_input=last_input
        )
        self.current_stage = "assessment"

    def stage_assessment(self, ui):
        """Assessment stage: Ask trait-specific questions."""
        last_input = None
        for trait, questions in self.prompt_manager.load_questions_by_trait().items():
            for question in questions:
                self.conversation_history.append({"role": "user", "content": question})
                response = self.prompt_manager.generate_response(self.conversation_history, self.model, trait)
                self.conversation_history.append({"role": "sentient", "content": response})
                ui.display_message(response)

                user_input = ui.get_user_input()
                if not user_input:
                    continue
                self.conversation_history.append({"role": "user", "content": user_input})
                self.scoring_system.update_scores(trait, user_input)
                last_input = user_input  # Capture the final input

        # Combine the last input with the stage prompt for katarsis
        self.prompt_manager.inject_stage_prompt(
            "katarsis", self.conversation_history, self.model, user_input=last_input
        )
        self.current_stage = "katarsis"

    def stage_katarsis(self, ui):
        """Katarsis stage: Summarize the effects."""
        summary = self.scoring_system.summarize_scores()
        ui.display_message("Here’s what I’ve learned about you:\n" + summary)

        critique = self.prompt_manager.generate_critique(summary, self.conversation_history, self.model)
        ui.display_message(critique)

