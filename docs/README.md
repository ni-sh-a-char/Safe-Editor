# Safe‑Editor  
**A user‑authenticated text editor that stores the username and password in SHA‑256 encryption form.**  

---  

## Table of Contents  

| Section | Description |
|---------|-------------|
| [Overview](#overview) | What Safe‑Editor does and why it matters |
| [Features](#features) | Core capabilities |
| [Installation](#installation) | How to get Safe‑Editor up and running |
| [Quick‑Start](#quick-start) | One‑line demo |
| [Usage](#usage) | CLI, GUI, and library usage |
| [API Documentation](#api-documentation) | Public classes, functions and data structures |
| [Examples](#examples) | Real‑world snippets (CLI, Python, and integration) |
| [Configuration](#configuration) | Customising storage, hashing, and UI |
| [Testing](#testing) | Running the test‑suite |
| [Contributing](#contributing) | How to help |
| [License](#license) | Open‑source terms |

---  

## Overview  

Safe‑Editor is a lightweight, cross‑platform text editor that requires a user to log in before any file can be opened, edited, or saved.  

* **Security first** – usernames and passwords are never stored in plain text. They are hashed with **SHA‑256** and salted with a per‑user random 16‑byte value.  
* **Pluggable storage** – by default credentials are kept in a local SQLite database (`.safe-editor.db`), but the storage backend can be swapped for JSON, PostgreSQL, or any custom implementation.  
* **CLI & Python API** – use the bundled command‑line interface for quick editing, or import the library into your own Python projects.  

---  

## Features  

| ✅ | Feature |
|---|---------|
| ✅ | Secure password hashing (SHA‑256 + per‑user salt) |
| ✅ | Automatic lock after configurable inactivity timeout |
| ✅ | Syntax‑highlighted editing (via **pygments**) |
| ✅ | File‑type detection & line numbers |
| ✅ | Undo/redo stack |
| ✅ | Extensible storage back‑ends (SQLite, JSON, custom) |
| ✅ | Full Python API for embedding Safe‑Editor in other tools |
| ✅ | Cross‑platform (Windows, macOS, Linux) |
| ✅ | Unit‑tested (coverage > 90 %) |

---  

## Installation  

Safe‑Editor is distributed as a **Python package** and can be installed with `pip`. It requires Python 3.9+.

```bash
# 1️⃣ Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2️⃣ Install the package from PyPI
pip install safe-editor

# 3️⃣ (Optional) Install optional dependencies for GUI mode
pip install "safe-editor[gui]"
```

### From source  

```bash
# Clone the repo
git clone https://github.com/your-org/Safe-Editor.git
cd Safe-Editor

# Install in editable mode (useful for development)
pip install -e .[dev]   # includes test, lint, and GUI extras
```

### System dependencies  

| Dependency | Reason |
|------------|--------|
| `python >=3.9` | Core interpreter |
| `sqlite3` (bundled) | Default credential store |
| `pygments` | Syntax highlighting |
| `prompt-toolkit` | Rich CLI UI |
| `PyQt5` (optional) | GUI mode (`safe-editor --gui`) |
| `cryptography` | Secure random salt generation |

---  

## Quick‑Start  

```bash
# Initialise the credential store (run once)
safe-editor --init

# Create a user (you will be prompted for a password)
safe-editor --add-user alice

# Open a file (you will be asked to log in)
safe-editor notes.txt
```

You should now see a full‑screen, syntax‑highlighted editor. Press `Ctrl‑S` to save, `Ctrl‑Q` to quit.

---  

## Usage  

### 1️⃣ Command‑Line Interface  

```bash
safe-editor [OPTIONS] <file>
```

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help and exit |
| `--init` | Initialise the credential database (`.safe-editor.db`) |
| `--add-user USERNAME` | Add a new user (prompts for password) |
| `--remove-user USERNAME` | Delete a user |
| `--list-users` | List all registered usernames |
| `--gui` | Launch the optional Qt GUI instead of the TUI |
| `--timeout SECS` | Override inactivity lock timeout (default = 300 s) |
| `--no‑hash‑salt` | **⚠️** Store passwords without a salt (for testing only) |

#### Example workflow  

```bash
# Initialise DB (first‑time only)
safe-editor --init

# Add two users
safe-editor --add-user alice
safe-editor --add-user bob

# Edit a file as Alice
safe-editor secret.txt   # you will be prompted for username/password

# Edit a file with GUI
safe-editor --gui diary.md
```

### 2️⃣ Python Library  

Safe‑Editor can be imported and used programmatically.

```python
from safe_editor import SafeEditor, Authenticator, StorageSQLite

# 1️⃣ Choose a storage backend (SQLite by default)
store = StorageSQLite(db_path="my_credentials.db")

# 2️⃣ Create an authenticator
auth = Authenticator(storage=store)

# 3️⃣ Register a user (only once)
auth.register_user("alice", "S3cureP@ssw0rd!")

# 4️⃣ Authenticate
if auth.login("alice", "S3cureP@ssw0rd!"):
    # 5️⃣ Open the editor instance
    editor = SafeEditor(authenticator=auth)
    editor.open_file("notes.txt")
    # The editor runs a blocking TUI loop; when it returns the file is saved.
else:
    raise PermissionError("Invalid credentials")
```

#### Minimal “headless” usage (no UI)  

```python
from safe_editor import Authenticator, StorageSQLite, FileManager

store = StorageSQLite()
auth = Authenticator(store)

auth.register_user("bob", "My$ecret")
assert auth.login("bob", "My$ecret")

fm = FileManager(auth)          # Handles encryption‑aware read/write
content = fm.read("project.py")
print(content)
fm.write("project.py", content + "\n# edited by bob")
```

---  

## API Documentation  

Below is a concise reference for the public API. Full doc‑strings are available in the source (`safe_editor/*.py`) and via `pydoc safe_editor`.

### `safe_editor.auth.Authenticator`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `Authenticator(storage: BaseStorage, *, pepper: bytes = b"")` | Initialise with a storage backend. `pepper` is an optional global secret added to every hash. |
| `register_user` | `register_user(username: str, password: str) -> None` | Hashes `password` with a random 16‑byte salt, stores `username`, `salt`, and `hash`. Raises `UserExistsError` if the name already exists. |
| `login` | `login(username: str, password: str) -> bool` | Verifies the supplied password against the stored hash. On success, sets `self.current_user`. |
| `logout` | `logout() -> None` | Clears the current session. |
| `change_password` | `change_password(username: str, old_pw: str, new_pw: str) -> None` | Validates `old_pw` then updates the stored hash with a fresh salt. |
| `is_authenticated` | `is_authenticated() -> bool` | Returns `True` if a user is logged in. |
| `current_user` | `property` | Returns the username of the logged‑in user (or `None`). |

### `safe_editor.storage.BaseStorage` (abstract)

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_user` | `add_user(username: str, salt: bytes, pwd_hash: bytes) -> None` | Persist a new user record. |
| `get_user` | `get_user(username: str) -> Tuple[bytes, bytes] | None` | Retrieve `(salt, pwd_hash)`