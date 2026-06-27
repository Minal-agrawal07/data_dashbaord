import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from catalog.crawler import crawl_file, get_csv_folder
from catalog.db import upsert_csv_file, replace_columns


class CSVHandler(FileSystemEventHandler):
    def _handle(self, path: str):
        if not path.endswith(".csv"):
            return
        try:
            info = crawl_file(path)
            file_id = upsert_csv_file(
                info["filename"], info["filepath"], info["row_count"], info["last_modified"]
            )
            replace_columns(file_id, info["columns"])
            print(f"[watcher] Updated schema for {info['filename']}")
        except Exception as e:
            print(f"[watcher] Error processing {path}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle(event.src_path)


_observer: Observer | None = None


def start_watcher():
    global _observer
    folder = get_csv_folder()
    folder.mkdir(parents=True, exist_ok=True)

    handler = CSVHandler()
    _observer = Observer()
    _observer.schedule(handler, str(folder), recursive=False)

    thread = threading.Thread(target=_observer.start, daemon=True)
    thread.start()
    print(f"[watcher] Watching {folder}")


def stop_watcher():
    global _observer
    if _observer:
        _observer.stop()
        _observer.join()
