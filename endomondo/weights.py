#%%
import json
from datetime import datetime
import pathlib
import pandas as pd

WEIGHTS_DIR_PATH = r"C:\Users\berti\Desktop\endomondo\Weights"
OUTPUT_PATH = r"C:\Users\berti\Desktop\endomondo"
STRPTIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

WEIGHTS_DIR = pathlib.Path(WEIGHTS_DIR_PATH)
OUTPUT_DIR = pathlib.Path(OUTPUT_PATH)

# WORKOUT_DATE_STRINGS = [x.stem for x in WORKOUT_FILES]
# WORKOUT_DATES = [datetime.strptime(x, STRPTIME_FORMAT) for x in WORKOUT_DATE_STRINGS]

#%%
WEIGHT_FILES = WEIGHTS_DIR.glob("*.json")
WEIGHTS = []
for weight_file in WEIGHT_FILES:
    file = weight_file
    with open(file, "r") as infile:
        weight_data = json.load(infile)
    for item in weight_data:
        data = {
            "date": datetime.strptime(item[1]["date"], STRPTIME_FORMAT),
            "weight": float(item[0]["weight_kg"]),
        }
        WEIGHTS.append(data)
        

#%%
df = pd.DataFrame(data=WEIGHTS)
df = df.sort_values("date")
df.to_excel(OUTPUT_DIR / "weights.xlsx")

#%%
df.plot(x="date", y="weight")