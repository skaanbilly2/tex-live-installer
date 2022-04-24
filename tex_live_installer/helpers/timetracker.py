import time

from logging import getLogger

logger = getLogger(__name__)


class TimeTracker:
    def __init__(self) -> None:
        self.time = time.time()
        self.tasks = []

    def task_done(self, name):
        new_time = time.time()
        self.tasks.append((new_time - self.time, name))
        self.time = new_time

    def report(self):
        tot_time = sum((time for (time, label) in self.tasks))
        logger.info(f"tot_time: {tot_time}")
        for time, name in self.tasks:
            logger.info(f"task {name} took {100*time/tot_time}% of time")
