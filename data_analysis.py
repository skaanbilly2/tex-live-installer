import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

packages_dict = []
with open("packages.json") as inputfile:
    packages_dict = json.load(inputfile)


sizes = {"containersize": [], "doccontainersize": [], "srccontainersize": []}

size_keys = [
    key
    for key in ["containersize", "doccontainersize", "srccontainersize"]
    if key.endswith("containersize")
]
pd.DataFrame()
for package in packages_dict:

    for key in size_keys:
        sizes[key].append(package.get(key, None))


contsize = np.array(sizes["containersize"], dtype=float)
doccontsize = np.array(sizes["doccontainersize"], dtype=float)
srccontsize = np.array(sizes["srccontainersize"], dtype=float)
tot_size = contsize + doccontsize + srccontsize

df = pd.DataFrame(
    {
        "containersize": contsize,
        "doccontainersize": doccontsize,
        "srccontainersize": srccontsize,
        "tot_size": tot_size,
    }
)
print(df.describe())
df.boxplot()
plt.show()

x_labels = [i for i in range(len(contsize))]
plt.plot(x_labels, contsize, label="containersize")
plt.plot(x_labels, doccontsize, label="doccontainersize")
plt.plot(x_labels, srccontsize, label="srccontainersize")
plt.legend()
plt.show()

plt.plot(x_labels, tot_size, label="tot_size")
plt.legend()
plt.show()
