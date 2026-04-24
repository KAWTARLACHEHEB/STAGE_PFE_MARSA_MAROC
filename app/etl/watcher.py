import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pipeline import MarsaETL
from pathlib import Path

class BaplieWatcherHandler(FileSystemEventHandler):
    """
    Detecte les nouveaux fichiers dans data/raw et lance l'ETL.
    """
    def __init__(self):
        self.etl = MarsaETL()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            print(f"🔍 Changement detecte : {event.src_path}")
            print("⏳ Declenchement du pipeline ETL...")
            self.etl.run_pipeline()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            print(f"✨ Nouveau fichier detecte : {event.src_path}")
            print("⏳ Declenchement du pipeline ETL...")
            self.etl.run_pipeline()

if __name__ == "__main__":
    # Dossier a surveiller
    path_to_watch = str(Path(__file__).resolve().parent.parent.parent / "data" / "raw")
    
    event_handler = BaplieWatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    
    print(f"📡 Surveillant Marsa Maroc actif sur : {path_to_watch}")
    print("En attente de nouveaux fichiers CSV...")
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
