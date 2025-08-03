from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

class CLIFormatter:
    """A class to handle standardized rich console output."""

    def __init__(self, console: Console):
        self.console = console

    def aiwrite(self, text: str):
        """Formats and prints the agent's response in a styled panel."""
        output_markdown = Markdown(text, style="ai")
        output_panel = Panel(
            output_markdown,
            title="🤖 Agent Response",
            title_align="left",
            border_style="info",
            padding=(1, 2)
        )
        self.console.print(output_panel)

    def write(self, message: str, style: str = "info"):
        """
        Prints a message to the console with a specified style.
        
        Args:
            message: The message to print.
            style: The theme style to use (e.g., "success", "warning", "danger").
        """
        self.console.print(message, style=style)