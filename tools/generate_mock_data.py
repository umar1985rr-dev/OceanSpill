"""
Generate realistic mock datasets for the OceanSpill platform.

Produces *valid* data the app can run on plus deliberately *invalid*
files used for negative-testing upload validation and loaders.

Run with the SAME python that runs the backend (has numpy/PIL/pandas):

    python tools/generate_mock_data.py

Everything is seeded -> reproducible. Generated files land in:

  dataset/raw/ais_data/            AIS CSV (+ invalid variants)
  dataset/raw/geographic/          coastline/ports/protected/fishing/...
  dataset/environmental/           mock ocean-current grid
  dataset/samples/satellite_images/  synthetic satellite frames

Note: dataset/raw/ and dataset/environmental/ are gitignored (runtime
data), so this script is the source of truth for regenerating them.
"""

import csv
import math
import random
from pathlib import Path

import numpy as np

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ----------------------------------------------------------------------
# Anchors — Tamil Nadu coast, incident defaults from backend/config.py
# ----------------------------------------------------------------------
CHENNAI = (13.08, 80.27)
REPO = Path(__file__).resolve().parents[1]
AIS_DIR = REPO / "dataset/raw/ais_data"
GEO_DIR = REPO / "dataset/raw/geographic"
ENV_DIR = REPO / "dataset/environmental"
IMG_DIR = REPO / "dataset/samples/satellite_images"

RNG = random.Random(20260831)
NPR = np.random.default_rng(20260831)

# ----------------------------------------------------------------------
# 1. AIS data
# ----------------------------------------------------------------------
AIS_COLUMNS = [
    "MMSI", "BaseDateTime", "LAT", "LON", "SOG", "COG", "Heading",
    "VesselName", "IMO", "VesselType",
]
VESSEL_TYPES = {70: "Cargo", 80: "Tanker", 60: "Passenger", 30: "Fishing",
                52: "Tug", 35: "Military", 36: "Sailing", 40: "HSC"}
VESSEL_NAMES = [
    "OCEAN HARMONY", "SEA PRINCE", "GOLDEN WAVE", "TAMIL MARU", "KAVERI STAR",
    "BAY BREEZE", "COROMANDEL QUEEN", "PALLAVAN PRIDE", "MARINA SPIRIT",
    "NEELAM VENTURE", "COCHIN NAVIGATOR", "MALDIVES EXPRESS", "SRI LANKA SKY",
    "ORISSA PEARL", "DELTA RIDER", "KANYA KUMARI", "DHANUSHKODI", "VELANKANNI",
    "PORTO NOVO", "ROMEO EXPRESS", "NAGA LL", "TUTICORIN TIDE", "CEYLON TRADER",
    "BAY ISLAND", "SOUTHERN CROSS",
]


def _jitter(lat, lon, km):
    """Offset a coordinate by ~km in a random direction (for point data)."""
    deg = km / 111.0
    ang = RNG.uniform(0, 2 * math.pi)
    return lat + deg * math.cos(ang), lon + deg * math.sin(ang) * 1.15


def _make_ais_rows(n, anchor, radius_km, near_incident=0, suspect=0):
    rows = []
    for i in range(n):
        mmsi = 419000000 + RNG.randrange(0, 999999)
        lat, lon = _jitter(*anchor, RNG.uniform(0.5, radius_km))
        # Vessel type weighted toward cargo/tanker near ports
        vtype = RNG.choices(
            [70, 80, 60, 30, 52, 35, 36, 40],
            weights=[30, 25, 10, 15, 5, 5, 5, 5],
        )[0]

        if i < near_incident:
            # clustered around the incident point (a spill zone)
            lat, lon = _jitter(*CHENNAI, RNG.uniform(0.1, 1.5))

        if i < suspect:
            sog = RNG.uniform(12, 22)          # fast movers = suspects
            cog = RNG.uniform(100, 260)        # heading away / across
        else:
            cog = RNG.uniform(0, 359)
            if vtype == 30:
                sog = RNG.uniform(0.1, 5)      # fishing boats loiter
            elif RNG.random() < 0.2:
                sog = 0.0                      # anchored
            else:
                sog = RNG.uniform(3, 14)

        heading = int((cog if RNG.random() < 0.6 else
                      RNG.uniform(0, 359)) % 360)
        rows.append([
            str(mmsi),
            f"2026-08-31 {RNG.randint(0, 23):02d}:{RNG.randint(0, 59):02d}:{RNG.randint(0, 59):02d}",
            round(lat, 5), round(lon, 5),
            round(sog, 1), round(cog, 1), heading,
            RNG.choice(VESSEL_NAMES),
            str(9000000 + RNG.randrange(0, 999999)),
            str(vtype),
        ])
    return rows


def _write_csv(path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  wrote {path.relative_to(REPO)} ({len(rows)} rows)")


def gen_ais():
    print("AIS:")
    valid = []
    valid += _make_ais_rows(45, CHENNAI, 25, near_incident=8, suspect=4)
    valid += _make_ais_rows(25, (8.76, 78.13), 30, suspect=3)      # Gulf of Mannar
    valid += _make_ais_rows(20, (10.77, 79.84), 20)                # Nagapattinam
    valid += _make_ais_rows(10, (11.72, 79.79), 15)                # Cuddalore
    _write_csv(AIS_DIR / "ais_data.csv", AIS_COLUMNS, valid)

    # Alternate valid file for upload success tests
    alt = _make_ais_rows(15, CHENNAI, 30)
    _write_csv(AIS_DIR / "ais_alt_valid.csv", AIS_COLUMNS, alt)

    # INVALID 1: missing required columns (should be REJECTED on upload)
    missing = [r[0:8] for r in _make_ais_rows(6, CHENNAI, 20)]  # drop IMO, VesselType
    _write_csv(
        AIS_DIR / "invalid_missing_cols.csv",
        ["MMSI", "BaseDateTime", "LAT", "LON", "SOG", "COG", "Heading", "VesselName"],
        missing,
    )

    # INVALID 2: all columns present but garbage values (validator only checks
    # column NAMES — this file passes upload but breaks downstream ranking.
    # Deliberate "gotcha" test case.)
    bad = [
        ["419000000", "not-a-date", "north-hundred", "east-many", "fast", "@", 999,
         "", "", ""],
        ["419000001", "2026-08-31 10:00:00", "999", "85.303", "-5", "361", -90,
         "", "", ""],
        ["not-an-int", "2026-08-31 10:00:00", "13.08", "80.27", "1000", "0", 0,
         "", "", ""],
    ]
    _write_csv(AIS_DIR / "invalid_bad_values.csv", AIS_COLUMNS, bad)


# ----------------------------------------------------------------------
# 2. Geographic datasets  (Name/Latitude/Longitude — ImpactDataLoader)
# ----------------------------------------------------------------------
def gen_geographic():
    print("Geographic:")
    # Synthetic coastline hugging the Tamil Nadu east coast
    coast = []
    for i in range(45):
        t = i / 44
        lat = 8.0 + t * (13.4 - 8.0)
        lon = 77.56 + t * (80.4 - 77.56) + math.sin(lat * 2.1) * 0.22
        coast.append([f"Coast Point {i:02d}", round(lat, 4), round(lon, 4)])
    _write_csv(GEO_DIR / "coastlines.csv",
               ["Name", "Latitude", "Longitude"], coast)

    ports = [
        ["Chennai Port", 13.0869, 80.2941],
        ["Ennore Port", 13.2507, 80.3379],
        ["Kattupalli", 13.2920, 80.3650],
        ["Cuddalore", 11.7180, 79.7920],
        ["Karaikal", 10.9240, 79.8320],
        ["Nagapattinam", 10.7670, 79.8440],
        ["Thoothukudi (Tuticorin)", 8.7620, 78.1430],
        ["Colachel", 8.1790, 77.2600],
        ["Kanyakumari", 8.0880, 77.5380],
        ["Rameswaram", 9.2870, 79.3130],
    ]
    _write_csv(GEO_DIR / "ports.csv", ["Name", "Latitude", "Longitude"], ports)

    protected = [
        ["Gulf of Mannar Biosphere Reserve", 9.25, 79.12],
        ["Gulf of Mannar National Park", 9.10, 78.80],
        ["Pulicat Lake Bird Sanctuary", 13.45, 80.20],
        ["Point Calimere Wildlife Sanctuary", 10.30, 79.86],
        ["Vedaranyam Swamp", 10.35, 79.85],
        ["Koonthankulam Bird Sanctuary", 8.49, 77.75],
        ["Chitrangudi Bird Sanctuary", 9.33, 78.43],
        ["Suchindram Theroor WLS", 8.18, 77.43],
    ]
    _write_csv(GEO_DIR / "marine_protected_areas.csv",
               ["Name", "Latitude", "Longitude"], protected)

    fishing = [
        ["Chennai Offshore Zone", 13.20, 80.60],
        ["Coromandel Zone A", 12.20, 80.40],
        ["Cuddalore Grounds", 11.60, 80.20],
        ["Delta Zone", 10.90, 80.10],
        ["Nagapattinam Bank", 10.60, 80.00],
        ["Palk Bay North", 10.10, 79.60],
        ["Palk Strait", 9.80, 79.30],
        ["Gulf of Mannar Zone", 8.90, 78.60],
        ["Thoothukudi Grounds", 8.60, 78.40],
        ["Kanyakumari Deep", 8.00, 77.80],
        ["Rameswaram East", 9.30, 79.80],
        ["Southern Spill Zone", 13.08, 80.27],
    ]
    _write_csv(GEO_DIR / "fishing_zones.csv",
               ["Name", "Latitude", "Longitude"], fishing)

    mangroves = [
        ["Pichavaram Mangrove", 11.4270, 79.7870],
        ["Muthupet Mangrove", 10.3220, 79.4820],
        ["Emballur Mangrove", 13.05, 80.20],
        ["Kodiakkarai Reserve", 10.28, 79.87],
        ["Pulicat Mangrove", 13.52, 80.18],
        ["Coringa (Andhra)", 16.86, 82.30],   # upstream, used for drift reach
    ]
    _write_csv(GEO_DIR / "mangroves.csv", ["Name", "Latitude", "Longitude"], mangroves)

    reefs = [
        ["Mandapam Reef Group", 9.278, 79.156],
        ["Keezhakkarai Reef", 9.233, 78.784],
        ["Appa Island Reef", 9.162, 79.850],
        ["Vembar Reef Group", 9.090, 78.330],
        ["Thoothukudi Reef Group", 8.793, 78.162],
        ["Van Island Reef", 9.219, 79.300],
        ["Krusadai Reef", 9.245, 79.210],
        ["Hare Island Reef", 9.200, 79.195],
    ]
    _write_csv(GEO_DIR / "coral_reefs.csv", ["Name", "Latitude", "Longitude"], reefs)

    # INVALID geographic file (missing 'Longitude') for negative loader tests
    bad = [["A", 1.0], ["B", 2.0]]
    _write_csv(GEO_DIR / "_invalid_missing_col.csv", ["Name", "Latitude"], bad)


# ----------------------------------------------------------------------
# 3. Ocean currents (drift prediction: dataset/environmental/)
# ----------------------------------------------------------------------
def gen_currents():
    print("Ocean currents:")
    rows = []
    for lat in np.arange(7.5, 15.01, 0.5):
        for lon in np.arange(77.0, 82.01, 0.5):
            # southwest monsoon-ish flow; speed higher offshore
            speed = round(float(0.3 + 0.8 * math.sin((lat - 7) / 8 * math.pi) ** 2
                               + NPR.uniform(-0.1, 0.4)), 2)
            speed = max(0.05, speed)
            # direction roughly along the coast (south-west, ~200-260 deg)
            direction = round(float(200 + 50 * math.sin((lon - 77) / 5 * math.pi)
                                   + NPR.uniform(-15, 15)), 1)
            rows.append([round(float(lat), 2), round(float(lon), 2),
                         speed, direction % 360])
    _write_csv(ENV_DIR / "mock_ocean_current.csv",
               ["latitude", "longitude", "current_speed", "current_direction"],
               rows)


# ----------------------------------------------------------------------
# 4. Satellite images — synthetic ocean frames for the simulator feed
# ----------------------------------------------------------------------
def _oil_slick(size, center, radius, thickness):
    """Dark, irregular oil slick mask on a white canvas."""
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    cx, cy = center
    for _ in range(6):
        rx = radius * NPR.uniform(0.7, 1.3)
        ry = radius * NPR.uniform(0.45, 1.1)
        ang = NPR.uniform(0, math.pi)
        dx, dy = rx * math.cos(ang), ry * math.sin(ang)
        d.ellipse([min(cx - dx, cx + dx), min(cy - dy, cy + dy),
                   max(cx - dx, cx + dx), max(cy - dy, cy + dy)],
                  fill=int(255 * NPR.uniform(0.25, 0.8)))
    # elongate streaks down-current
    streak = Image.new("L", size, 0)
    ds = ImageDraw.Draw(streak)
    for _ in range(4):
        sx, sy = center[0] + NPR.uniform(-size[0] * 0.3, size[0] * 0.3), center[1]
        ds.line([sx, sy, sx + NPR.uniform(50, 160), sy + NPR.uniform(-8, 14)],
                fill=int(255 * NPR.uniform(0.15, 0.5)), width=int(NPR.uniform(4, 12)))
    mask = ImageChops.lighter(mask, streak)
    mask = mask.filter(ImageFilter.GaussianBlur(radius / 4))
    mask = mask.point(lambda p: 255 if p > 90 else 0)  # re-threshold for hard edges
    return mask


def _ocean_base(size, shore_on_left=True):
    """Smooth bathymetry-style ocean gradient + water noise."""
    w, h = size
    x = np.linspace(0, 1, w, dtype=np.float32)
    y = np.linspace(0, 1, h, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    # deep blue ocean -> lighter coastal shallows toward the left (land side)
    if shore_on_left:
        depth = 0.35 + 0.45 * np.clip(xx - 0.05, 0, 1) ** 1.4
    else:
        depth = 0.8 - 0.4 * yy
    noise = NPR.normal(0, 0.02, (h, w)).astype(np.float32)
    # low-frequency swell pattern
    swell = 0.05 * np.sin(xx * 14 + yy * 9) * np.cos(yy * 11)
    r = np.clip(8 + 28 * (1 - depth) + 14 * swell + 40 * noise, 0, 255) * 0.45
    g = np.clip(30 + 60 * (1 - depth) + 20 * swell + 60 * noise, 0, 255) * 0.55
    b = np.clip(70 + 160 * depth + 30 * swell + 90 * noise, 0, 255)
    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").filter(ImageFilter.GaussianBlur(1.5))
    return img


def gen_images():
    print("Satellite images:")
    size = (512, 512)
    for i, (cx, cy, rad) in enumerate([
        (0.42, 0.50, 0.16),
        (0.55, 0.36, 0.22),
        (0.38, 0.62, 0.13),
        (0.60, 0.48, 0.27),
        (0.46, 0.30, 0.18),
        (0.50, 0.55, 0.10),
        (0.44, 0.44, 0.20),
        (0.58, 0.40, 0.15),
    ]):
        img = _ocean_base(size)
        slick = _oil_slick(
            size,
            (int(cx * size[0]), int(cy * size[1])),
            int(rad * size[0]),
            thickness=int(0.03 * size[0]),
        )
        black = Image.new("RGB", size, (12, 14, 18))
        img = Image.composite(black, img, slick)
        path = IMG_DIR / f"sim_frame_{i + 1:02d}.png"
        img.save(path)
        print(f"  wrote {path.relative_to(REPO)}")
    print("  (8 frames — enough for the simulator loop)")


def main():
    print(f"Generating mock data into {REPO / 'dataset'}\n")
    gen_ais()
    gen_geographic()
    gen_currents()
    gen_images()
    print("\nDone. Use the /config/upload API or Config page to swap files.")


if __name__ == "__main__":
    main()
