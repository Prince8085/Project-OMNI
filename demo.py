"""
Simple demo of Project OMNI - Phase 1
This is a minimal working version to demonstrate the concept.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

console = Console()


def print_welcome():
    """Print welcome banner."""
    welcome_text = """
# 🤖 OMNI Demo - Phase 1

**Project OMNI** - Your AI Agent with System Access

This is a simplified demo showing the architecture.
For full functionality, Open Interpreter needs to be properly installed.

**Current Status:**
- ✅ Project structure created
- ✅ Safety systems implemented
- ✅ File/Terminal tools ready
- ⏳ Open Interpreter integration (dependency issues)

**Try these demo commands:**
- `list` - List files in current directory
- `info` - Show system information
- `help` - Show help
- `quit` - Exit

**Note:** Full Open Interpreter integration requires resolving dependency conflicts.
"""
    console.print(Panel(Markdown(welcome_text), title="Welcome to OMNI Demo", border_style="cyan"))


def list_files():
    """List files in current directory."""
    try:
        files = os.listdir('.')
        console.print("\n[cyan]Files in current directory:[/cyan]")
        for f in sorted(files)[:20]:  # Show first 20
            if os.path.isdir(f):
                console.print(f"  📁 {f}")
            else:
                console.print(f"  📄 {f}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def show_info():
    """Show system information."""
    import platform
    console.print("\n[cyan]System Information:[/cyan]")
    console.print(f"  OS: {platform.system()} {platform.release()}")
    console.print(f"  Python: {platform.python_version()}")
    console.print(f"  Current Directory: {os.getcwd()}")


def main():
    """Main demo loop."""
    print_welcome()
    
    console.print("\n[green]✓ OMNI Demo Ready![/green]\n")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip().lower()
            
            if not user_input:
                continue
            
            if user_input in ['quit', 'exit']:
                if Confirm.ask("Exit demo?"):
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                continue
            
            elif user_input == 'list':
                list_files()
            
            elif user_input == 'info':
                show_info()
            
            elif user_input == 'help':
                console.print("\n[cyan]Available commands:[/cyan]")
                console.print("  list - List files")
                console.print("  info - System info")
                console.print("  help - This help")
                console.print("  quit - Exit")
            
            else:
                console.print(f"\n[yellow]Demo mode: Command '{user_input}' not implemented.[/yellow]")
                console.print("[dim]Full Open Interpreter integration coming soon![/dim]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    main()
