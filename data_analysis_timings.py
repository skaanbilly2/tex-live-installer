import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

timings_dict = []
with open("timings.json") as inputfile:
    timings_dict = json.load(inputfile)



time_keys = [
    key
    for key in timings_dict.keys()
    if key not in ("name", "size")
]

size = np.array(timings_dict["size"], dtype=float)

task_timings = { key: np.array(timings_dict[key], dtype=float) for key in time_keys }

df = pd.DataFrame(
    {
        "size": size,
        **task_timings
    }
)
print(df.describe())
df.boxplot()
plt.show()
df.boxplot(column="size")
plt.show()
df.boxplot(column=time_keys)
plt.show()


df = df.sort_values(by=["size"])

# time spent on each task
for key in time_keys:
    plt.loglog(df.loc[:, "size"], df.loc[:, key], label=key)
plt.loglog(df.loc[:,"size"], df.loc[:,"size"], label="size")
plt.legend()
plt.show()



# Proportional time spent in each task
def sum_row(row, keys):
    return sum(row[key] for key in keys)

df['tot_time'] = df.apply(lambda row: sum_row(row, keys=time_keys), axis=1)
for key in time_keys:
    plt.loglog(df.loc[:, "size"], df.loc[:, key] / df["tot_time"], label=key)
plt.legend()
plt.show()