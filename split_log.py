import csv

INPUT = "_logV2_with_eventID.csv"
OUT_A = "_logV2_events.csv"        # date, event, description, actor
OUT_B = "_logV2_features.csv"      # feature_source, action, event_category, app_name

COLS_A = ["eventID", "Date", "Event", "Description", "Actor"]
COLS_B = ["eventID", "Feature_source", "Action", "Event_category", "App_name"]

with open(INPUT, "r", encoding="utf-8", newline="") as fin, \
     open(OUT_A, "w", encoding="utf-8", newline="") as fa, \
     open(OUT_B, "w", encoding="utf-8", newline="") as fb:

    reader = csv.DictReader(fin, delimiter=";")
    writer_a = csv.DictWriter(fa, fieldnames=COLS_A, delimiter=";", extrasaction="ignore")
    writer_b = csv.DictWriter(fb, fieldnames=COLS_B, delimiter=";", extrasaction="ignore")

    writer_a.writeheader()
    writer_b.writeheader()

    for row in reader:
        writer_a.writerow({k: row[k] for k in COLS_A})
        writer_b.writerow({k: row[k] for k in COLS_B})

print(f"Done. Written:\n  {OUT_A}\n  {OUT_B}")
