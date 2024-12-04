from rich.console import Console
from sentient_five.constants import ASCII_ARTS
import sys
import select
import time
import os
import shutil
import logging


class TerminalUI:
    def __init__(self):
        self.console = Console()

    def hide_cursor(self):
        """Hide the terminal cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    def show_cursor(self):
        """Show the terminal cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def display_idle_screen(self):
        """Displays the idle state with stacking ASCII art until user interaction is detected."""
        art_keys = list(ASCII_ARTS.keys())
        current_index = 0

        self.hide_cursor()
        self.console.clear()
        try:
            while True:
                art_key = art_keys[current_index]
                centered_art = self.center_text(ASCII_ARTS[art_key])
                self.console.print(centered_art, style="bold green")
                time.sleep(1)

                if self.check_for_input():
                    self.clear_input_buffer()
                    return

                current_index = (current_index + 1) % len(art_keys)
        finally:
            self.show_cursor()

    def center_text(self, text):
        """Centers ASCII art in the terminal."""
        terminal_width = shutil.get_terminal_size().columns
        lines = text.splitlines()
        centered_lines = [
            line.center(terminal_width) for line in lines
        ]
        return "\n".join(centered_lines)

    def check_for_input(self):
        """Non-blocking input detection."""
        return select.select([sys.stdin], [], [], 0.1)[0]

    def display_loading_screen(self):
        """Display a loading screen during initialization."""
        self.console.clear()
        self.console.print("[bold red]Initializing System...[/bold red]")
        time.sleep(3)
        self.clear_input_buffer()

    def clear_input_buffer(self):
        """Flush the input buffer to discard unintended inputs."""
        try:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass

    def get_user_input(self, prompt="> "):
        """Prompt the user for input and wait for enter."""
        user_input = self.console.input(f"[bold white]{prompt}[/bold white]").strip()
        if not user_input:
            return None
        return user_input

    def display_message(self, message, delay=0.05):
        """Display a message with a typewriter effect."""
        self.console.print("\n\n", end="")
        for char in message:
            self.console.print(f"[bold green]{char}[/bold green]", end="")
            time.sleep(delay)
        self.console.print("")  # Ensure newline at the end

    def display_exit_message(self):
        """Display an exit message."""
        self.console.print("\n[bold red]Session complete. Thank you for participating![/bold red]\n")



class Logger:
    """Centralized logger setup for consistent log formatting and output."""
    def __init__(self, log_file="logs/application.log", module_name="Application", level=logging.INFO):
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger(module_name)
        if not self.logger.hasHandlers():
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(level)

    def get_logger(self):
        return self.logger
