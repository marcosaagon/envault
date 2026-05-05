"""File watcher for auto-locking .env files on change."""

import time
import hashlib
import threading
from pathlib import Path
from typing import Callable, Optional


def _file_hash(path: Path) -> Optional[str]:
    """Return MD5 hex digest of file contents, or None if file missing."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None


class EnvWatcher:
    """Watch a .env file and trigger a callback when it changes."""

    def __init__(
        self,
        env_path: Path,
        on_change: Callable[[Path], None],
        poll_interval: float = 1.0,
    ):
        self.env_path = Path(env_path)
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_hash: Optional[str] = _file_hash(self.env_path)

    def start(self) -> None:
        """Start watching in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the watcher thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self.poll_interval + 1.0)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            current_hash = _file_hash(self.env_path)
            if current_hash is not None and current_hash != self._last_hash:
                self._last_hash = current_hash
                try:
                    self.on_change(self.env_path)
                except Exception:
                    pass
            self._stop_event.wait(self.poll_interval)

    def reset(self) -> None:
        """Re-baseline the watched file's hash to its current contents.

        Useful after an intentional programmatic write to the file, so the
        next poll does not treat the write as an external change.
        """
        self._last_hash = _file_hash(self.env_path)

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
