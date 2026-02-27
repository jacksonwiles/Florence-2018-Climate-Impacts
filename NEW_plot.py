import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pandas as pd
import glob
import os
import math

# Paul Tol CVD-safe qualitative palette (distinct, no black)
DISTINCT_COLORS = [
    "#0077BB", "#33BBEE", "#009988", "#EE7733", "#CC3311", "#EE3377",
    "#228833", "#4477AA", "#66CCEE", "#AA3377", "#CCBB44", "#EE6677",
    "#44AA99", "#332288", "#DDCC77", "#6699CC", "#882255", "#AA4499",
    "#117733", "#999933", "#CC6677", "#888888"
]

hurdat_file = "HURDAT2.csv"  # ensure parity with time-series scripts

savefig_name = "all_tracks.png"
zoom_savefig_name = "all_tracks_landfall_zoom.png"

lat_names = ["center_lat", "lat", "latitude", "Lat", "Latitude"]
lon_names = ["center_lon", "lon", "longitude", "Lon", "Longitude"]

def find_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

def plot_tracks(ax, lons_list, lats_list, colors, labels, landfall_points=None, show_star=False):
    n = len(lons_list)
    for i, (lons_plot, lats_plot, label) in enumerate(zip(lons_list, lats_list, labels)):
        color = colors[i % len(colors)]
        ax.plot(
            lons_plot, lats_plot, '-o', color=color, markersize=3, linewidth=2.2,
            label=label, zorder=10
        )
        ax.scatter(lons_plot[0], lats_plot[0], color=color, s=65, marker='o', zorder=20)
        ax.scatter(lons_plot[-1], lats_plot[-1], color=color, s=65, marker='X', zorder=20)
        ax.text(
            lons_plot[0], lats_plot[0]+0.3, "Start", fontsize=8, color=color,
            ha="center", weight="bold", zorder=25,
            bbox=dict(facecolor='white', alpha=0.7, lw=0)
        )
        ax.text(
            lons_plot[-1], lats_plot[-1]-0.3, "End", fontsize=8, color=color,
            ha="center", weight="bold", zorder=25,
            bbox=dict(facecolor='white', alpha=0.7, lw=0)
        )
        # Draw jittered star marker (but no label) if requested and available
        if show_star and landfall_points is not None and landfall_points[i] is not None:
            x, y = landfall_points[i]
            angle = (2 * math.pi * i) / max(n, 1)
            offset_radius = 0.08  # degrees; adjust if needed
            x_jit = x + offset_radius * math.cos(angle)
            y_jit = y + offset_radius * math.sin(angle)
            ax.scatter(
                x_jit, y_jit, color=color, edgecolor='black', marker='*', s=160, zorder=200,
                linewidth=1.5, label=None
            )

def plot_hurdat2(ax, hurdat_track, show_star=False):
    """Plot HURDAT2 in solid black with start/end markers (and optional star)."""
    if hurdat_track is None:
        return
    lons_plot, lats_plot, landfall_point = hurdat_track
    color = "#000000"
    ax.plot(lons_plot, lats_plot, '-o', color=color, markersize=3, linewidth=2.8,
            label="HURDAT2 Best Track", zorder=50)
    ax.scatter(lons_plot[0], lats_plot[0], color=color, s=70, marker='o', zorder=60)
    ax.scatter(lons_plot[-1], lats_plot[-1], color=color, s=70, marker='X', zorder=60)
    ax.text(lons_plot[0], lats_plot[0]+0.3, "Start", fontsize=8, color=color,
            ha="center", weight="bold", zorder=65,
            bbox=dict(facecolor='white', alpha=0.7, lw=0))
    ax.text(lons_plot[-1], lats_plot[-1]-0.3, "End", fontsize=8, color=color,
            ha="center", weight="bold", zorder=65,
            bbox=dict(facecolor='white', alpha=0.7, lw=0))
    if show_star and landfall_point is not None:
        x, y = landfall_point
        ax.scatter(x, y, color=color, edgecolor='white', marker='*', s=180, zorder=200, linewidth=1.2)

# === MAIN PROCESSING ===

lats_list, lons_list, times_list, labels, landfall_points = [], [], [], [], []

# Match time-series behavior: exclude HURDAT2.csv and sort
all_csv = sorted([f for f in glob.glob("*.csv") if os.path.basename(f) != hurdat_file])

# Build a stable filename -> color map identical to time-series ordering
file_bases = [os.path.splitext(os.path.basename(f))[0] for f in all_csv]
color_map = {base: DISTINCT_COLORS[i % len(DISTINCT_COLORS)] for i, base in enumerate(file_bases)}

for i, csv_file in enumerate(all_csv):
    df = pd.read_csv(csv_file)
    lat_col = find_column(df, lat_names)
    lon_col = find_column(df, lon_names)
    time_col = find_column(df, ["time", "Time", "date", "datetime"])

    if not lat_col or not lon_col:
        print(f"Skipping {csv_file}: Missing lat/lon columns.")
        continue

    lats = df[lat_col].values
    lons = df[lon_col].values
    times = df[time_col].values if time_col else None

    # Convert lons if needed (to -180..180)
    lons = np.where(lons > 180, lons - 360, lons)

    # Mask non-finite
    valid = np.isfinite(lats) & np.isfinite(lons)
    lats_plot = lats[valid]
    lons_plot = lons[valid]
    times_plot = np.array(times)[valid] if times is not None else None

    if len(lats_plot) == 0 or len(lons_plot) == 0:
        print(f"Skipping {csv_file}: No valid track points.")
        continue

    # Find landfall point index (time containing '09-14_12')
    if times_plot is not None:
        match_idx = [j for j, t in enumerate(times_plot) if "09-14_12" in str(t)]
        if match_idx:
            j = match_idx[0]
            landfall_points.append((lons_plot[j], lats_plot[j]))
        else:
            landfall_points.append(None)
    else:
        landfall_points.append(None)

    lats_list.append(lats_plot)
    lons_list.append(lons_plot)
    times_list.append(times_plot)
    labels.append(os.path.splitext(os.path.basename(csv_file))[0])

# Colors aligned to labels (and thus to the time-series scripts)
colors_aligned = [color_map[label] for label in labels]

# --- Prepare HURDAT2 track (optional; plotted in black) ---
hurdat_track = None
if os.path.exists(hurdat_file):
    try:
        df_h = pd.read_csv(hurdat_file)
        lat_h = find_column(df_h, lat_names)
        lon_h = find_column(df_h, lon_names)
        time_h = find_column(df_h, ["time", "Time", "date", "datetime"])
        if lat_h and lon_h:
            lats_h = df_h[lat_h].values
            lons_h = df_h[lon_h].values
            lons_h = np.where(lons_h > 180, lons_h - 360, lons_h)
            valid_h = np.isfinite(lats_h) & np.isfinite(lons_h)
            lats_h_plot = lats_h[valid_h]
            lons_h_plot = lons_h[valid_h]
            landfall_h = None
            if time_h:
                times_h = np.array(df_h[time_h].values)[valid_h]
                match_idx_h = [j for j, t in enumerate(times_h) if "09-14_12" in str(t)]
                if match_idx_h:
                    jh = match_idx_h[0]
                    landfall_h = (lons_h_plot[jh], lats_h_plot[jh])
            if len(lats_h_plot) > 0 and len(lons_h_plot) > 0:
                hurdat_track = (lons_h_plot, lats_h_plot, landfall_h)
        else:
            print("HURDAT2 lat/lon columns not found; skipping HURDAT2 plot.")
    except Exception as e:
        print(f"Failed to read/plot HURDAT2: {e}")

# ----------------------
# Plot 1: Full domain (no stars on HURDAT2)
# ----------------------
fig = plt.figure(figsize=(11, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.LAND, zorder=0)
ax.add_feature(cfeature.OCEAN, zorder=0)
ax.add_feature(cfeature.COASTLINE, zorder=1, linewidth=0.7)
ax.add_feature(cfeature.BORDERS, zorder=1, linestyle=":")
ax.gridlines(draw_labels=True, linewidth=0.4, color='gray', alpha=0.5, linestyle='--')

# Collect min/max for domain extent
lonmin, lonmax, latmin, latmax = 360, -360, 90, -90
for lons_plot, lats_plot in zip(lons_list, lats_list):
    lonmin = min(lonmin, lons_plot.min())
    lonmax = max(lonmax, lons_plot.max())
    latmin = min(latmin, lats_plot.min())
    latmax = max(latmax, lats_plot.max())

plot_tracks(ax, lons_list, lats_list, colors_aligned, labels, landfall_points, show_star=False)
# Plot HURDAT2 in black (doesn't affect other colors)
plot_hurdat2(ax, hurdat_track, show_star=False)

ax.set_extent([lonmin - 3, lonmax + 3, latmin - 3, latmax + 3])
ax.set_title("All Tracks Comparison", fontsize=16)
ax.legend(loc='upper right', fontsize=9)
plt.tight_layout()
plt.savefig(savefig_name, dpi=300)
plt.close(fig)
print(f"Saved combined track plot to {savefig_name}")

# ----------------------
# Plot 2: Zoomed on landfall region (with jittered stars for others; solid star for HURDAT2)
# ----------------------
landfall_lons = [pt[0] for pt in landfall_points if pt is not None]
landfall_lats = [pt[1] for pt in landfall_points if pt is not None]
if hurdat_track is not None and hurdat_track[2] is not None:
    landfall_lons.append(hurdat_track[2][0])
    landfall_lats.append(hurdat_track[2][1])

if landfall_lons and landfall_lats:
    lonmin_zoom = min(landfall_lons) - 2
    lonmax_zoom = max(landfall_lons) + 2
    latmin_zoom = min(landfall_lats) - 2
    latmax_zoom = max(latmax, max(landfall_lats) + 2)

    fig2 = plt.figure(figsize=(11, 8))
    ax2 = plt.axes(projection=ccrs.PlateCarree())
    ax2.add_feature(cfeature.LAND, zorder=0)
    ax2.add_feature(cfeature.OCEAN, zorder=0)
    ax2.add_feature(cfeature.COASTLINE, zorder=1, linewidth=0.7)
    ax2.add_feature(cfeature.BORDERS, zorder=1, linestyle=":")
    ax2.gridlines(draw_labels=True, linewidth=0.4, color='gray', alpha=0.5, linestyle='--')

    plot_tracks(ax2, lons_list, lats_list, colors_aligned, labels, landfall_points, show_star=True)
    # Plot HURDAT2 in black and (if available) a white-edged star at landfall
    plot_hurdat2(ax2, hurdat_track, show_star=True)

    ax2.set_extent([lonmin_zoom, lonmax_zoom, latmin_zoom, latmax_zoom])
    ax2.set_title("Landfall Zoom: All Tracks", fontsize=16)
    ax2.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(zoom_savefig_name, dpi=300)
    plt.close(fig2)
    print(f"Saved zoomed landfall plot to {zoom_savefig_name}")
else:
    print("No '09-14_12' points found for zoomed landfall plot.")

