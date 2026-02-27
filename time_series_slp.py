import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
import matplotlib.dates as mdates

# Paul Tol CVD-safe qualitative palette (distinct, no black)
DISTINCT_COLORS = [
    "#0077BB", "#33BBEE", "#009988", "#EE7733", "#CC3311", "#EE3377",
    "#228833", "#4477AA", "#66CCEE", "#AA3377", "#CCBB44", "#EE6677",
    "#44AA99", "#332288", "#DDCC77", "#6699CC", "#882255", "#AA4499",
    "#117733", "#999933", "#CC6677", "#888888"
]

hurdat_file = "HURDAT2.csv" #"hurdat2_extracted_florence_reformatted.csv"

mslp_names = ["MinMSLP_hPa", "mslp", "MSLP", "min_mslp", "slp", "SLP", "Minimum SLP"]
time_names = ["time", "Time", "date", "datetime"]

def find_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# Read HURDAT2 file to get x-axis times
df_hurdat = pd.read_csv(hurdat_file)
time_col = find_column(df_hurdat, time_names)
if not time_col:
    raise ValueError("No time column found in the specified HURDAT2 file.")
hurdat_times = df_hurdat[time_col].values

# Parse as datetime for axis formatting
try:
    times_x = pd.to_datetime(hurdat_times)
except Exception:
    times_x = pd.Series(hurdat_times)

plt.figure(figsize=(13, 7))

csv_files = sorted([f for f in glob.glob("*.csv") if f != hurdat_file])

for i, csv_file in enumerate(csv_files):
    df = pd.read_csv(csv_file)
    mslp_col = find_column(df, mslp_names)
    if not mslp_col:
        print(f"Skipping {csv_file}: Missing MSLP column.")
        continue

    mslp = df[mslp_col].values

    # Align the mslp array to the length of hurdat_times
    if len(mslp) < len(times_x):
        mslp = list(mslp) + [float("nan")] * (len(times_x) - len(mslp))
    elif len(mslp) > len(times_x):
        mslp = mslp[:len(times_x)]

    color = DISTINCT_COLORS[i % len(DISTINCT_COLORS)]
    label = os.path.splitext(csv_file)[0]
    is_era5 = "era5" in csv_file.lower()
    linestyle = '-.' if is_era5 else '-'
    plt.plot(times_x, mslp, marker='o', color=color, linewidth=2, markersize=3, label=label, linestyle=linestyle)

# Plot the HURDAT2 best track MSLP as well (in bold black)
mslp_col_hurdat = find_column(df_hurdat, mslp_names)
if mslp_col_hurdat:
    mslp_hurdat = df_hurdat[mslp_col_hurdat].values
    if len(mslp_hurdat) < len(times_x):
        mslp_hurdat = list(mslp_hurdat) + [float("nan")] * (len(times_x) - len(mslp_hurdat))
    elif len(mslp_hurdat) > len(times_x):
        mslp_hurdat = mslp_hurdat[:len(times_x)]
    plt.plot(times_x, mslp_hurdat, marker='s', color="#000000", linewidth=2.5, markersize=5, label="HURDAT2 Best Track")
else:
    print("HURDAT2 MSLP column not found, not plotted.")

plt.xlabel("Time (from HURDAT2 best track)", fontsize=14)
plt.ylabel("Min Sea Level Pressure (hPa)", fontsize=14)
plt.title("MSLP Time Series (All Tracks, HURDAT2 Time Axis)", fontsize=16)

# Set up tick locator and formatter for every 4th tick, format as YYYY-MM-DD_HH
ax = plt.gca()
if pd.api.types.is_datetime64_any_dtype(times_x):
    locator = mdates.IndexLocator(base=4, offset=0)  # every 4th tick
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d_%H'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=10)
else:
    xticks = range(0, len(times_x), 4)
    ax.set_xticks(xticks)
    labels = [str(times_x[i])[:13].replace(' ', '_') for i in xticks]
    ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)

plt.legend(fontsize=9, loc='lower right', ncol=1)
plt.tight_layout()
plt.grid(True, linestyle="--", alpha=0.5)
plt.savefig("mslp_timeseries.png", dpi=300)
plt.show()
print("Saved MSLP time series to mslp_timeseries.png")

