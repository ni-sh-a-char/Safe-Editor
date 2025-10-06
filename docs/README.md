# Safe‑Editor  
**A user‑authenticated text editor that stores the username and password in SHA‑256 bit encryption form.**  

---  

## Table of Contents
1. [Overview](#overview)  
2. [Installation](#installation)  
3. [Quick Start / Usage](#quick-start--usage)  
4. [Command‑Line Interface (CLI)](#command-line-interface-cli)  
5. [Python API Documentation](#python-api-documentation)  
6. [Examples](#examples)  
7. [Configuration](#configuration)  
8. [Security Considerations](#security-considerations)  
9. [Testing](#testing)  
10. [Contributing](#contributing)  
11. [License](#license)  

---  

## Overview
Safe‑Editor is a lightweight, cross‑platform text editor that requires a user to authenticate before any file can be opened or saved.  

* **Authentication** – Username & password are stored as a SHA‑256 hash (salted) in a local SQLite database (`.safe_editor.db`).  
* **Encryption** – All passwords are **hashed**, not encrypted, ensuring they are never persisted in plain text.  
* **Extensible API** – The core functionality is exposed as a Python package (`safe_editor`) so you can embed it in other applications or build custom GUIs.  
* **CLI** – A ready‑to‑use command‑line interface (`safe-editor`) for quick editing from the terminal.  

---  

## Installation  

### Prerequisites
| Tool | Minimum Version |
|------|-----------------|
| Python | 3.9+ |
| Git | 2.20+ |
| pip | 21.0+ |

> **Note** – Safe‑Editor is pure‑Python; no external binaries are required.

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-org/Safe-Editor.git
cd Safe-Editor
```

### 2️⃣ Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
```

### 3️⃣ Install the package and its dependencies
```bash
pip install -e .          # editable install (development)
# or, for a production‑only install:
pip install .
```

### 4️⃣ Verify the installation
```bash
safe-editor --version
# Expected output: Safe-Editor vX.Y.Z
```

### Optional: Install optional GUI dependencies
If you plan to use the optional Qt‑based GUI, install the extra:
```bash
pip install .[gui]   # pulls PyQt6
```

---  

## Quick Start / Usage  

### Register a new user (first‑time setup)
```bash
safe-editor register
# You will be prompted for a username and password.
```

### Open a file (authenticated)
```bash
safe-editor edit path/to/file.txt
```

The CLI will:
1. Prompt for username & password.  
2. Verify the SHA‑256 hash against the stored value.  
3. Open the file in the built‑in terminal editor (uses `prompt_toolkit`).  

### Save & exit
* Press **Ctrl‑S** to save.  
* Press **Ctrl‑Q** to quit (will prompt to save if there are unsaved changes).  

---  

## Command‑Line Interface (CLI)

| Command | Description | Options |
|---------|-------------|---------|
| `safe-editor register` | Create a new user account. | `--username <name>` (optional, will prompt) |
| `safe-editor login` | Test login credentials without opening a file. | `--username <name>` |
| `safe-editor edit <file>` | Open `<file>` after authentication. | `--readonly` (open in read‑only mode) |
| `safe-editor changepw` | Change the password for the current user. | |
| `safe-editor users` | List all registered usernames (admin only). | `--json` (machine‑readable output) |
| `safe-editor --version` | Show version information. | |

**Global options**

* `-h, --help` – Show help for any command.  
* `-v, --verbose` – Enable detailed logging (writes to `~/.safe_editor/logs.txt`).  

---  

## Python API Documentation  

The package can be imported as `import safe_editor`. Below is the public API surface.

### `safe_editor.auth.Authenticator`
Handles user registration, login, and password hashing.

| Method | Signature | Description |
|--------|-----------|-------------|
| `register(username: str, password: str) -> None` | `register(username, password)` | Creates a new user. Raises `UserExistsError` if the username already exists. |
| `login(username: str, password: str) -> bool` | `login(username, password)` | Returns `True` if credentials match, otherwise `False`. |
| `change_password(username: str, old_password: str, new_password: str) -> None` | `change_password(username, old_password, new_password)` | Updates the stored hash. |
| `list_users(admin_token: str) -> List[str]` | `list_users(admin_token)` | Returns all usernames; requires a valid admin token. |
| `hash_password(password: str, salt: bytes | None = None) -> Tuple[str, str]` | `hash_password(password, salt=None)` | Returns `(salt_hex, hash_hex)`. Uses `hashlib.sha256`. |
| `verify_password(stored_salt: str, stored_hash: str, password: str) -> bool` | `verify_password(salt, hash, password)` | Checks a password against stored values. |

### `safe_editor.editor.Editor`
Core editor class used by both CLI and GUI.

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__(auth: Authenticator, *, readonly: bool = False)` | `Editor(auth, readonly=False)` | Initialise with an `Authenticator` instance. |
| `open(file_path: str) -> None` | `open(file_path)` | Loads the file into memory; raises `FileNotFoundError` if missing. |
| `save() -> None` | `save()` | Writes the current buffer back to disk (requires write permission). |
| `get_text() -> str` | `get_text()` | Returns the current buffer as a string. |
| `set_text(text: str) -> None` | `set_text(text)` | Replaces the buffer with `text`. |
| `close() -> None` | `close()` | Clears the buffer and releases resources. |

### `safe_editor.db.Database`
Thin wrapper around SQLite for user storage.

| Method | Signature | Description |
|--------|-----------|-------------|
| `init_db(path: str = "~/.safe_editor.db") -> None` | `init_db(path)` | Creates the DB file and required tables if they do not exist. |
| `execute(query: str, params: Tuple = ()) -> sqlite3.Cursor` | `execute(query, params=())` | Low‑level query execution (used internally). |
| `close() -> None` | `close()` | Closes the DB connection. |

### Exceptions
* `safe_editor.exceptions.UserExistsError` – Raised when trying to register an existing username.  
* `safe_editor.exceptions.AuthenticationError` – Raised on failed login.  
* `safe_editor.exceptions.PermissionError` – Raised when a write operation is attempted in read‑only mode.  

---  

## Examples  

### 1️⃣ Basic script – open a file after authenticating
```python
from safe_editor.auth import Authenticator
from safe_editor.editor import Editor

def main():
    auth = Authenticator()
    username = input("Username: ")
    password = input("Password: ")

    if not auth.login(username, password):
        print("❌ Invalid credentials")
        return

    editor = Editor(auth)
    editor.open("notes.txt")
    print("--- Current content ---")
    print(editor.get_text())

    # Append a line
    new_content = editor.get_text() + "\nAdded on " + __import__("datetime").datetime.now().isoformat()
    editor.set_text(new_content)
    editor.save()
    print("✅ File saved!")

if __name__ == "__main__":
    main()
```

### 2️⃣ Register a new user programmatically
```python
from safe_editor.auth import Authenticator, UserExistsError

auth = Authenticator()
try:
    auth.register("alice", "S3cureP@ssw0rd")
    print("User 'alice' created successfully.")
except UserExistsError:
    print