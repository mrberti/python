#%%
import json
from datetime import datetime
import pathlib
import pandas as pd

WORKOUTS_DIR_PATH = r"C:\Users\berti\Desktop\endomondo\Workouts"
OUTPUT_PATH = r"C:\Users\berti\Desktop\endomondo"
STRPTIME_FORMAT = "%Y-%m-%d %H_%M_%S.%f"

WORKOUTS_DIR = pathlib.Path(WORKOUTS_DIR_PATH)
OUTPUT_DIR = pathlib.Path(OUTPUT_PATH)
WORKOUT_FILES = WORKOUTS_DIR.glob("*.json")

# WORKOUT_DATE_STRINGS = [x.stem for x in WORKOUT_FILES]
# WORKOUT_DATES = [datetime.strptime(x, STRPTIME_FORMAT) for x in WORKOUT_DATE_STRINGS]

#%%
WORKOUTS = []
for workout_file in WORKOUT_FILES:
    workout = {
        "filepath": workout_file,
        "datetime": datetime.strptime(workout_file.stem, STRPTIME_FORMAT)
    }
    WORKOUTS.append(workout)

#%%
for workout in WORKOUTS:
    file = workout["filepath"]
    with open(file, "r") as infile:
        workout_data = json.load(infile)
        for item in workout_data:
            key = list(item.keys())[0]
            value = item[key]
            if key.lower() == "points":
                continue
            workout[key] = value

#%%
df = pd.DataFrame(data=WORKOUTS)
df.to_excel(OUTPUT_DIR / "workouts.xlsx")