from core.execution import Executor

class SessionManager:
    def __init__(self, executor: Executor):
        self.executor = executor
        self.is_running = False

    def run(self):
        self.is_running = True
        print("Торговая сессия стартовала.")

    def stop(self):
        self.executor.drain_positions()
        self.is_running = False
        print("Торговая сессия остановлена.")