from rich.console import Console
from constants import ASCII_ARTS
import sys
import select
import time


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
        """Displays the idle state with cycling ASCII art until user interaction is detected."""
        self.console.clear()
        art_keys = list(ASCII_ARTS.keys())
        current_index = 0

        self.hide_cursor()  # Hide cursor for screensaver effect
        try:
            while True:
                art_key = art_keys[current_index]
                self.console.print(ASCII_ARTS[art_key], style="bold green")
                time.sleep(1)
                self.console.clear()
                time.sleep(0.5)

                if self.check_for_input():
                    self.clear_input_buffer()  # Clear lingering inputs
                    self.console.clear()
                    return

                current_index = (current_index + 1) % len(art_keys)
        finally:
            self.show_cursor()


    def check_for_input(self):
        """Non-blocking input detection."""
        return select.select([sys.stdin], [], [], 0)[0]


    def display_loading_screen(self):
        """Display a loading screen during initialization."""
        self.console.clear()
        self.console.print("[bold red]Initializing System...[/bold red]")
        time.sleep(3)
        self.clear_input_buffer()  # Clear lingering inputs

    def clear_input_buffer(self):
        """Flush the input buffer to discard unintended inputs."""
        try:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)  # Flush input buffer
        except Exception:
            pass


    def get_user_input(self, prompt="> "):
        """Prompt the user for input and wait for enter."""
        user_input = self.console.input(f"[bold white]{prompt}[/bold white]").strip()
        if not user_input:
            return None  # Handle empty input gracefully
        return user_input

    def display_message(self, message):
        """Display a generic message with visual spacing."""
        self.console.print("\n\n" + f"[bold green]{message}[/bold green]")

    def display_exit_message(self):
        """Display an exit message."""
        self.console.print("\n[bold red]Session complete. Thank you for participating![/bold red]\n")
