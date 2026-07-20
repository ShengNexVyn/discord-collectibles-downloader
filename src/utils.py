import os
import re
import random
import urllib.request
import urllib.error

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
]

def sanitize_name(name, max_len=60):
    """Sanitize and truncate strings for safe Windows/Linux/macOS path names."""
    if not name:
        return "Uncategorized"
    name = str(name).encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    name = re.sub(r'[\\/*?:"<>|\r\n\t]', "_", name)
    name = name.strip(" ._")
    if len(name) > max_len:
        name = name[:max_len].strip(" ._")
    return name if name else "Uncategorized"

def detect_file_extension(data: bytes, url: str = "", content_type: str = "") -> str:
    """Detect real file extension using magic bytes signatures or MIME headers."""
    if data:
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return ".png"
        elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
            return ".gif"
        elif len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return ".webp"
        elif len(data) >= 12 and (data[4:8] == b"ftyp" or data[4:12] == b"ftypisom" or data[4:12] == b"ftypmp42"):
            return ".mp4"
        elif data.startswith(b"\x1a\x45\xdf\xa3"):
            return ".webm"
        elif data.startswith(b"\xff\xd8\xff"):
            return ".jpg"

    url_lower = url.lower()
    if ".png" in url_lower: return ".png"
    if ".webm" in url_lower: return ".webm"
    if ".mp4" in url_lower: return ".mp4"
    if ".gif" in url_lower: return ".gif"
    if ".webp" in url_lower: return ".webp"
    if "png" in content_type: return ".png"
    if "webm" in content_type: return ".webm"
    if "mp4" in content_type: return ".mp4"
    if "gif" in content_type: return ".gif"
    if "webp" in content_type: return ".webp"
    return ".png"

def parse_proxy(proxy_str):
    """Normalize any proxy format (host:port:user:pass, user:pass@host:port, etc.) to standard http:// format."""
    if not proxy_str or not isinstance(proxy_str, str):
        return None
    proxy_str = proxy_str.strip()
    if not proxy_str:
        return None

    # Handle host:port:username:password format
    parts = proxy_str.split(":")
    if len(parts) == 4 and not proxy_str.startswith(("http://", "https://", "socks5://")):
        host, port, user, password = parts
        return f"http://{user}:{password}@{host}:{port}"
    
    # Handle user:pass@host:port format without scheme
    if "@" in proxy_str and not proxy_str.startswith(("http://", "https://", "socks5://")):
        return f"http://{proxy_str}"

    if not proxy_str.startswith(("http://", "https://", "socks5://")):
        return f"http://{proxy_str}"
        
    return proxy_str

def test_proxy_connection(proxy_url, timeout=6):
    """Test if proxy connection is alive and functional."""
    if not proxy_url:
        return True, "Direct Connection"
        
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    req = urllib.request.Request("https://discord.com", headers=headers)
    proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
    opener = urllib.request.build_opener(proxy_handler)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return True, "Connection Successful"
    except urllib.error.HTTPError as e:
        if e.code in (407, 401):
            return False, f"Proxy Authentication Required ({e.code})"
        return True, f"HTTP {e.code}"
    except Exception as e:
        err_msg = str(e)
        if "407" in err_msg or "Proxy Authentication" in err_msg:
            return False, "Proxy Authentication Failed (407)"
        if "WinError 10061" in err_msg or "Connection refused" in err_msg:
            return False, "Connection Refused (Proxy Dead)"
        if "timed out" in err_msg.lower():
            return False, "Connection Timed Out"
        return False, err_msg

def load_proxies_from_file(file_path):
    """Load proxy list from file."""
    proxies = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                p = parse_proxy(line)
                if p:
                    proxies.append(p)
    return proxies
