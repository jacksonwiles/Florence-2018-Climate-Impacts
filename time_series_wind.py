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

wind_names = ["MaxWind_mps", "max_wind", "vmax", "wind", "Wind", "WindSpeed", "windspeed"]
time_names = ["time", "Time", "date", "datetime"]

def find_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

df_hurdat = pd.read_csv(hurdat_file)
time_col = find_column(df_hurdat, time_names)
if not time_col:
    raise ValueError("No time column found in the specified HURDAT2 file.")
hurdat_times = df_hurdat[time_col].values

try:
    times_x = pd.to_datetime(hurdat_times)
except Exception:
    times_x = pd.Series(hurdat_times)

plt.figure(figsize=(13, 7))

csv_files = sorted([f for f in glob.glob("*.csv") if f != hurdat_file])

for i, csv_file in enumerate(csv_files):
    df = pd.read_csv(csv_file)
    wind_col = find_column(df, wind_names)
    if not wind_col:
        print(f"Skipping {csv_file}: Missing wind column.")
        continue

    wind = df[wind_col].values
    if len(wind) < len(times_x):
        wind = list(wind) + [float("nan")] * (len(times_x) - len(wind))
    elif len(wind) > len(times_x):
        wind = wind[:len(times_x)]

    color = DISTINCT_COLORS[i % len(DISTINCT_COLORS)]
    label = os.path.splitext(csv_file)[0]
    is_era5 = "era5" in csv_file.lower()
    linestyle = '-.' if is_era5 else '-'
    plt.plot(times_x, wind, marker='o', color=color, linewidth=2, markersize=3, label=label, linestyle=linestyle)

wind_col_hurdat = find_column(df_hurdat, wind_names)
if wind_col_hurdat:
    wind_hurdat = df_hurdat[wind_col_hurdat].values
    if len(wind_hurdat) < len(times_x):
        wind_hurdat = list(wind_hurdat) + [float("nan")] * (len(times_x) - len(wind_hurdat))
    elif len(wind_hurdat) > len(times_x):
        wind_hurdat = wind_hurdat[:len(times_x)]
    plt.plot(times_x, wind_hurdat, marker='s', color="#000000", linewidth=2.5, markersize=5, label="HURDAT2 Best Track")
else:
    print("HURDAT2 wind column not found, not plotted.")

plt.xlabel("Time (from HURDAT2 best track)", fontsize=14)
plt.ylabel("Wind Speed (m/s)", fontsize=14)
plt.title("Wind Speed Time Series (All Tracks, HURDAT2 Time Axis)", fontsize=16)

ax = plt.gca()
if pd.api.types.is_datetime64_any_dtype(times_x):
    locator = mdates.IndexLocator(base=4, offset=0)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d_%H'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right', fontsize=10)
else:
    xticks = range(0, len(times_x), 4)
    ax.set_xticks(xticks)
    labels = [str(times_x[i])[:13].replace(' ', '_') for i in xticks]
    ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)

plt.legend(fontsize=9, loc='upper right', ncol=1)
plt.tight_layout()
plt.grid(True, linestyle="--", alpha=0.5)
plt.savefig("wind_timeseries.png", dpi=300)
plt.show()
print("Saved wind speed time series to wind_timeseries.png")

