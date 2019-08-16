import time
import datetime
import json
import matplotlib.pyplot as plt

with open("endomondo_weights.json", "r") as f:
    data = f.read()

data_j = json.loads(data)

weights = list()
dates = list()
data_out = list()
for data in data_j:
    weight = float(data[0]["weight_kg"])
    weights.append(weight)
    date = data[1]["date"]
    timestamp = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").timetuple())
    dates.append(timestamp)
    data_out.append((timestamp, weight))

def sortKey(val):
    return val[0]

data_out.sort(key=sortKey)
X = list(zip(*data_out))
print(X)
plt.plot(X[0], X[1])
plt.show()

with open("out.csv","w") as f:
    for data in data_out:
        line = "{},{}\n".format(data[0], data[1])
        # print(line)
        f.write(line)
