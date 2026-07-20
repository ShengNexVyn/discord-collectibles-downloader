# 🌌 DISCORD COLLECTIBLES SCRAPER by MrX 🚀

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/discord-collectibles-scraper?style=social)](https://github.com/yourusername/discord-collectibles-scraper)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/discord-collectibles-scraper?style=social)](https://github.com/yourusername/discord-collectibles-scraper)

An ultra-modern, high-performance, modular CLI scraper for Discord profile collectibles: **Avatar Decorations**, **Profile Effects**, **Nameplates**, and **Profile Borders/Widgets**.

```text
  ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗ 
  ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗
  ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║
  ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║
  ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝
  ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ 
         DISCORD COLLECTIBLES SCRAPER by MrX
```

---

> ⚠️ **DISCLAIMER & LEGAL WARNING / AVERTISSEMENT LÉGAL**  
> 
> **[FR] À DESSIN ÉDUCATIONNEL UNIQUEMENT :**  
> Ce logiciel a été conçu exclusivement à des fins d'éducation, de recherche et d'apprentissage sur le fonctionnement des API web et le multithreading en Python. Les créateurs, développeurs et contributeurs de ce projet **déclinent toute responsabilité** quant à l'utilisation qui pourrait être faite de ce programme par des tiers. L'utilisateur est seul responsable du respect des Conditions Générales d'Utilisation (Terms of Service) des services tiers concernés.
> 
> **[EN] FOR EDUCATIONAL PURPOSES ONLY:**  
> This software is created strictly for educational, research, and learning purposes regarding Python multithreading and web API structures. The authors, developers, and maintainers **assume no responsibility or liability** for any misuse, damage, or violations caused by third parties using this software. Users are solely responsible for ensuring compliance with all applicable Terms of Service and local laws.

> 🔮 **UNRELEASED ASSETS & LEAKS / ÉLÉMENTS NON SORTIS**  
> 
> **[FR] DÉCOUVERTE D'ÉLÉMENTS INÉDITS :**  
> En raison de la puissance de notre scanner et de l'exploration directe des API Discord, il est possible que cet outil découvre et télécharge des décorations, effets ou éléments de boutique **pas encore publiés ni disponibles au grand public** (assets non sortis / unreleased). Désolé Discord pour les leaks ! 🤫👀
> 
> **[EN] UNRELEASED CONTENT DISCOVERY:**  
> Due to the deep direct API scanning algorithm, this tool may uncover and download **unreleased collectibles and upcoming shop assets** before they are officially released to the public. Sorry Discord for the leaks! 🤫👀

> 🌐 **PROXY RECOMMENDATION / RECOMMANDATION PROXY**  
> 
> **[FR] UTILISATION DE PROXY FORTEMENT RECOMMANDÉE :**  
> Pour scraper l'intégralité du catalogue Discord (plus de 1 200 éléments) sans subir de ralentissements ou de blocages temporaires **HTTP 429 (Rate-Limited)**, il est **fortement recommandé de configurer un proxy** (ou une liste de proxys rotatifs) via le menu de configuration avancée (`⚙️ Configure Advanced Settings`) ou dans le fichier `config.yaml`.
> 
> **[EN] PROXY USAGE STRONGLY RECOMMENDED:**  
> When scraping large volumes of Discord Shop assets (1,200+ items), using a proxy or rotating proxy list (configured via `⚙️ Configure Advanced Settings` or `config.yaml`) is **strongly recommended** to avoid Discord HTTP 429 rate limit delays.

---

## 🏗️ Project Architecture / Architecture Modulaire

```text
discord-collectibles-scraper/
├── main.py                     # Entry point (100% Interactive CLI)
├── README.md                   # Full documentation & guide
├── LICENSE                     # MIT License
├── config.yaml                 # Auto-saved configuration settings
├── .gitignore                  # Git ignore rules
└── src/                        # Core modular engine
    ├── __init__.py
    ├── banner.py               # ASCII logo & ANSI neon themes
    ├── menu.py                 # Interactive Menu, Wizard & Token Prompt
    ├── config.py               # YAML configuration loader & saver
    ├── scanner.py              # Live Discord API Catalog Parser & Timer
    ├── downloader.py           # Multithreaded Downloader & Magic Bytes detector
    └── utils.py                # Path Sanitizers, Proxy parser & Health tester
```

---

## ✨ Features / Fonctionnalités

- 🔮 **Unreleased Collectibles Discovery**: Directly queries internal Discord API endpoints to uncover upcoming and unreleased collectibles.
- ⏱️ **Live Elapsed Timer & Speed Stats**: Real-time elapsed time counter (`⏱️ 00:45`) and speed tracker (`14.2 items/sec`) during scanning and downloading.
- 🧪 **Automatic Proxy Health Check**: Tests proxy status (`🟢 ON` / `🔴 OFF`) before scanning with automatic fallback to direct connection if proxy fails.
- 🌐 **Universal Proxy Format Support**: Supports all proxy formats (`host:port:user:pass`, `user:pass@host:port`, `http://...`, `socks5://...`).
- 🎮 **100% Interactive Console Setup**: Configure threads, proxies, and output paths interactively on launch.
- 🎮 **Interactive Terminal Menu**: Navigate seamlessly using keyboard **Arrow Keys (Up/Down)** and **Enter** in your console.
- 🔑 **Mandatory Token Prompt**: Interactive token verification prompt upon execution.
- 📡 **Live Real-Time Feedback**: View asset discoveries line-by-line as the scanner queries Discord APIs.
- 🎨 **Modern Neon UI**: Vibrant ANSI color themes, ASCII headers, and live progress bars `[████████░░] 80%`.
- 🌐 **100% Direct API Scraper**: Queries Discord's official shop search API endpoints across all categories.
- ⚡ **Multi-threaded Downloader**: Concurrent downloads powered by `ThreadPoolExecutor`.
- 🛡️ **Rate-Limit & Retry System**: Automatically handles HTTP 429 (`Retry-After`) rate limits and retries failed requests.
- 🗂️ **Smart Categorization**: Automatically categorizes assets by item type (`Avatar_Decorations`, `Profile_Effects`, `Nameplates`, `Profile_Borders`) and theme category.
- 🔍 **Magic Bytes Detector**: Verifies actual file header signatures (`.png`, `.webp`, `.gif`, `.mp4`, `.webm`).

---

## 📁 Output Folder Structure / Structure des Dossiers

```text
discord_collectibles/
├── Avatar_Decorations/      # Avatar decorations (PNG / WebP / APNG)
│   └── [Category_Name]/
│       ├── Static/
│       └── Animated/
├── Profile_Effects/         # Profile effects & animation layers (PNG / WebM)
│   └── [Category_Name]/
│       ├── Static/
│       └── Animated/
├── Nameplates/              # Profile nameplates (Static PNG & Animated Video)
│   └── [Category_Name]/
│       ├── Static/
│       └── Video/
└── Profile_Borders/         # Profile borders & custom widgets
    └── [Category_Name]/
        ├── Static/
        └── Video/
```

---

## 🚀 Quick Start / Guide Rapide

### Prerequisites
- **Python 3.9+** (No external third-party dependencies required! Uses Python standard library).

### Installation
```bash
git clone https://github.com/yourusername/discord-collectibles-scraper.git
cd discord-collectibles-scraper
```

### Basic Usage
Launch the interactive app:

```bash
python main.py
```

### Interactive Menu Options:
```text
  Main Menu - Select an Action:

  ❯ 🚀 Start Full Scraper (Download Everything)
    🎭 Download Avatar Decorations Only
    ✨ Download Profile Effects Only
    📛 Download Nameplates Only
    🖼️  Download Profile Borders Only
    ⚙️  Configure Advanced Settings (Threads, Proxy, Output path)
    ❌ Exit
```

---

## 🏷️ GitHub Search Topics & Tags / Mots-clés

`discord` • `discord-scraper` • `discord-api` • `discord-profile-effects` • `discord-avatar-decorations` • `discord-nameplates` • `discord-collectibles` • `discord-shop` • `discord-assets` • `python-scraper` • `asset-downloader` • `profile-effects` • `avatar-decorations` • `nameplates` • `discord-media-downloader` • `discord-tools` • `discord-shop-api` • `open-source` • `cli-menu`

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐ **If you find this project useful, don't forget to give it a star on GitHub!** ⭐
