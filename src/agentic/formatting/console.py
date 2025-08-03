from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Define a more detailed theme
custom_theme = Theme({
    "info": "dim cyan",
    "success": "green",
    "warning": "yellow",
    "danger": "bold red",
    "path": "italic blue",
    "repr": "dim white",
    "ai": "green",
    "progress.bar": "green",
    "progress.percentage": "bold green",
    "progress.description": "default",
})

# Create the shared console instance
console = Console(theme=custom_theme)


def get_rich_handler() -> RichHandler:
    """Returns a pre-configured RichHandler for logging."""
    return RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_path=False, # The logger format already includes the path
    )