import csv
import os

INPUT = "_logV2.csv"
OUTPUT = "_logV2_with_eventID.csv"

with open(INPUT, "r", encoding="latin-1", newline="") as fin, \
     open(OUTPUT, "w", encoding="utf-8", newline="") as fout:

    reader = csv.reader(fin, delimiter=";")
    writer = csv.writer(fout, delimiter=";")

    header = next(reader)
    writer.writerow(["eventID"] + header)

    for i, row in enumerate(reader, start=1):
        writer.writerow([f"sol-ev{i}"] + row)

print(f"Done. Written to {OUTPUT}")
