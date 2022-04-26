import time
from logging import getLogger

import pandas as pd

logger = getLogger(__name__)


class TimeTracker:
    time_measurements = {
        "name": [],
        "size": [],
        # time measurements
        "get": [],
        "hash": [],
        "extract_write": [],
    }

    def __init__(self, name, size, save_timings: bool = False) -> None:
        self.time = time.time()
        self.tasks = []
        TimeTracker.time_measurements["name"].append(name)
        TimeTracker.time_measurements["size"].append(size)

    def task_done(self, taskname, size=0):
        new_time = time.time()
        task_time = new_time - self.time
        TimeTracker.time_measurements[taskname].append(task_time)
        self.tasks.append((task_time, taskname, size))
        self.time = new_time

    def report(self):
        tot_time = sum((time for (time, label, size) in self.tasks))
        logger.info(f"tot_time: {tot_time}")
        for time, name, size in self.tasks:
            logger.info(
                f"task {name} with size {size} took {100*time/tot_time}% of time"
            )
