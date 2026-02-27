import pandas as pd

# === USER INPUTS ===
input_csv = "florence_era5_track_hourly_reformatted.csv"     # Path to your input CSV
output_csv = "florence_era5_track_hourly_reformatted_lon.csv"     # Path to your output CSV

# === READ CSV ===
df = pd.read_csv(input_csv)

# === DETECT LONGITUDE COLUMN NAME ===
if "longitude" in df.columns:
    lon_col = "longitude"
elif "lon" in df.columns:
    lon_col = "lon"
else:
    raise ValueError("No 'longitude' or 'lon' column found in CSV.")

# === CONVERT LONGITUDE TO -180 to 180 ===
df[lon_col] = ((df[lon_col] + 180) % 360) - 180

# === SAVE TO NEW CSV ===
df.to_csv(output_csv, index=False)
print(f"Saved updated CSV with -180..180 longitude to: {output_csv}")

