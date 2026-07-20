import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .banner import C_PURPLE, C_CYAN, C_GREEN, C_YELLOW, C_RED, C_BOLD, C_RESET
from .utils import detect_file_extension

def format_elapsed_time(seconds):
    """Format seconds into HH:MM:SS or MM:SS."""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

class AssetDownloader:
    def __init__(self, output_dir="discord_collectibles", scanner=None, max_workers=16):
        self.output_dir = os.path.abspath(output_dir)
        self.scanner = scanner
        self.max_workers = max_workers

    def process_item_download(self, item):
        url = item["url"]
        kind = item["kind"]
        category = item["category"]
        subtype = item["subtype"]
        name = item["name"]
        item_id = item["item_id"]

        # Fast timeout (5s) for asset downloads so single dead proxy connections never freeze the queue
        data, content_type = self.scanner.download_url(url, timeout=5)
        if not data or len(data) < 50:
            return False, url, "Empty / 404 response"

        ext = detect_file_extension(data, url, content_type)
        folder = os.path.join(self.output_dir, kind, category, subtype)
        os.makedirs(folder, exist_ok=True)

        filename = f"{name}_{item_id}{ext}" if item_id and item_id not in name else f"{name}{ext}"
        filepath = os.path.join(folder, filename)

        if os.path.exists(filepath) and os.path.getsize(filepath) == len(data):
            return True, filepath, "Already exists"

        try:
            with open(filepath, "wb") as f:
                f.write(data)
            return True, filepath, "Saved"
        except Exception as e:
            return False, url, str(e)

    def download_all(self, items):
        if not items:
            print(f"{C_RED}[!] No items to download.{C_RESET}")
            return

        print(f"{C_PURPLE}[*] DOWNLOADING {len(items)} ITEMS TO {self.output_dir}...{C_RESET}\n")

        saved_count = 0
        error_count = 0
        already_count = 0
        total = len(items)
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {executor.submit(self.process_item_download, item): item for item in items}
            
            for idx, future in enumerate(as_completed(future_to_item), 1):
                try:
                    success, path_or_url, status = future.result()
                    if success:
                        if status == "Already exists":
                            already_count += 1
                        else:
                            saved_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1

                elapsed = time.time() - start_time
                speed = idx / elapsed if elapsed > 0 else 0
                percent = (idx / total) * 100
                bar_len = 20
                filled = int(bar_len * idx // total)
                bar = '█' * filled + '░' * (bar_len - filled)
                
                sys.stdout.write(
                    f"\r\033[K {C_CYAN}[{bar}] {percent:5.1f}%{C_RESET} | "
                    f"{C_GREEN}Saved: {saved_count}{C_RESET} | "
                    f"{C_YELLOW}Exist: {already_count}{C_RESET} | "
                    f"{C_RED}Fail: {error_count}{C_RESET} | "
                    f"⏱️ {C_BOLD}{format_elapsed_time(elapsed)}{C_RESET} ({speed:.1f} i/s)"
                )
                sys.stdout.flush()

        total_elapsed = time.time() - start_time
        avg_speed = total / total_elapsed if total_elapsed > 0 else 0

        print(f"\n\n{C_PURPLE}{C_BOLD}================ DOWNLOAD SUMMARY ================{C_RESET}")
        print(f" {C_GREEN}✔ Successfully Saved New Files: {saved_count}{C_RESET}")
        print(f" {C_YELLOW}✔ Already Existing Files:       {already_count}{C_RESET}")
        print(f" {C_RED}✖ Failed / 404 Requests:        {error_count}{C_RESET}")
        print(f" ⏱️  Total Download Duration:    {format_elapsed_time(total_elapsed)} ({avg_speed:.1f} items/sec)")
        print(f" 📁 Saved Location:              {self.output_dir}{C_RESET}")
        print(f"{C_PURPLE}{C_BOLD}=================================================={C_RESET}\n")
