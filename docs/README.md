# Safe‑Editor  
**A user‑authenticated text editor that stores the username and password in SHA‑256 encryption form.**  

---  

## Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Quick Start (Usage)](#quick-start-usage)  
6. [Command‑Line Interface (CLI)](#command-line-interface-cli)  
7. [API Documentation](#api-documentation)  
8. [Examples](#examples)  
9. [Configuration](#configuration)  
10. [Testing](#testing)  
11. [Contributing](#contributing)  
12. [License](#license)  

---  

## Overview
Safe‑Editor is a lightweight, cross‑platform text editor that requires a user to log in before any file can be opened or saved.  
User credentials are never stored in plain text – they are hashed with **SHA‑256** and persisted in a local SQLite database.  

The project is written in **Python 3.11+** and uses **Tkinter** for the GUI, **SQLAlchemy** for database handling, and **Click** for the CLI wrapper.

---  

## Features
| ✅ | Feature |
|---|---|
| ✅ | Secure login with SHA‑256 hashed credentials |
| ✅ | Automatic user registration (first‑time login) |
| ✅ | Plain‑text editing with syntax highlighting (via Pygments) |
| ✅ | Open / Save files with UTF‑8 support |
| ✅ | Auto‑save and recovery on crash |
| ✅ | Configurable themes (light / dark) |
| ✅ | Extensible plugin system (Python modules) |
| ✅ | Full API for embedding the editor in other applications |
| ✅ | Unit‑tested core components (pytest) |

---  

## Prerequisites
| Tool | Minimum Version |
|------|-----------------|
| Python | 3.11 |
| pip | 23.0 |
| Git | 2.30 |
| (Optional) virtualenv | 20.0 |

---  

## Installation  

### 1. Clone the repository
```bash
git clone https://github.com/your‑org/Safe-Editor.git
cd Safe-Editor
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (Optional) Install the CLI entry‑point globally
```bash
pip install .
# Now you can run `safe-editor` from any terminal
```

### 5. Verify the installation
```bash
safe-editor --version
# Expected output: Safe-Editor vX.Y.Z
```

---  

## Quick Start (Usage)  

```bash
# Start the GUI (will prompt for login / registration)
safe-editor
```

### First‑time login (registration)
1. When the login window appears, type a **new** username and password.  
2. The password is hashed with SHA‑256 and stored in `~/.safe_editor/users.db`.  
3. After registration you are automatically logged in and the main editor window opens.

### Normal login
1. Enter your existing username and password.  
2. If the hash matches the stored value you are granted access; otherwise you receive an error.

### Opening a file
- Use **File → Open** or press <kbd>Ctrl+O</kbd>.  
- The editor will only allow opening files after a successful login.

### Saving a file
- **File → Save** (<kbd>Ctrl+S</kbd>) or **Save As** (<kbd>Ctrl+Shift+S</kbd>).  
- Files are saved with UTF‑8 encoding.

---  

## Command‑Line Interface (CLI)

| Command | Description |
|---------|-------------|
| `safe-editor` | Launch the GUI (default). |
| `safe-editor --version` | Print the current version. |
| `safe-editor --reset-db` | **⚠️** Delete the user database (useful for testing). |
| `safe-editor --export-users <path>` | Export the hashed user list to a JSON file (admin only). |
| `safe-editor --theme <light|dark>` | Start the editor with the specified theme. |
| `safe-editor --no-gui <script.py>` | Run a headless script that uses the API (see *Embedding* below). |

**Example – start in dark mode:**
```bash
safe-editor --theme dark
```

---  

## API Documentation  

Safe‑Editor can be embedded in other Python applications via its public API.  
All public objects live under the top‑level package `safe_editor`.

### 1. `safe_editor.auth`
Handles user registration, login, and password hashing.

| Function | Signature | Description |
|----------|-----------|-------------|
| `hash_password` | `hash_password(password: str) -> str` | Returns a hex‑encoded SHA‑256 hash. |
| `register_user` | `register_user(username: str, password: str, db_path: str = DEFAULT_DB) -> bool` | Creates a new user; returns `True` on success, raises `UserExistsError` if the username already exists. |
| `authenticate` | `authenticate(username: str, password: str, db_path: str = DEFAULT_DB) -> bool` | Returns `True` if the supplied password matches the stored hash. |
| `delete_user` | `delete_user(username: str, db_path: str = DEFAULT_DB) -> None` | Removes a user (admin only). |

**Exceptions**
```python
class AuthError(Exception): ...
class UserExistsError(AuthError): ...
class InvalidCredentialsError(AuthError): ...
```

### 2. `safe_editor.editor`
Core editor widget (Tkinter based) that can be instantiated programmatically.

| Class | Constructor | Key Methods |
|-------|-------------|-------------|
| `SafeEditor` | `SafeEditor(master: tk.Tk, username: str, theme: str = "light")` | `open_file(path: str)`, `save_file(path: str)`, `set_theme(theme: str)`, `get_content() -> str`, `set_content(text: str)` |

**Example**
```python
import tkinter as tk
from safe_editor.editor import SafeEditor

root = tk.Tk()
editor = SafeEditor(root, username="alice", theme="dark")
editor.pack(fill="both", expand=True)
root.mainloop()
```

### 3. `safe_editor.config`
Utility functions for reading/writing the global configuration file (`~/.safe_editor/config.json`).

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_config` | `load_config() -> dict` | Returns the parsed JSON config (creates default if missing). |
| `save_config` | `save_config(cfg: dict) -> None` | Persists the supplied dictionary. |
| `set_option` | `set_option(key: str, value: Any) -> None` | Shortcut for updating a single option. |

### 4. `safe_editor.plugin`
Simple plugin loader that discovers Python modules in `plugins/`.

| Function | Signature | Description |
|----------|-----------|-------------|
| `discover_plugins` | `discover_plugins(path: str = "plugins") -> List[Plugin]` | Returns a list of loaded plugin objects. |
| `run_plugin` | `run_plugin(plugin_name: str, editor: SafeEditor) -> None` | Executes a plugin’s `run(editor)` entry point. |

---  

## Examples  

### A. Register a new user programmatically
```python
from safe_editor.auth import register_user, hash_password

username = "bob"
password = "S3cureP@ss!"

try:
    register_user(username, password)
    print(f"User {username} created successfully.")
except Exception as e:
    print(f"Failed to register: {e}")
```

### B. Authenticate and open a file without the GUI
```python
import sys
from safe_editor.auth import authenticate
from safe_editor.editor import SafeEditor
import tkinter as tk

USERNAME = "alice"
PASSWORD = "MySecret"

if not authenticate(USERNAME, PASSWORD):
    sys.exit("Invalid credentials")

root = tk.Tk()
editor = SafeEditor(root, username=USERNAME, theme="light")
editor.pack(fill="both", expand=True)

# Open a file automatically
editor.open_file("example.txt")
root.mainloop()
```

### C. Using the CLI to export users
```bash
safe-editor --export-users ./user_dump.json
```

### D. Adding a simple plugin (example: word‑counter)
Create a file `plugins/word_counter.py`:
```python
# plugins