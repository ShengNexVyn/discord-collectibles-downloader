import sys
import json
import time
import ssl
import random
import itertools
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

from .banner import C_PURPLE, C_CYAN, C_BLUE, C_GREEN, C_YELLOW, C_RED, C_BOLD, C_DIM, C_RESET
from .utils import sanitize_name, parse_proxy, test_proxy_connection, USER_AGENTS

# Create unverified SSL context for proxy compatibility (fixes SSL handshake errors)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

def format_elapsed_time(seconds):
    """Format seconds into HH:MM:SS or MM:SS."""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

class DiscordCatalogScanner:
    def __init__(self, token="", proxies=None, retries=2):
        self.token = token
        self.retries = retries
        self.seen_urls = set()
        self.items = []
        self.target_filter = None
        self.scan_start_time = None
        
        parsed_proxies = []
        if proxies:
            for p in proxies:
                norm_p = parse_proxy(p)
                if norm_p:
                    parsed_proxies.append(norm_p)

        self.proxies = parsed_proxies
        self.proxy_pool = itertools.cycle(self.proxies) if self.proxies else None

    def get_next_proxy(self):
        if self.proxy_pool:
            return next(self.proxy_pool)
        return None

    def download_url(self, url, timeout=4, max_retries=1):
        proxy = self.get_next_proxy()
        
        for attempt in range(1, max_retries + 1):
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
            }
            if self.token:
                headers["Authorization"] = self.token

            req = urllib.request.Request(url, headers=headers)
            https_handler = urllib.request.HTTPSHandler(context=SSL_CONTEXT)
            
            if proxy:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
                opener = urllib.request.build_opener(proxy_handler, https_handler)
            else:
                opener = urllib.request.build_opener(https_handler)

            try:
                with opener.open(req, timeout=timeout) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    data = resp.read()
                    return data, content_type
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    return None, ""
                elif e.code in (401, 403, 404):
                    return None, ""
                else:
                    time.sleep(0.1 * attempt)
            except Exception:
                time.sleep(0.1 * attempt)

        return None, ""

    def add_item(self, kind, category, name, url, subtype="Static", item_id=""):
        if not url or url in self.seen_urls:
            return
            
        sanitized_kind = sanitize_name(kind, 30)
        
        # If user selected a specific filter mode, ONLY add items matching that mode!
        if self.target_filter and sanitized_kind.lower() != self.target_filter.lower():
            return

        self.seen_urls.add(url)
        item = {
            "kind": sanitized_kind,
            "category": sanitize_name(category, 50),
            "name": sanitize_name(name, 50),
            "url": url,
            "subtype": sanitize_name(subtype, 20),
            "item_id": sanitize_name(str(item_id), 40) if item_id else ""
        }
        self.items.append(item)
        
        elapsed_str = format_elapsed_time(time.time() - self.scan_start_time) if self.scan_start_time else "00:00"

        # Clean line output with live elapsed timer
        sys.stdout.write(
            f"\r\033[K  {C_GREEN}[✨ DISCOVERED]{C_RESET} {C_PURPLE}{sanitized_kind}{C_RESET} | {C_CYAN}{category}{C_RESET} : {C_BOLD}{item['name'][:25]}{C_RESET} {C_DIM}(Total: {len(self.items)}){C_RESET} | ⏱️ {C_YELLOW}{elapsed_str}{C_RESET}\n"
        )
        sys.stdout.flush()

    def parse_json_payload(self, data, current_cat="General"):
        if isinstance(data, dict):
            # Unpack published-listings wrapper if present
            if "sku" in data and isinstance(data["sku"], dict):
                self.parse_json_payload(data["sku"], current_cat)
                return

            cat_name = data.get("name", current_cat) if ("products" in data or "sku_id" in data or "tenant_metadata" in data) else current_cat
            
            # Check tenant_metadata for true collectibles item data & type
            collectibles_meta = data.get("tenant_metadata", {}).get("collectibles", {})
            item_meta = collectibles_meta.get("item", {}) if isinstance(collectibles_meta, dict) else {}
            
            item_type = None
            if isinstance(collectibles_meta, dict) and "type" in collectibles_meta:
                item_type = collectibles_meta["type"]
            elif isinstance(item_meta, dict) and "type" in item_meta:
                item_type = item_meta["type"]
            else:
                item_type = data.get("type")

            sku_id = data.get("sku_id") or data.get("id")
            prod_name = data.get("name") or data.get("title") or ""

            if item_type is not None and sku_id:
                label = data.get("name") or data.get("title") or data.get("label") or prod_name or sku_id

                # Type 0: Avatar Decoration
                if item_type == 0:
                    asset_hash = data.get("asset") or item_meta.get("asset")
                    if asset_hash:
                        is_anim = str(asset_hash).startswith("a_")
                        self.add_item("Avatar_Decorations", cat_name, label, f"https://cdn.discordapp.com/avatar-decoration-presets/{asset_hash}.png?size=1024", "Animated" if is_anim else "Static", asset_hash)

                # Type 1: Profile Effect
                elif item_type == 1:
                    effects = data.get("effects", []) or item_meta.get("effects", [])
                    for idx, eff in enumerate(effects):
                        if isinstance(eff, dict) and eff.get("src"):
                            self.add_item("Profile_Effects", cat_name, f"{label}_layer_{idx}", eff.get("src"), "Animated", f"{sku_id}_{idx}")
                    for key in ["staticFrameSrc", "static_frame_src", "thumbnailPreviewSrc", "thumbnail_preview_src", "reducedMotionSrc", "reduced_motion_src"]:
                        src = data.get(key) or item_meta.get(key)
                        if src:
                            self.add_item("Profile_Effects", cat_name, f"{label}_{key}", src, "Static", sku_id)

                # Type 2: Nameplate
                elif item_type == 2:
                    asset_path = data.get("asset") or item_meta.get("asset")
                    asset_id = sku_id
                    if asset_path and isinstance(asset_path, str):
                        parts = [p for p in asset_path.split("/") if p]
                        if parts: asset_id = parts[-1]

                    # Extract from assets dictionary (static_image_path, animated_image_path, video_path)
                    assets_dict = data.get("assets") or item_meta.get("assets")
                    if isinstance(assets_dict, dict):
                        for sub_key, sub_path in assets_dict.items():
                            if sub_path and isinstance(sub_path, str):
                                full_url = sub_path if sub_path.startswith("http") else f"https://cdn.discordapp.com/{sub_path}"
                                subtype = "Animated" if ("video" in sub_key or "anim" in sub_key) else "Static"
                                self.add_item("Nameplates", cat_name, f"{label}_{sub_key}", full_url, subtype, asset_id)

                    asset_url = data.get("asset_url") or item_meta.get("asset_url")
                    if asset_url:
                        self.add_item("Nameplates", cat_name, label, asset_url, "Static", asset_id)

                    # Fallback standard collectibles-shop media endpoints
                    self.add_item("Nameplates", cat_name, label, f"https://cdn.discordapp.com/media/v1/collectibles-shop/{sku_id}/static", "Static", sku_id)
                    self.add_item("Nameplates", cat_name, label, f"https://cdn.discordapp.com/media/v1/collectibles-shop/{sku_id}/video", "Video", sku_id)

                # Type 3: Profile Border / Widget / Frame
                elif item_type == 3:
                    layers = data.get("layers", []) or item_meta.get("layers", [])
                    for layer in layers:
                        layer_id = layer.get("id") if isinstance(layer, dict) else layer
                        if layer_id:
                            self.add_item(
                                "Profile_Borders",
                                cat_name,
                                f"{label}_layer_{layer_id}",
                                f"https://cdn.discordapp.com/media/v1/collectibles-shop/{sku_id}/{layer_id}/static",
                                "Static",
                                layer_id
                            )

                    for key in ["asset_url", "src", "static_frame_src", "thumbnail_preview_src", "hero_banner_url", "popout_asset", "asset"]:
                        src = data.get(key) or item_meta.get(key)
                        if src and isinstance(src, str) and src.startswith("http"):
                            self.add_item("Profile_Borders", cat_name, label, src, "Static", sku_id)

            for k, v in data.items():
                if k == "categories" and isinstance(v, list):
                    for cat in v:
                        if isinstance(cat, dict):
                            self.parse_json_payload(cat, cat.get("name", cat_name))
                elif k == "products" and isinstance(v, list):
                    for prod in v:
                        if isinstance(prod, dict):
                            self.parse_json_payload(prod, cat_name)
                elif isinstance(v, (dict, list)):
                    self.parse_json_payload(v, cat_name)

        elif isinstance(data, list):
            for elem in data:
                if isinstance(elem, dict):
                    self.parse_json_payload(elem, current_cat)

    def scan_catalog(self, filter_kind=None, mode_title="🚀 Full Scraper (Download Everything)"):
        self.target_filter = filter_kind
        self.scan_start_time = time.time()
        
        # Test Proxy Health if configured
        if self.proxies:
            active_proxy = self.proxies[0]
            print(f"\n{C_CYAN}[🧪 PROXY CHECK]{C_RESET} Testing proxy connection: {C_DIM}{active_proxy}{C_RESET}...")
            is_ok, reason = test_proxy_connection(active_proxy)
            if is_ok:
                print(f"  {C_GREEN}[✔ PROXY ONLINE] Connection successful! ({reason}){C_RESET}\n")
                proxy_status = f"{C_GREEN}{C_BOLD}🟢 ON{C_RESET} {C_DIM}({active_proxy[:40]}){C_RESET}"
            else:
                print(f"  {C_RED}[✖ PROXY ERROR] Proxy check failed: {reason}{C_RESET}\n")
                print(f"  {C_YELLOW}[!] Your configured proxy is unresponsive or rejected authentication.{C_RESET}")
                print(f"  {C_BOLD}➔ Continue with Direct Connection (without proxy)? (y/n) [y]: {C_RESET}", end="")
                try:
                    choice = input().strip().lower()
                    if choice in ("", "y", "yes"):
                        print(f"  {C_CYAN}[!] Switched to Direct Connection.{C_RESET}\n")
                        self.proxies = []
                        self.proxy_pool = None
                        proxy_status = f"{C_RED}{C_BOLD}🔴 OFF{C_RESET} {C_DIM}(Direct Connection - Proxy Failed){C_RESET}"
                    else:
                        print(f"  {C_RED}[!] Aborting scan due to proxy failure.{C_RESET}\n")
                        return []
                except Exception:
                    self.proxies = []
                    self.proxy_pool = None
                    proxy_status = f"{C_RED}{C_BOLD}🔴 OFF{C_RESET} {C_DIM}(Direct Connection){C_RESET}"
        else:
            proxy_status = f"{C_RED}{C_BOLD}🔴 OFF{C_RESET} {C_DIM}(Direct Connection){C_RESET}"

        print(f"\n{C_PURPLE}{C_BOLD}======================================================{C_RESET}")
        print(f"  {C_YELLOW}{C_BOLD}🎯 SELECTED MODE:{C_RESET} {C_CYAN}{C_BOLD}{mode_title}{C_RESET}")
        print(f"  {C_YELLOW}{C_BOLD}🌐 PROXY STATUS : {C_RESET} {proxy_status}")
        print(f"{C_PURPLE}{C_BOLD}======================================================{C_RESET}")
        print(f"\n{C_CYAN}{C_BOLD}[*] LIVE CATALOG SCANNER INITIALIZED...{C_RESET}\n")

        # Main Shop Categories & Marketing Catalog Endpoints
        endpoints = [
            "https://discord.com/api/v9/collectibles-shop?tab=home&include_bundles=true&include_dynamic_blocks=true&variants_return_style=2",
            "https://discord.com/api/v9/users/@me/collectibles-marketing?platform=0",
        ]

        for ep in endpoints:
            print(f"  {C_BLUE}[🔍 API SCAN]{C_RESET} Querying shop catalog: {C_DIM}{ep[:65]}...{C_RESET}")
            data_bytes, _ = self.download_url(ep, timeout=8, max_retries=2)
            if data_bytes:
                try:
                    self.parse_json_payload(json.loads(data_bytes.decode("utf-8", errors="ignore")))
                except Exception:
                    pass

        # Map filter_kind to Discord API search item_types
        kind_api_map = {
            "avatar_decorations": ["AVATAR_DECORATION"],
            "profile_effects": ["PROFILE_EFFECT"],
            "nameplates": ["NAMEPLATE"],
            "profile_borders": ["PROFILE_FRAME"]
        }

        if filter_kind and filter_kind.lower() in kind_api_map:
            item_types = kind_api_map[filter_kind.lower()]
        else:
            item_types = ["NAMEPLATE", "AVATAR_DECORATION", "PROFILE_EFFECT", "PROFILE_FRAME"]

        sort_types = ["popularity", "newest"]

        for itype in item_types:
            print(f"\n  {C_BLUE}[🔍 CATEGORY SCAN]{C_RESET} Searching Discord API: {C_BOLD}{itype}{C_RESET}")
            for sort_t in sort_types:
                offset = 0
                limit = 50
                while True:
                    api_url = f"https://discord.com/api/v9/shop/search?item_types={itype}&offset={offset}&limit={limit}&sort_type={sort_t}&sort_direction=desc"
                    data_bytes, _ = self.download_url(api_url, timeout=6, max_retries=2)
                    if not data_bytes:
                        break
                    try:
                        res_json = json.loads(data_bytes.decode("utf-8", errors="ignore"))
                        skus = res_json.get("skus", [])
                        pagination = res_json.get("pagination", {})
                        total_available = pagination.get("total", 0)
                        has_more = pagination.get("has_more", False)

                        if not skus:
                            break
                            
                        # Smooth parallel multithreaded SKU details resolution (fail-fast timeout=4s to prevent freezes)
                        def fetch_sku_detail(sku_id):
                            time.sleep(random.uniform(0.005, 0.02))
                            if isinstance(sku_id, str):
                                detail_url = f"https://discord.com/api/v9/store/published-listings/skus/{sku_id}"
                                detail_bytes, _ = self.download_url(detail_url, timeout=4, max_retries=1)
                                if detail_bytes:
                                    try:
                                        return json.loads(detail_bytes.decode("utf-8", errors="ignore"))
                                    except Exception:
                                        pass
                            elif isinstance(sku_id, dict):
                                return sku_id
                            return None

                        with ThreadPoolExecutor(max_workers=12) as executor:
                            futures = [executor.submit(fetch_sku_detail, sku_item) for sku_item in skus]
                            for future in as_completed(futures):
                                sku_json = future.result()
                                if sku_json:
                                    self.parse_json_payload(sku_json, current_cat=f"Shop_{itype}")

                        offset += len(skus)
                        if not has_more or (total_available > 0 and offset >= total_available):
                            break
                    except Exception:
                        break

        print("\n")

        total_scan_duration = time.time() - self.scan_start_time

        # Print catalog breakdown summary
        kind_counts = {}
        for item in self.items:
            k = item["kind"]
            kind_counts[k] = kind_counts.get(k, 0) + 1

        print(f"\n{C_PURPLE}{C_BOLD}================ CATALOG BREAKDOWN ================{C_RESET}")
        for k, count in kind_counts.items():
            print(f"  • {C_CYAN}{k:<20}{C_RESET} : {C_GREEN}{C_BOLD}{count}{C_RESET} assets discovered")
        print(f"  ------------------------------------------------")
        print(f"  {C_BOLD}Total Assets To Download : {C_YELLOW}{len(self.items)}{C_RESET}")
        print(f"  ⏱️  Total Catalog Scan Time: {C_BOLD}{format_elapsed_time(total_scan_duration)}{C_RESET}")
        print(f"{C_PURPLE}{C_BOLD}==================================================={C_RESET}\n")

        return self.items
