import os
import glob
import csv
import re

input_dir = "."
output_dir = "csv_output"
os.makedirs(output_dir, exist_ok=True)

target_headers = ["time", "center_lat", "center_lon", "MinMSLP_hPa", "MaxWind_mps"]

YEAR = 2018  # <<-- Change this if you want a fixed year for all files

def extract_year_from_filename(filename):
    # If your filename includes a year, e.g. florence_2018.txt, use this function
    m = re.search(r'(\d{4})', filename)
    return int(m.group(1)) if m else YEAR

def convert_time(timestr, year):
    # Expects timestr like '09/10/1200'
    try:
        mm, dd, hhmm = timestr.split('/')
        hh = hhmm[:2]
        mi = hhmm[2:]
        # Sometimes mi might be missing (e.g. '1200' -> '12','00')
        if not mi:
            mi = "00"
        return f"{year}-{int(mm):02d}-{int(dd):02d}_{int(hh):02d}:{mi}:00"
    except Exception as e:
        # If something goes wrong, just return original string
        return timestr

def process_dat_file(filepath):
    basename = os.path.basename(filepath)
    name, _ = os.path.splitext(basename)
    csvfile = os.path.join(output_dir, name + ".csv")
    with open(filepath, "r") as f_in, open(csvfile, "w", newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(target_headers)
        header_found = False
        year = extract_year_from_filename(name)
        for line in f_in:
            if not line.strip():
                continue
            parts = [p for p in line.strip().split() if p]
            if not header_found and all(h in parts for h in ["ADV", "LAT", "LON", "TIME", "WIND", "PR", "STAT"]):
                header_found = True
                continue
            if not header_found:
                continue
            if len(parts) < 7:
                continue
            lat, lon, time_raw, wind, pr = parts[1], parts[2], parts[3], parts[4], parts[5]
            time_fmt = convert_time(time_raw, year)
            writer.writerow([time_fmt, lat, lon, pr, wind])
    print(f"Converted {filepath} → {csvfile}")

def process_txt_file(filepath):
    basename = os.path.basename(filepath)
    name, _ = os.path.splitext(basename)
    csvfile = os.path.join(output_dir, name + ".csv")
    year = extract_year_from_filename(name)
    with open(filepath, "r") as f_in, open(csvfile, "w", newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(target_headers)
        data_started = False
        for line in f_in:
            if not line.strip():
                continue
            parts = [p for p in line.strip().split() if p]
            if not data_started:
                data_started = True
                continue
            if len(parts) < 5:
                continue
            time_raw, lat, lon, minslp, maxwind = parts[0], parts[1], parts[2], parts[3], parts[4]
            time_fmt = convert_time(time_raw, year)
            writer.writerow([time_fmt, lat, lon, minslp, maxwind])
    print(f"Converted {filepath} → {csvfile}")

def main():
    dat_files = glob.glob(os.path.join(input_dir, "*.dat"))
    txt_files = glob.glob(os.path.join(input_dir, "*.txt"))
    if not dat_files and not txt_files:
        print("No .dat or .txt files found.")
        return
    for filepath in dat_files:
        process_dat_file(filepath)
    for filepath in txt_files:
        process_txt_file(filepath)

if __name__ == "__main__":
    main()

