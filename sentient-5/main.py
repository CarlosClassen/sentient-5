import argparse
import threading
import ollama
from chat_engine import ChatEngine
from utils import TerminalUI

class SentientApp:
    def __init__(self, ollama_model):
        self.ui = TerminalUI()
        self.model = ollama
        self.chat_engine = ChatEngine(self.model)
        self.inactivity_timer = None

    def reset(self):
        """Reset the app to IDLE screen."""
        self.chat_engine.reset()
        self.ui.display_idle_screen()

    def start_inactivity_timer(self):
        """Start or reset the inactivity timer."""
        if self.inactivity_timer:
            self.inactivity_timer.cancel()  # Stop any previous timer
        self.inactivity_timer = threading.Timer(42, self.reset)
        self.inactivity_timer.start()

    def stop_inactivity_timer(self):
        """Stop the inactivity timer."""
        if self.inactivity_timer:
            self.inactivity_timer.cancel()
            self.inactivity_timer = None

    def run(self):
        """Run the application."""
        self.ui.display_idle_screen()
        self.chat_engine.run_conversation(self.ui)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Sentient interactive installation.")
    parser.add_argument("--ollama_model", type=str, default="llama3.2", help="The Ollama model to use.")
    args = parser.parse_args()

    app = SentientApp(args.ollama_model)
    app.run()
