# Safe‑Editor  
**A user‑authenticated text editor that stores the username and password in SHA‑256 encryption form.**  

---  

## Table of Contents  

| Section | Description |
|---------|-------------|
| **[Installation](#installation)** | How to get Safe‑Editor up and running on Windows, macOS, and Linux. |
| **[Usage](#usage)** | Quick start guide, command‑line options, and GUI launch. |
| **[API Documentation](#api-documentation)** | Public classes, methods, and data structures for developers who want to embed Safe‑Editor or extend it. |
| **[Examples](#examples)** | Real‑world snippets showing authentication, file handling, and custom extensions. |
| **[Contributing](#contributing)** | How to submit bugs, feature requests, and pull requests. |
| **[License](#license)** | MIT License. |

---  

## Installation  

Safe‑Editor is distributed as a **Python package** (≥ 3.9) and also as a **stand‑alone Electron app** for users who prefer a native GUI. Choose the installation method that best fits your workflow.

### 1. Python Package (pip)  

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install Safe‑Editor from PyPI
pip install safe-editor
```

> **Note** – The package pulls in `cryptography`, `PyQt5` (for the optional GUI), and `watchdog` (for file‑system monitoring).  

#### Optional GUI dependencies  

If you only need the CLI, you can skip the GUI extras:

```bash
pip install "safe-editor[cli]"
```

If you want the full desktop experience:

```bash
pip install "safe-editor[gui]"
```

### 2. Stand‑alone Electron App  

> The Electron distribution bundles a pre‑compiled Python runtime, so you don’t need a separate Python installation.

| Platform | Download Link |
|----------|---------------|
| **Windows (x64)** | [Safe‑Editor‑win-x64.zip](https://github.com/yourorg/Safe-Editor/releases/latest) |
| **macOS (Intel & Apple‑Silicon)** | [Safe‑Editor‑mac.dmg](https://github.com/yourorg/Safe-Editor/releases/latest) |
| **Linux (AppImage)** | [Safe‑Editor‑linux-x86_64.AppImage](https://github.com/yourorg/Safe-Editor/releases/latest) |

**Installation steps**

1. **Windows** – Extract the zip, run `Safe-Editor.exe`.  
2. **macOS** – Open the DMG, drag `Safe-Editor.app` to `/Applications`.  
3. **Linux** – Make the AppImage executable and run it:  

   ```bash
   chmod +x Safe-Editor-linux-x86_64.AppImage
   ./Safe-Editor-linux-x86_64.AppImage
   ```

### 3. From Source  

```bash
git clone https://github.com/yourorg/Safe-Editor.git
cd Safe-Editor

# Install development dependencies
pip install -e .[dev]

# Run the test suite (optional but recommended)
pytest -vv
```

---  

## Usage  

Safe‑Editor can be used **via the command line**, **as a library**, or **through the GUI**.  

### 1. CLI Quick‑Start  

```bash
# First run – create an admin account
safe-editor register --username admin

# Launch the editor (will prompt for password)
safe-editor edit my_notes.txt
```

#### CLI Options  

| Option | Alias | Description |
|--------|-------|-------------|
| `--username` | `-u` | Username for login/registration. |
| `--register` | `-r` | Register a new user (prompts for password). |
| `--file` | `-f` | Path to the file to open (default: `stdin`). |
| `--gui` | `-g` | Force GUI mode even when a terminal is attached. |
| `--help` | `-h` | Show help message. |

> **Password handling** – Passwords are never stored in plain text. They are hashed with **SHA‑256** and salted with a per‑user random 16‑byte value before being persisted in the SQLite database (`~/.safe_editor/users.db`).  

### 2. GUI Launch  

```bash
# From a terminal (or double‑click the desktop shortcut)
safe-editor --gui
```

The GUI provides:

* **Login screen** – Username + password fields.  
* **File browser** – Open, create, rename, and delete files within the configured workspace.  
* **Auto‑save** – Changes are saved every 5 seconds or on focus loss.  

### 3. Using Safe‑Editor as a Library  

```python
from safe_editor import Authenticator, TextEditor

# 1️⃣ Authenticate (or register) a user
auth = Authenticator()
if not auth.user_exists("alice"):
    auth.register_user("alice", password="S3cureP@ss")
else:
    auth.login("alice", password="S3cureP@ss")

# 2️⃣ Open an editor instance
editor = TextEditor(authenticated_user=auth.current_user)
editor.open("project/readme.md")
editor.insert_text("\n## New Section\n")
editor.save()
```

---  

## API Documentation  

Below is a concise reference for the public API. Full docstrings are available in the source (`safe_editor/` package) and via `pydoc safe_editor`.  

### `safe_editor.auth.Authenticator`  

| Method | Signature | Description |
|--------|-----------|-------------|
| `register_user` | `register_user(username: str, password: str) -> None` | Creates a new user. Password is salted + hashed with SHA‑256 and stored in `users.db`. Raises `UserExistsError` if the username already exists. |
| `login` | `login(username: str, password: str) -> None` | Verifies credentials. On success, sets `self.current_user`. Raises `AuthenticationError` on failure. |
| `user_exists` | `user_exists(username: str) -> bool` | Returns `True` if the username is present in the DB. |
| `change_password` | `change_password(username: str, old_password: str, new_password: str) -> None` | Validates `old_password` then updates the stored hash. |
| `delete_user` | `delete_user(username: str, password: str) -> None` | Removes a user after verifying the password. |
| `list_users` | `list_users() -> List[str]` | Returns all registered usernames (admin only). |
| `current_user` | `property` | Returns a `User` dataclass instance for the logged‑in user. |

#### `User` dataclass  

```python
@dataclass
class User:
    username: str
    created_at: datetime
    last_login: datetime | None
    is_admin: bool = False
```

### `safe_editor.editor.TextEditor`  

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `TextEditor(authenticated_user: User, workspace: Path = Path.home() / ".safe_editor" / "files")` | Creates an editor bound to a user and a workspace directory. |
| `open` | `open(file_path: Union[str, Path]) -> None` | Loads the file into memory; creates it if it does not exist (subject to write permissions). |
| `save` | `save() -> None` | Writes the in‑memory buffer to disk, updating the file’s modification timestamp. |
| `insert_text` | `insert_text(text: str, position: int | None = None) -> None` | Inserts `text` at `position` (or at the end if `None`). |
| `replace_range` | `replace_range(start: int, end: int, new_text: str) -> None` | Replaces the slice `[start:end]` with `new_text`. |
| `get_content` | `get_content() -> str` | Returns the current buffer as a string. |
| `close` | `close() -> None` | Clears the buffer and optionally prompts to save unsaved changes. |
| `watch_file` | `watch_file(callback: Callable[[Path], None]) -> None` | Starts a watchdog observer that triggers `callback` when the underlying file changes on disk (useful for collaborative scenarios). |

### `safe_editor.utils.crypto` (internal)  

| Function | Signature | Description |
|----------|-----------|-------------|
| `hash_password