from src.agentic.formatting.console import console, get_rich_handler
from src.agentic.formatting.formatters import CLIFormatter

def test_console_and_formatter():
    assert console is not None
    formatter = CLIFormatter(console)
    formatter.write("Test message", style="success")
    formatter.aiwrite("## Hello\nThis is a test.")
    assert callable(get_rich_handler)
