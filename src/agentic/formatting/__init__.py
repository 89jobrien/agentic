from .console import console
from .formatters import CLIFormatter

# Create a single, globally accessible formatter instance
writer = CLIFormatter(console)