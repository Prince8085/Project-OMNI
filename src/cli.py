"""
Project OMNI - Command Line Interface
Interactive CLI for the OMNI AI agent.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.brain import OmniBrain

# Load environment variables
load_dotenv('config/.env')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Rich console for beautiful output
console = Console()


class OmniCLI:
    """Command-line interface for OMNI."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.brain = None
        self.running = False
    
    def _check_api_keys(self) -> bool:
        """Check if at least one API key is configured."""
        keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'Google': os.getenv('GOOGLE_API_KEY')
        }
        
        configured = [name for name, key in keys.items() if key and key != 'your_openai_key_here']
        
        if not configured:
            console.print("[red]❌ No API keys configured![/red]")
            console.print("\nPlease configure at least one API key in config/.env")
            console.print("Available providers: OpenAI, Anthropic, Google")
            return False
        
        console.print(f"[green]✓[/green] Configured providers: {', '.join(configured)}")
        return True
    
    def _print_welcome(self):
        """Print welcome banner."""
        welcome_text = """
# 🤖 OMNI - Omnipotent Machine Network Intelligence

Your personal AI agent with full system access via **Open Interpreter**.

**Available Commands:**
- Type any request in natural language
- `reset` - Reset conversation
- `help` - Show this help
- `quit` or `exit` - Exit OMNI

**Examples:**
- "List all Python files in this directory"
- "Create a folder called MyProject"
- "Read the contents of README.md"
- "Show my current directory"

⚠️  **Safety First:** Review generated code before execution!
"""
        console.print(Panel(Markdown(welcome_text), title="Welcome to OMNI", border_style="cyan"))
    
    def _print_help(self):
        """Print help information."""
        help_text = """
## OMNI Commands

**Natural Language Requests:**
Just type what you want to do in plain English.

**Special Commands:**
- `reset` - Clear conversation history
- `help` - Show this help message
- `quit` or `exit` - Exit OMNI

**Safety Features:**
- ✓ Code review before execution
- ✓ Permission system (Safe/Confirmation/Blocked)
- ✓ Action logging for audit trail
- ✓ Dangerous command blocking

**Tips:**
1. Be specific in your requests
2. Review generated code carefully
3. Check logs in ~/.omni/logs/
4. Use Docker sandbox for risky operations
"""
        console.print(Panel(Markdown(help_text), title="Help", border_style="yellow"))
    
    def start(self):
        """Start the interactive CLI."""
        try:
            # Print welcome banner
            self._print_welcome()
            
            # Check API keys
            if not self._check_api_keys():
                return
            
            # Initialize brain
            console.print("\n[cyan]Initializing OMNI...[/cyan]")
            self.brain = OmniBrain()
            console.print("[green]✓ Ready![/green]\n")
            
            # Main loop
            self.running = True
            while self.running:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit']:
                        if Confirm.ask("Are you sure you want to exit?"):
                            console.print("[yellow]Goodbye! 👋[/yellow]")
                            break
                        continue
                    
                    elif user_input.lower() == 'reset':
                        self.brain.reset()
                        console.print("[green]✓ Conversation reset[/green]")
                        continue
                    
                    elif user_input.lower() == 'help':
                        self._print_help()
                        continue
                    
                    # Process command
                    console.print("\n[cyan]OMNI is thinking...[/cyan]\n")
                    result = self.brain.process_command(user_input)
                    
                    # Display result
                    if result.get('success'):
                        output = result.get('output', 'No output')
                        console.print(Panel(
                            Markdown(output),
                            title="[green]✓ OMNI Response[/green]",
                            border_style="green"
                        ))
                    else:
                        error = result.get('error', 'Unknown error')
                        console.print(Panel(
                            f"[red]{error}[/red]",
                            title="[red]✗ Error[/red]",
                            border_style="red"
                        ))
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' or 'exit' to leave OMNI[/yellow]")
                    continue
                
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    logging.exception("CLI error")
        
        except Exception as e:
            console.print(f"[red]Fatal error: {e}[/red]")
            logging.exception("Fatal CLI error")
        
        finally:
            self.running = False


def main():
    """Main entry point."""
    cli = OmniCLI()
    cli.start()


if __name__ == '__main__':
    main()
