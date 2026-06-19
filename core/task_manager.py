import threading
import time
from typing import Dict, Any

class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_task(self, task_id: str, total_steps: int = 100) -> str:
        with self._lock:
            self._tasks[task_id] = {
                'progress': 0,
                'message': '准备中...',
                'total': total_steps,
                'done': False,
                'error': None,
                'start_time': time.time()
            }
        return task_id

    def update_task(self, task_id: str, progress: int, message: str = None):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]['progress'] = min(progress, 100)
                if message:
                    self._tasks[task_id]['message'] = message

    def finish_task(self, task_id: str, error: str = None):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]['done'] = True
                self._tasks[task_id]['progress'] = 100
                if error:
                    self._tasks[task_id]['error'] = error

    def get_task(self, task_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._tasks.get(task_id, {})

    def cleanup(self, max_age: int = 300):
        """清理超过 max_age 秒的已完成任务"""
        now = time.time()
        with self._lock:
            to_delete = []
            for tid, task in self._tasks.items():
                if task.get('done') and (now - task.get('start_time', 0) > max_age):
                    to_delete.append(tid)
            for tid in to_delete:
                del self._tasks[tid]

task_manager = TaskManager()