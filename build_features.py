import csv

INPUT       = "_logV2_with_eventID.csv"
OUT_LOG     = "_logV2_normalized.csv"
OUT_FEAT    = "features.csv"

FEAT_COLS   = ["Feature_source", "Action", "Event_category", "App_name"]
EVENT_COLS  = ["eventID", "Date", "Event", "Description", "Actor"]

feat_map = {}   # tuple(feat values) -> featureID

def get_feat_id(row):
    key = tuple(row[c] for c in FEAT_COLS)
    if key not in feat_map:
        feat_map[key] = f"sol-feat{len(feat_map) + 1}"
    return feat_map[key]

with open(INPUT, "r", encoding="utf-8", newline="") as fin, \
     open(OUT_LOG, "w", encoding="utf-8", newline="") as flog:

    reader  = csv.DictReader(fin, delimiter=";")
    log_fields = EVENT_COLS + ["featureID"]
    writer  = csv.DictWriter(flog, fieldnames=log_fields, delimiter=";", extrasaction="ignore")
    writer.writeheader()

    for row in reader:
        fid = get_feat_id(row)
        out = {c: row[c] for c in EVENT_COLS}
        out["featureID"] = fid
        writer.writerow(out)

with open(OUT_FEAT, "w", encoding="utf-8", newline="") as ff:
    writer_f = csv.writer(ff, delimiter=";")
    writer_f.writerow(["featureID"] + FEAT_COLS)
    for key, fid in feat_map.items():
        writer_f.writerow([fid] + list(key))

print(f"Done.")
print(f"  {OUT_LOG}  — normalized log")
print(f"  {OUT_FEAT} — {len(feat_map)} unique feature combos")
