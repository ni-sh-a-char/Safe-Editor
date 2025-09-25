# Safe‑Editor  
**A user‑authenticated text editor that stores the username and password in SHA‑256 encryption form.**  

---  

## Table of Contents
1. [Overview](#overview)  
2. [Installation](#installation)  
3. [Quick Start / Usage](#quick-start--usage)  
4. [Command‑Line Interface (CLI)](#command-line-interface-cli)  
5. [API Documentation](#api-documentation)  
6. [Code Examples](#code-examples)  
7. [Configuration](#configuration)  
8. [Testing](#testing)  
9. [Contributing](#contributing)  
10. [License](#license)  

---  

## Overview
Safe‑Editor is a lightweight, cross‑platform text editor that requires a user to log in before any file can be opened, edited, or saved.  
* **Security** – Usernames and passwords are never stored in plain text. They are hashed with **SHA‑256** and salted before persisting to the local SQLite database.  
* **Extensible API** – The core functionality is exposed through a clean Python API, making it easy to embed the editor in other applications or to build custom front‑ends.  
* **CLI & GUI** – By default the repository ships a terminal‑based UI (curses) and a minimal Qt5 GUI (`safe_editor_gui.py`). Both share the same backend logic.  

---  

## Installation  

### Prerequisites
| Tool | Minimum version |
|------|-----------------|
| Python | 3.9 |
| pip   | 21.0 |
| Git   | any (for cloning) |
| (Optional) Qt5 libraries – required only for the GUI (`safe_editor_gui.py`) |

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourorg/Safe-Editor.git
cd Safe-Editor
```

### 2️⃣ Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

> **Tip:** The `requirements.txt` currently contains:
```
cryptography>=42.0.0
SQLAlchemy>=2.0.0
click>=8.0
pyqt5>=5.15   # only needed for the GUI
```

### 4️⃣ (Optional) Install as a command‑line tool
```bash
pip install -e .
# This adds the `safe-editor` entry point to your PATH.
```

You can now run `safe-editor --help` from any terminal.

---  

## Quick Start / Usage  

### 1️⃣ Initialise the user database (run once)
```bash
safe-editor init-db
```
This creates a local SQLite file (`safe_editor.db`) in the project root and prompts you to create the first admin account.

### 2️⃣ Launch the editor (CLI)
```bash
safe-editor
```
You will be asked for a username and password. After successful authentication you can:
* **Open** a file: `:open path/to/file.txt`
* **Save** the current buffer: `:save` (or `:save path/to/file.txt`)
* **Quit**: `:quit`

### 3️⃣ Launch the GUI (if you installed PyQt5)
```bash
python safe_editor_gui.py
```
The same login dialog appears, followed by a simple text‑editing window.

---  

## Command‑Line Interface (CLI)

The CLI is built with **Click** and provides the following commands:

| Command | Description |
|---------|-------------|
| `safe-editor` | Starts the interactive terminal editor (default). |
| `safe-editor init-db` | Initialise or reset the user database. |
| `safe-editor add-user <username>` | Prompt for a password and add a new user. |
| `safe-editor del-user <username>` | Delete an existing user (admin only). |
| `safe-editor list-users` | Show all registered usernames. |
| `safe-editor change-pass <username>` | Change password for a given user. |
| `safe-editor --version` | Show the current version. |

#### Global options
* `--db PATH` – Path to the SQLite DB (default: `./safe_editor.db`).  
* `--log-level LEVEL` – Set logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).  

#### Example
```bash
safe-editor add-user alice
# → prompts for password, stores SHA‑256 hash + random 16‑byte salt.
```

---  

## API Documentation  

All public classes live in the `safe_editor` package. Below is a high‑level overview; full doc‑strings are available in the source code and via `pydoc`.

### `safe_editor.auth.Authenticator`
Handles user registration, login, and password verification.

| Method | Signature | Description |
|--------|-----------|-------------|
| `register(username: str, password: str) -> None` | `register(username, password)` | Creates a new user entry. Password is salted and hashed with SHA‑256 before storage. |
| `login(username: str, password: str) -> bool` | `login(username, password)` | Returns `True` if the supplied password matches the stored hash. |
| `change_password(username: str, new_password: str) -> None` | `change_password(username, new_password)` | Re‑hashes the new password with a fresh salt. |
| `delete_user(username: str) -> None` | `delete_user(username)` | Removes a user from the DB (admin only). |
| `list_users() -> List[str]` | `list_users()` | Returns a list of all usernames. |

### `safe_editor.editor.Editor`
Core text‑editing engine (no UI).

| Method | Signature | Description |
|--------|-----------|-------------|
| `load(path: str) -> None` | `load(path)` | Reads a file into the internal buffer (`self.buffer`). |
| `save(path: Optional[str] = None) -> None` | `save(path=None)` | Writes the buffer to `path` (or the original file if `path` is `None`). |
| `insert(line_no: int, text: str) -> None` | `insert(line_no, text)` | Inserts `text` at the given line number. |
| `delete(line_no: int) -> None` | `delete(line_no)` | Deletes the line at `line_no`. |
| `replace(line_no: int, text: str) -> None` | `replace(line_no, text)` | Replaces the content of a line. |
| `get_buffer() -> List[str]` | `get_buffer()` | Returns a copy of the current buffer. |
| `search(pattern: str, regex: bool = False) -> List[int]` | `search(pattern, regex=False)` | Returns line numbers that match the pattern. |

### `safe_editor.db.Database`
Thin wrapper around SQLAlchemy for persistence.

| Method | Signature | Description |
|--------|-----------|-------------|
| `engine` (property) | `engine` | SQLAlchemy engine instance. |
| `session()` | `session()` | Context‑manager returning a scoped session. |
| `create_all()` | `create_all()` | Creates tables if they don’t exist. |
| `drop_all()` | `drop_all()` | Drops all tables (dangerous – used only in tests). |

### Exceptions
* `AuthenticationError` – Raised when login fails.  
* `UserExistsError` – Raised on duplicate registration.  
* `UserNotFoundError` – Raised when a username cannot be located.  
* `FileIOError` – Raised for any file‑system related problem (permission, missing file, etc.).  

---  

## Code Examples  

### 1️⃣ Using the API programmatically
```python
from safe_editor.auth import Authenticator
from safe_editor.editor import Editor

# ----------------------------------------------------------------------
# 1. Authenticate the user
# ----------------------------------------------------------------------
auth = Authenticator(db_path="my_safe_editor.db")
if not auth.login("bob", "s3cr3t!"):
    raise PermissionError("Invalid credentials")

# ----------------------------------------------------------------------
# 2. Work with the editor
# ----------------------------------------------------------------------
ed = Editor()
ed.load("notes.txt")               # load existing file
ed.insert(0, "# My Daily Notes")   # prepend a title
ed.replace(5, "Updated line content")
ed.save()                          # writes back to notes.txt

print("Current buffer:")
for i, line in enumerate(ed.get_buffer(),