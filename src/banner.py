import os

# ANSI Color Codes
C_PURPLE = "\033[95m"
C_CYAN   = "\033[96m"
C_BLUE   = "\033[94m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_RED    = "\033[91m"
C_BOLD   = "\033[1m"
C_DIM    = "\033[2m"
C_RESET  = "\033[0m"

BANNER = f"""
{C_PURPLE}{C_BOLD}
  ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗ 
  ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗
  ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║
  ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║
  ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝
  ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ 
{C_CYAN}         DISCORD COLLECTIBLES SCRAPER {C_YELLOW}by MrX{C_RESET}
{C_DIM}  ======================================================{C_RESET}
"""

def enable_ansi_windows():
    """Enable Virtual Terminal Processing on Windows Command Prompt."""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
