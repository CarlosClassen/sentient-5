import argparse
import os
import threading
import ollama
from sentient_five.dialog_engine import DialogEngine
from sentient_five.assessment_engine import AssessmentEngine
from sentient_five.emotion_engine import EmotionEngine
from sentient_five.prompt_manager import PromptManager
from sentient_five.scoring_system import ScoringSystem
from sentient_five.utils import TerminalUI, Logger


class SentientApp:
    def __init__(self, dialog_model, dialog_model_name, assessment_model, assessment_model_name, settings_path, questions_path, log_file):
        """Initialize the SentientApp."""
        self.logger = Logger(log_file=log_file, module_name="Main").get_logger()
        self.logger.info("Initializing SentientApp...")

        # Initialize TerminalUI
        self.ui = TerminalUI()
        
        # Initialize PromptManager
        self.prompt_manager = PromptManager(
            settings_path=settings_path,
            questions_path=questions_path,
            logger=Logger(log_file=log_file, module_name="PromptManager").get_logger(),
        )

        # Initialize EmotionEngine
        self.emotion_engine = EmotionEngine(
            settings_file=settings_path,
            logger=Logger(log_file=log_file, module_name="EmotionEngine").get_logger(),
        )

        # Initialize ScoringSystem
        scoring_system = ScoringSystem(
            logger=Logger(log_file=log_file, module_name="ScoringSystem").get_logger(),
        )

        # Initialize AssessmentEngine
        self.assessment_engine = AssessmentEngine(
            ollama_model=assessment_model,
            model_name=assessment_model_name,
            prompt_manager=self.prompt_manager,
            scoring_system=scoring_system,  # Pass scoring system here
            emotion_engine=self.emotion_engine,
            logger=Logger(log_file=log_file, module_name="AssessmentEngine").get_logger(),
        )


        # Initialize DialogEngine
        self.dialog_engine = DialogEngine(
            ollama_model=dialog_model,
            model_name=dialog_model_name,
            prompt_manager=self.prompt_manager,
            emotion_engine=self.emotion_engine,
            assessment_engine=self.assessment_engine,
            logger=Logger(log_file=log_file, module_name="DialogEngine").get_logger(),
        )

        # Inactivity timer
        self.inactivity_timer = None
        self.logger.info("SentientApp initialized.")


    def reset(self):
        """Reset the application to IDLE state."""
        self.logger.info("Resetting the application to IDLE state.")
        self.dialog_engine.reset()
        self.ui.display_idle_screen()

    def start_inactivity_timer(self):
        """Start or reset the inactivity timer."""
        if self.inactivity_timer:
            self.inactivity_timer.cancel()  # Stop any previous timer
        self.logger.info("Starting inactivity timer (42 seconds).")
        self.inactivity_timer = threading.Timer(42, self.reset)
        self.inactivity_timer.start()

    def stop_inactivity_timer(self):
        """Stop the inactivity timer."""
        if self.inactivity_timer:
            self.logger.info("Stopping inactivity timer.")
            self.inactivity_timer.cancel()
            self.inactivity_timer = None

    def run(self):
        """Run the SentientApp."""
        self.logger.info("Displaying idle screen.")
        self.ui.display_idle_screen()

        try:
            # Start the dialog flow
            self.logger.info("Running the dialog flow.")
            self.dialog_engine.run_conversation(self.ui)

            # Transition to the assessment flow
            self.logger.info("Running the assessment flow.")
            self.assessment_engine.run_assessment(self.ui)

        except Exception:
            self.logger.exception("An unexpected error occurred during the application flow:")
            self.ui.display_message("An error occurred. Please restart the application.")
            self.reset()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Sentient interactive installation.")
    parser.add_argument("--dialog_model_name", type=str, default="llama3.2", help="The name of the dialog model to use.")
    parser.add_argument("--assessment_model_name", type=str, default="llama3.2", help="The name of the assessment model to use.")
    parser.add_argument(
        "--settings_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "settings.json"),
        help="Path to the settings JSON file.",
    )
    parser.add_argument(
        "--questions_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "questions.json"),
        help="Path to the questions JSON file.",
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "sentient-5.log"),
        help="Path to the log file.",
    )

    args = parser.parse_args()

    # Ensure the log directory exists
    log_dir = os.path.dirname(args.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Initialize and run SentientApp
    try:
        # Create Ollama clients for both dialog and assessment models
        dialog_client = ollama.Client()
        assessment_client = ollama.Client()

        app = SentientApp(
            dialog_model=dialog_client,
            dialog_model_name=args.dialog_model_name,
            assessment_model=assessment_client,
            assessment_model_name=args.assessment_model_name,
            settings_path=args.settings_path,
            questions_path=args.questions_path,
            log_file=args.log_file,
        )
        app.run()
    except Exception:
        logger = Logger(log_file=args.log_file, module_name="Main").get_logger()
        logger.exception("Critical failure during application initialization or runtime:")
