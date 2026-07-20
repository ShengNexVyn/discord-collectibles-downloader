import os
import sys
import time
from .banner import BANNER, C_CYAN, C_PURPLE, C_YELLOW, C_RED, C_GREEN, C_BOLD, C_DIM, C_RESET
from .config import load_config, save_config
from .utils import parse_proxy

def get_key():
    """Read single keypress for cross-platform interactive menu (Up/Down/Enter)."""
    if os.name == 'nt':
        import msvcrt
        key = msvcrt.getch()
        if key in (b'\x00', b'\xe0'):
            key = msvcrt.getch()
            if key == b'H': return 'up'
            if key == b'P': return 'down'
        elif key in (b'\r', b'\n'):
            return 'enter'
        elif key == b'\x03':
            raise KeyboardInterrupt
    else:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                if ch3 == 'A': return 'up'
                if ch3 == 'B': return 'down'
            elif ch in ('\r', '\n'):
                return 'enter'
            elif ch == '\x03':
                raise KeyboardInterrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def interactive_select(title, options):
    """Render ultra-smooth 60fps flicker-free interactive arrow-key selection menu."""
    selected_idx = 0
    menu_lines_count = len(options)

    # Hide cursor during menu selection
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    # Initial full header render
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"{C_CYAN}{C_BOLD}  {title}{C_RESET}\n")
    print(f"{C_DIM}  (Use UP / DOWN arrow keys and press ENTER to select){C_RESET}\n")

    try:
        while True:
            # Overwrite menu lines smoothly in-place without os.system('cls')
            for idx, option in enumerate(options):
                if idx == selected_idx:
                    sys.stdout.write(f"\r\033[K  {C_PURPLE}{C_BOLD}❯ {option}{C_RESET}\n")
                else:
                    sys.stdout.write(f"\r\033[K    {C_DIM}{option}{C_RESET}\n")
            sys.stdout.flush()

            key = get_key()
            if key == 'up':
                selected_idx = (selected_idx - 1) % len(options)
                sys.stdout.write(f"\033[{menu_lines_count}A")
            elif key == 'down':
                selected_idx = (selected_idx + 1) % len(options)
                sys.stdout.write(f"\033[{menu_lines_count}A")
            elif key == 'enter':
                sys.stdout.write("\033[?25h\n")
                sys.stdout.flush()
                return selected_idx
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
        sys.exit(0)
    except Exception:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        print(f"\n{C_YELLOW}Select option [1-{len(options)}]: {C_RESET}", end="")
        choice = input().strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def prompt_mandatory_token(config_data):
    """Prompt user interactively for token if missing and save to config.yaml."""
    token = config_data.get("token", "").strip()
    if token:
        return token

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"{C_RED}{C_BOLD}  [!] DISCORD AUTHORIZATION TOKEN REQUIRED{C_RESET}")
    print(f"{C_DIM}  To fetch live Discord Shop items, a Discord user token is mandatory.{C_RESET}\n")
    
    while not token:
        print(f"{C_YELLOW}{C_BOLD}  ➔ Enter your Discord Authorization Token: {C_RESET}", end="")
        try:
            token = input().strip()
            if not token:
                print(f"{C_RED}  [!] Token cannot be empty. Please enter a valid token.{C_RESET}\n")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{C_RED}[!] Exiting...{C_RESET}")
            sys.exit(0)
            
    config_data["token"] = token
    save_config(config_data)
    return token

def prompt_advanced_settings(current_settings):
    """Interactive settings configuration wizard & auto-save to config.yaml."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"{C_CYAN}{C_BOLD}  ⚙️ ADVANCED CONFIGURATION WIZARD{C_RESET}\n")
    print(f"{C_DIM}  Press ENTER to keep the default value in brackets [default].{C_RESET}\n")

    # 1. Threads
    default_threads = current_settings.get("threads", 16)
    print(f"  {C_YELLOW}➔ Number of Parallel Download Threads [{default_threads}]: {C_RESET}", end="")
    try:
        t_input = input().strip()
        threads = int(t_input) if t_input.isdigit() and int(t_input) > 0 else default_threads
    except Exception:
        threads = default_threads

    # 2. Proxy
    raw_default_proxy = current_settings.get("proxy", "")
    norm_default_proxy = parse_proxy(raw_default_proxy)
    display_proxy_status = f"{C_GREEN}🟢 ON ({norm_default_proxy}){C_RESET}" if norm_default_proxy else f"{C_RED}🔴 OFF{C_RESET}"

    print(f"  {C_YELLOW}➔ Proxy server (e.g. host:port:user:pass or leave blank for Direct) [Current: {display_proxy_status}]: {C_RESET}", end="")
    try:
        p_input = input().strip()
        if p_input:
            proxy = p_input
        else:
            proxy = raw_default_proxy
    except Exception:
        proxy = raw_default_proxy

    # 3. Output Folder
    default_output = current_settings.get("output", "discord_collectibles")
    print(f"  {C_YELLOW}➔ Output Folder Path [{default_output}]: {C_RESET}", end="")
    try:
        out_input = input().strip()
        output_dir = out_input if out_input else default_output
    except Exception:
        output_dir = default_output

    # 4. Export JSON
    print(f"  {C_YELLOW}➔ Export catalog metadata to JSON file? (y/n) [n]: {C_RESET}", end="")
    try:
        exp_input = input().strip().lower()
        export_json = "catalog.json" if exp_input in ("y", "yes") else ""
    except Exception:
        export_json = ""

    updated_settings = {
        "token": current_settings.get("token", ""),
        "threads": threads,
        "proxy": proxy,
        "output": output_dir,
        "export_json": export_json,
        "retries": current_settings.get("retries", 3)
    }

    save_config(updated_settings)
    print(f"\n{C_GREEN}[✔] Settings updated and saved to config.yaml successfully!{C_RESET}\n")
    time.sleep(1)

    return updated_settings
