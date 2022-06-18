import uuid
import os
import random
from datetime import datetime
from pathlib import Path

os.chdir("/home/simon/svn/test")

dirs = [
    "a",
    "a/b",
    "a/b/c",
    "a/b/c/d",
    "a/b/c/d/e",
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

for i in range(1000):
    path = random.choice(dirs)
    f_name = f"{path}/{uuid.uuid4()}.txt"
    content = f"""\
file: {f_name}
date: {datetime.now()}
"""
    # print(f_name)
    # print(content)
    with open(f_name, "w") as fout:
        fout.write(content)