import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from workers.blend_watcher import start_blend_watcher

def run_worker(user_id: int = 1, mode="sandbox"):
    print(f"Running worker for user {user_id} in mode {mode}")

if __name__ == "__main__":
    run_worker()