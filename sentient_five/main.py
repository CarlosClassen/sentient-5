import argparse
import os
import threading
import ollama
from sentient_five.chat_engine import ChatEngine
from sentient_five.emotion_engine import EmotionEngine
from sentient_five.prompt_manager import PromptManager
from sentient_five.scoring_system import ScoringSystem
from sentient_five.utils import TerminalUI, Logger


class SentientApp:
    def __init__(self, ollama_model, settings_path, prompts_path, stimuli_path, log_file):
        """Initialize the SentientApp."""
        self.logger = Logger(log_file=log_file, module_name="Main").get_logger()
        self.logger.info("Initializing SentientApp...")

        # Initialize TerminalUI and ollama model
        self.ui = TerminalUI()
        self.model = ollama

        # Initialize PromptManager
        self.prompt_manager = PromptManager(
            prompts_path=prompts_path,
            settings_path=settings_path,
            logger=Logger(log_file=log_file, module_name="PromptManager").get_logger(),
        )

        # Initialize EmotionEngine
        self.emotion_engine = EmotionEngine(
            settings_file=settings_path,
            logger=Logger(log_file=log_file, module_name="EmotionEngine").get_logger(),
        )

        # Initialize ScoringSystem
        self.scoring_system = ScoringSystem(
            logger=Logger(log_file=log_file, module_name="ScoringSystem").get_logger(),
        )

        # Initialize ChatEngine
        self.chat_engine = ChatEngine(
            ollama_model=self.model,
            settings_path=settings_path,
            prompts_path=prompts_path,
            stimuli_path=stimuli_path,
            prompt_manager=self.prompt_manager,
            emotion_engine=self.emotion_engine,
            scoring_system=self.scoring_system,
            logger=Logger(log_file=log_file, module_name="ChatEngine").get_logger(),
        )


        # Inactivity timer
        self.inactivity_timer = None
        self.logger.info("SentientApp initialized.")

    def reset(self):
        """Reset the application to IDLE state."""
        self.logger.info("Resetting the application to IDLE state.")
        self.chat_engine.reset()
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
            self.logger.info("Running the conversation flow.")
            self.chat_engine.run_conversation(self.ui)
        except Exception as e:
            self.logger.exception("An unexpected error occurred during the conversation flow:")
            self.ui.display_message("An error occurred. Please restart the application.")
            self.reset()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Sentient interactive installation.")
    parser.add_argument("--ollama_model", type=str, default="llama3.2", help="The Ollama model to use.")
    parser.add_argument(
        "--settings_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "settings.json"),
        help="Path to the settings JSON file.",
    )
    parser.add_argument(
        "--prompts_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "prompts.json"),
        help="Path to the prompts JSON file.",
    )
    parser.add_argument(
        "--stimuli_path",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "data", "stimuli.json"),
        help="Path to the stimuli JSON file.",
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
        app = SentientApp(
            ollama_model=args.ollama_model,
            settings_path=args.settings_path,
            prompts_path=args.prompts_path,
            stimuli_path=args.stimuli_path,
            log_file=args.log_file,
        )
        app.run()
    except Exception as e:
        logger = Logger(log_file=args.log_file, module_name="Main").get_logger()
        logger.exception("Critical failure during application initialization or runtime:")
