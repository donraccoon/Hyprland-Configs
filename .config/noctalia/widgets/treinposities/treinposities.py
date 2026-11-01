#!/usr/bin/env python3
"""
Treinposities.nl Waybar Widget & Trip Planner
Provides real-time Dutch train departure times, vehicle tracking, and trip planning.
"""

import sys
import os
import json
import time
import re
import html
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
STATIONS_FILE = os.path.join(SCRIPT_DIR, "stations.json")
CACHE_DIR = os.path.expanduser("~/.cache/waybar-treinposities")
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_CONFIG = {
    "mode": "station",  # "station" or "trip"
    "current_station": "Utrecht Centraal",
    "trip_from": "Utrecht Centraal",
    "trip_to": "Amsterdam Centraal",
    "favorites": [
        "Utrecht Centraal",
        "Amsterdam Centraal",
        "Rotterdam Centraal",
        "Den Haag Centraal",
        "Schiphol Airport",
        "Eindhoven Centraal",
        "Arnhem Centraal"
    ],
    "max_tooltip_departures": 10,
    "max_tooltip_trips": 4,
    "show_material": True,
    "cache_ttl_seconds": 25,
    "waybar_signal": 8
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(data)
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        sys.stderr.write(f"Error saving config: {e}\n")

# ---------------------------------------------------------
# Stations Database
# ---------------------------------------------------------

def load_stations():
    if os.path.exists(STATIONS_FILE):
        try:
            with open(STATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

STATIONS = load_stations()

def find_station(query):
    """Finds a station by name, code, or slug."""
    if not query:
        return None
    q = query.strip().lower()
    
    # 1. Exact match on code
    for s in STATIONS:
        if s.get("code", "").lower() == q:
            return s
            
    # 2. Exact match on name
    for s in STATIONS:
        if s.get("name", "").lower() == q:
            return s
            
    # 3. Exact match on slug
    for s in STATIONS:
        if s.get("slug", "").lower() == q:
            return s
            
    # 4. Name starts with query
    for s in STATIONS:
        if s.get("name", "").lower().startswith(q):
            return s
            
    # 5. Query in name
    for s in STATIONS:
        if q in s.get("name", "").lower():
            return s
            
    # Fallback: create slug from query
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', q).strip('-')
    return {"name": query, "code": query[:3].title(), "slug": slug}

def get_station_slug(name):
    st = find_station(name)
    return st["slug"] if st else re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')

def get_station_code(name):
    st = find_station(name)
    if st and st.get("code"):
        return st["code"]
    return name[:3]

# ---------------------------------------------------------
# Caching & HTTP Requests
# ---------------------------------------------------------

def fetch_url(url, timeout=7):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")

def get_cached(key, ttl):
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_path):
        try:
            mtime = os.path.getmtime(cache_path)
            if time.time() - mtime < ttl:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
    return None

def set_cached(key, data):
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass

def format_duration(dur_str):
    if not dur_str:
        return ""
    parts = dur_str.split(":")
    if len(parts) == 2:
        try:
            h = int(parts[0])
            m = int(parts[1])
            if h == 0:
                return f"{m}m"
            return f"{h}u {m:02d}m"
        except ValueError:
            pass
    return dur_str

# ---------------------------------------------------------
# Treinposities.nl Scrapers
# ---------------------------------------------------------

def fetch_departures(station_name, force=False):
    st = find_station(station_name)
    slug = st["slug"] if st else get_station_slug(station_name)
    cache_key = f"dep_{slug}"
    
    cfg = load_config()
    ttl = cfg.get("cache_ttl_seconds", 25)
    
    if not force:
        cached = get_cached(cache_key, ttl)
        if cached is not None:
            return cached

    url = f"https://treinposities.nl/ajax/vts/{slug}"
    try:
        content = fetch_url(url)
    except Exception as e:
        stale = get_cached(cache_key, 3600)
        if stale is not None:
            return stale
        return {"error": f"Kan data niet ophalen ({e})", "departures": []}

    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")
    departures = []

    for r in rows:
        cols = r.find_all("td")
        if len(cols) < 4:
            continue

        # Column 0: Time & delay
        time_div = cols[0].find("div", class_="vts_time")
        dep_time = ""
        delay_str = ""
        rit_url = ""
        if time_div:
            a_tag = time_div.find("a")
            if a_tag:
                dep_time = a_tag.get_text(strip=True)
                rit_url = a_tag.get("href", "")
            else:
                dep_time = time_div.get_text(strip=True)
            delay_el = time_div.find("span", class_="vts_delay")
            if delay_el:
                delay_str = delay_el.get_text(strip=True)

        countdown_div = cols[0].find("div", class_="vts_vwvtime")
        countdown = countdown_div.get_text(strip=True) if countdown_div else ""

        # Column 1: Destination, via, alerts, material
        dest_div = cols[1].find("div", class_="vts_destination")
        dest = dest_div.get_text(strip=True) if dest_div else ""

        alert_el = cols[1].find(class_="vts_alert")
        alert = alert_el.get_text(strip=True) if alert_el else ""

        is_cancelled = False
        if alert and ("rijdt niet" in alert.lower() or "vervallen" in alert.lower()):
            is_cancelled = True

        via_el = cols[1].find("div", style=lambda s: s and "font-size: 14px" in s)
        via = via_el.get_text(" ", strip=True) if via_el else ""

        mat_info = []
        for m in cols[1].find_all("div", class_="vts_matinfo"):
            txt = m.get_text(" ", strip=True)
            if txt:
                mat_info.append(txt)

        # Seats
        seats_el = cols[0].find("abbr")
        seats = seats_el.get_text(strip=True) if seats_el else ""

        # Column 2: Platform
        platform = cols[2].get_text(strip=True)
        if not platform:
            plat_sm = cols[0].find("div", class_="vts_platform")
            if plat_sm:
                platform = plat_sm.get_text(strip=True).replace("Sp", "").strip()

        platform_changed = "vts_platform_changed" in cols[2].get("class", []) or (
            cols[0].find("div", class_="vts_platform_changed") is not None
        )

        # Column 3: Train type & number
        train_type = cols[3].get_text(strip=True)
        if not train_type:
            tt_sm = cols[1].find("div", class_="d-block d-sm-none")
            if tt_sm:
                train_type = tt_sm.get_text(strip=True)

        departures.append({
            "time": dep_time,
            "delay": delay_str,
            "countdown": countdown,
            "platform": platform,
            "platform_changed": platform_changed,
            "destination": dest,
            "train": train_type,
            "via": via,
            "alert": alert,
            "cancelled": is_cancelled,
            "material": mat_info,
            "seats": seats,
            "rit_url": rit_url
        })

    result = {
        "station_name": st["name"] if st else station_name,
        "station_code": st.get("code", "") if st else "",
        "station_slug": slug,
        "updated_at": datetime.now().strftime("%H:%M:%S"),
        "departures": departures
    }
    set_cached(cache_key, result)
    return result

def fetch_trips(from_station, to_station, dep_time=None, dep_date=None, force=False):
    st_from = find_station(from_station)
    st_to = find_station(to_station)

    name_from = st_from["name"] if st_from else from_station
    name_to = st_to["name"] if st_to else to_station

    now = datetime.now()
    if not dep_date:
        dep_date = now.strftime("%Y-%m-%d")
    if not dep_time:
        dep_time = now.strftime("%H:%M")

    safe_from = re.sub(r'[^a-zA-Z0-9]+', '_', name_from.lower())
    safe_to = re.sub(r'[^a-zA-Z0-9]+', '_', name_to.lower())
    cache_key = f"trip_{safe_from}_{safe_to}"

    cfg = load_config()
    ttl = cfg.get("cache_ttl_seconds", 30)

    if not force:
        cached = get_cached(cache_key, ttl)
        if cached is not None:
            return cached

    params = {
        "frow[van_station]": name_from,
        "frow[naar_station]": name_to,
        "frow[datum]": dep_date,
        "frow[welketijd]": "v",
        "frow[tijd]": dep_time
    }
    url = f"https://treinposities.nl/reisplanner/verbindingen/?{urllib.parse.urlencode(params)}"

    try:
        content = fetch_url(url, timeout=9)
    except Exception as e:
        stale = get_cached(cache_key, 3600)
        if stale is not None:
            return stale
        return {"error": f"Kan reisadvies niet ophalen ({e})", "trips": []}

    soup = BeautifulSoup(content, "html.parser")
    trip_divs = soup.find_all("div", class_="rp-trip")
    trips = []

    for trip_div in trip_divs:
        txt = trip_div.get_text(" ", strip=True)
        m = re.search(r'Vertrek:\s*([0-9:]+)\s*-\s*Aankomst\s*([0-9:]+)', txt)
        t_dep = m.group(1) if m else ""
        t_arr = m.group(2) if m else ""

        dur_m = re.search(r'Reistijd:\s*([0-9:]+)', txt)
        duration_raw = dur_m.group(1) if dur_m else ""
        duration = format_duration(duration_raw)

        trans_m = re.search(r'Overstap:\s*([^<\n]+)', txt)
        if trans_m:
            transfers = f"{trans_m.group(1).strip()} overstap"
        elif "rechtstreeks" in txt.lower():
            transfers = "Rechtstreeks"
        else:
            transfers = "0 overstap"

        legs = []
        details = trip_div.find_next_sibling("div")
        has_delay = False
        is_cancelled = False

        if details:
            for leg_div in details.find_all("div", class_="rp-leg"):
                from_div = leg_div.find(class_="rp-from")
                train_div = leg_div.find(class_="rp-train")
                to_div = leg_div.find(class_="rp-to")

                # Clean origin station and delay
                f_plat = ""
                f_delay = ""
                f_name = ""
                if from_div:
                    f_plat_el = from_div.find(class_="vts_platform")
                    if f_plat_el:
                        f_plat = f_plat_el.get_text(strip=True).replace("Sp", "").strip()
                    
                    c10 = from_div.find(class_="col-10")
                    if c10:
                        f_del_el = c10.find(class_="rp-vertr")
                        if f_del_el:
                            f_delay = f_del_el.get_text(strip=True)
                            if f_delay:
                                has_delay = True
                            f_del_el.decompose()
                        raw_c10 = c10.get_text(" ", strip=True)
                        # Remove leading time like "11:09 "
                        f_name = re.sub(r'^\s*\d{1,2}:\d{2}\s*', '', raw_c10).strip()
                    else:
                        f_name = from_div.get_text(" ", strip=True)

                # Train line & rolling stock
                train_text = train_div.get_text(" ", strip=True) if train_div else ""
                mat_parts = []
                if train_div:
                    for mat_el in train_div.find_all(class_="vts_matinfo"):
                        mt = mat_el.get_text(" ", strip=True)
                        if mt:
                            mat_parts.append(mt)

                # Clean destination station and delay
                t_plat = ""
                t_delay = ""
                t_name = ""
                if to_div:
                    t_plat_el = to_div.find(class_="vts_platform")
                    if t_plat_el:
                        t_plat = t_plat_el.get_text(strip=True).replace("Sp", "").strip()

                    c10_to = to_div.find(class_="col-10")
                    if c10_to:
                        t_del_el = c10_to.find(class_="rp-vertr")
                        if t_del_el:
                            t_delay = t_del_el.get_text(strip=True)
                            if t_delay:
                                has_delay = True
                            t_del_el.decompose()
                        raw_c10_to = c10_to.get_text(" ", strip=True)
                        t_name = re.sub(r'^\s*\d{1,2}:\d{2}\s*', '', raw_c10_to).strip()
                    else:
                        t_name = to_div.get_text(" ", strip=True)

                legs.append({
                    "from_station": f_name,
                    "from_platform": f_plat,
                    "from_delay": f_delay,
                    "train": train_text,
                    "material": mat_parts,
                    "to_station": t_name,
                    "to_platform": t_plat,
                    "to_delay": t_delay
                })

        trips.append({
            "departure": t_dep,
            "arrival": t_arr,
            "duration": duration,
            "duration_raw": duration_raw,
            "transfers": transfers,
            "legs": legs,
            "has_delay": has_delay,
            "cancelled": is_cancelled
        })

    result = {
        "from": name_from,
        "from_code": st_from.get("code", "") if st_from else "",
        "to": name_to,
        "to_code": st_to.get("code", "") if st_to else "",
        "query_time": f"{dep_date} {dep_time}",
        "updated_at": datetime.now().strftime("%H:%M:%S"),
        "trips": trips
    }
    set_cached(cache_key, result)
    return result

# ---------------------------------------------------------
# Waybar Output Formatter
# ---------------------------------------------------------

def escape_pango(text):
    if not text:
        return ""
    text = html.unescape(str(text))
    return html.escape(text, quote=False)

def format_waybar_output():
    cfg = load_config()
    mode = cfg.get("mode", "station")

    if mode == "trip":
        return format_waybar_trip(cfg)
    else:
        return format_waybar_station(cfg)

def format_waybar_station(cfg):
    station_name = cfg.get("current_station", "Utrecht Centraal")
    max_rows = cfg.get("max_tooltip_departures", 10)
    data = fetch_departures(station_name)

    if "error" in data and not data.get("departures"):
        output = {
            "text": "󰠹 Trein: Offline",
            "tooltip": f"Fout bij ophalen van {station_name}:\n{escape_pango(data['error'])}\n\nKlik om te vernieuwen of station te kiezen.",
            "class": "error",
            "alt": "offline"
        }
        return json.dumps(output, ensure_ascii=False)

    departures = data.get("departures", [])
    st_name = data.get("station_name", station_name)
    st_code = data.get("station_code") or get_station_code(st_name)

    if not departures:
        output = {
            "text": f"󰠹 {st_code}: Geen vertrekken",
            "tooltip": f"Geen vertrektijden gevonden voor {escape_pango(st_name)}.",
            "class": "empty",
            "alt": "empty"
        }
        return json.dumps(output, ensure_ascii=False)

    # First upcoming departure for the bar
    first = departures[0]
    dep_time = first["time"]
    platform = f"Sp.{first['platform']}" if first['platform'] else ""
    dest = first["destination"]
    delay = first["delay"]
    is_cancelled = first["cancelled"]

    # Short destination for clean topbar fit
    short_dest = dest
    if len(short_dest) > 14:
        short_dest = short_dest[:12] + "…"

    css_class = "ontime"
    status_tag = ""

    if is_cancelled:
        css_class = "cancelled"
        status_tag = " [VERVALLEN]"
    elif delay:
        css_class = "delayed"
        status_tag = f" ({delay})"
        try:
            val = int(delay.replace("+", ""))
            if val >= 10:
                css_class = "critical"
        except ValueError:
            pass

    # Bar text: 󰠹 Ut: 11:09 Sp.5 ➔ Den Helder (+2)
    bar_text = f"󰠹 {st_code}: {dep_time} {platform} ➔ {short_dest}{status_tag}".strip()

    # Tooltip construction with Pango Markup
    tooltip_lines = [
        f"<b><big>󰠹 {escape_pango(st_name)} ({st_code})</big></b>  <small>Live Treinposities.nl • {data.get('updated_at')}</small>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"<b>{'Tijd':<9} {'Sp':<5} {'Bestemming':<20} {'Trein':<12} {'Status / Materieel'}</b>",
        "──────────────────────────────────────────────────────"
    ]

    for d in departures[:max_rows]:
        t_str = d["time"]
        if d["delay"]:
            t_str = f"{t_str} {d['delay']}"
        
        sp = d["platform"] or "-"
        if d.get("platform_changed"):
            sp = f"!{sp}"

        d_dest = d["destination"]
        if len(d_dest) > 18:
            d_dest = d_dest[:17] + "…"

        tr_short = d["train"].replace("NS ", "").replace("International ", "Int ")
        if len(tr_short) > 12:
            tr_short = tr_short[:11] + "…"

        # Extra info (material / position / alert)
        extra = ""
        if d["cancelled"]:
            extra = "<span color='#f7768e'><b>[Rijdt niet]</b></span>"
        elif d["alert"]:
            extra = f"<span color='#ea8000'>{escape_pango(d['alert'][:25])}</span>"
        elif d["material"]:
            extra = f"<small>{escape_pango(d['material'][0][:28])}</small>"
        elif d["countdown"]:
            extra = f"in {escape_pango(d['countdown'])}"

        # Colors
        if d["cancelled"]:
            row_line = f"<span color='#f7768e' strikethrough='true'>{t_str:<9}</span> <b>{sp:<5}</b> {escape_pango(d_dest):<20} {escape_pango(tr_short):<12} {extra}"
        elif d["delay"]:
            row_line = f"<span color='#ea8000'><b>{t_str:<9}</b></span> <b>{sp:<5}</b> {escape_pango(d_dest):<20} {escape_pango(tr_short):<12} {extra}"
        else:
            row_line = f"<span color='#9ece6a'>{t_str:<9}</span> <b>{sp:<5}</b> {escape_pango(d_dest):<20} {escape_pango(tr_short):<12} {extra}"

        tooltip_lines.append(row_line)

    tooltip_lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "<small><b>Links-klik:</b> Menu &amp; Vertrektijden   •   <b>Rechts-klik:</b> Reisplanner</small>",
        "<small><b>Midden-klik:</b> Modus wissel (Reisplanner)   •   <b>Scroll:</b> Favoriet station</small>"
    ])

    output = {
        "text": bar_text,
        "tooltip": "\n".join(tooltip_lines),
        "class": css_class,
        "alt": "station"
    }
    return json.dumps(output, ensure_ascii=False)

def format_waybar_trip(cfg):
    from_st = cfg.get("trip_from", "Utrecht Centraal")
    to_st = cfg.get("trip_to", "Amsterdam Centraal")
    max_trips = cfg.get("max_tooltip_trips", 4)

    data = fetch_trips(from_st, to_st)

    if "error" in data and not data.get("trips"):
        output = {
            "text": "󰠹 Planner: Offline",
            "tooltip": f"Fout bij ophalen reisadvies {from_st} ➔ {to_st}:\n{escape_pango(data['error'])}\n\nKlik om te plannen of te vernieuwen.",
            "class": "error",
            "alt": "offline"
        }
        return json.dumps(output, ensure_ascii=False)

    trips = data.get("trips", [])
    from_code = data.get("from_code") or get_station_code(from_st)
    to_code = data.get("to_code") or get_station_code(to_st)

    if not trips:
        output = {
            "text": f"󰠹 {from_code} ➔ {to_code}: Geen reizen",
            "tooltip": f"Geen geplande reizen gevonden tussen {escape_pango(from_st)} en {escape_pango(to_st)}.",
            "class": "empty",
            "alt": "empty"
        }
        return json.dumps(output, ensure_ascii=False)

    # First trip for Waybar bar
    first = trips[0]
    dep_time = first["departure"]
    first_plat = ""
    first_delay = ""
    if first["legs"]:
        first_plat = f"Sp.{first['legs'][0]['from_platform']}" if first['legs'][0]['from_platform'] else ""
        first_delay = first['legs'][0]['from_delay']

    css_class = "ontime"
    status_tag = ""
    if first.get("has_delay") or first_delay:
        css_class = "delayed"
        if first_delay:
            status_tag = f" ({first_delay})"

    dur = first.get("duration", "")
    dur_str = f" ({dur})" if dur else ""

    bar_text = f"󰠹 {from_code} ➔ {to_code}: {dep_time} {first_plat}{status_tag}{dur_str}".strip()

    tooltip_lines = [
        f"<b><big>🧭 Reisplanner: {escape_pango(data.get('from'))} ➔ {escape_pango(data.get('to'))}</big></b>",
        f"<small>Live Treinposities.nl • Gezocht om {data.get('updated_at')}</small>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]

    for i, t in enumerate(trips[:max_trips]):
        transfers_label = escape_pango(t["transfers"])
        dur_label = escape_pango(t["duration"])
        
        delay_marker = ""
        if t.get("has_delay"):
            delay_marker = " <span color='#ea8000'><b>[Vertraging]</b></span>"

        tooltip_lines.append(
            f"<b><span color='#9ece6a'>{t['departure']}</span> ➔ <span color='#41a6b5'>{t['arrival']}</span></b>  ({dur_label})  •  <b>{transfers_label}</b>{delay_marker}"
        )

        for leg in t["legs"]:
            plat_from = f"[Sp.{leg['from_platform']}]" if leg['from_platform'] else ""
            plat_to = f"[Sp.{leg['to_platform']}]" if leg['to_platform'] else ""
            
            f_del = f" <span color='#ea8000'>{escape_pango(leg['from_delay'])}</span>" if leg['from_delay'] else ""
            
            # Short clean train name
            train_name = leg['train'].split(' Naar ')[0].strip() if ' Naar ' in leg['train'] else leg['train']
            
            mat_str = ""
            if cfg.get("show_material", True) and leg["material"]:
                mat_str = f"  •  <small>Mat: {escape_pango(', '.join(leg['material']))}</small>"

            tooltip_lines.append(
                f"  └ <b>{plat_from}</b> {escape_pango(leg['from_station'])}{f_del} ➔ <b>{plat_to}</b> {escape_pango(leg['to_station'])}"
            )
            tooltip_lines.append(
                f"    <i><small>{escape_pango(train_name)}</small></i>{mat_str}"
            )

        if i < len(trips[:max_trips]) - 1:
            tooltip_lines.append("──────────────────────────────────────────────────────")

    tooltip_lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "<small><b>Links-klik:</b> Menu   •   <b>Rechts-klik:</b> Nieuwe reis plannen</small>",
        "<small><b>Midden-klik:</b> Wissel reisrichting (omdraaien)   •   <b>Scroll:</b> Wissel modus</small>"
    ])

    output = {
        "text": bar_text,
        "tooltip": "\n".join(tooltip_lines),
        "class": css_class,
        "alt": "trip"
    }
    return json.dumps(output, ensure_ascii=False)

# ---------------------------------------------------------
# Interactivity & Rofi Dialogs
# ---------------------------------------------------------

def signal_waybar():
    cfg = load_config()
    sig = cfg.get("waybar_signal", 8)
    try:
        subprocess.run(["pkill", f"-RTMIN+{sig}", "waybar"], check=False)
    except Exception:
        pass
    try:
        subprocess.run(["noctalia", "msg", "plugin", "lars/treinposities:treinposities", "all", "refresh"], check=False)
        subprocess.run(["noctalia", "msg", "plugin", "lars/treinposities:panel", "all", "refresh"], check=False)
    except Exception:
        pass

def notify(summary, body="", icon="dialog-information"):
    try:
        subprocess.run(["notify-send", "-a", "Treinposities", "-i", icon, summary, body], check=False)
    except Exception:
        pass

def copy_to_clipboard(text):
    try:
        proc = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE, text=True)
        proc.communicate(input=text)
        return True
    except Exception:
        return False

def action_panel_data():
    cfg = load_config()
    cur_st = cfg.get("current_station", "Utrecht Centraal")
    from_st = cfg.get("trip_from", "Utrecht Centraal")
    to_st = cfg.get("trip_to", "Amsterdam Centraal")
    
    dep_data = fetch_departures(cur_st)
    trip_data = fetch_trips(from_st, to_st)
    
    out = {
        "config": cfg,
        "current_station": cur_st,
        "departures": dep_data.get("departures", [])[:25],
        "station_info": {
            "name": dep_data.get("station_name", cur_st),
            "updated": dep_data.get("updated", "")
        },
        "trip": trip_data,
        "favorites": cfg.get("favorites", [])
    }
    print(json.dumps(out, ensure_ascii=False))

def action_search_stations(query=""):
    q = query.strip().lower()
    results = []
    for s in STATIONS:
        name = s.get("name", "")
        code = s.get("code", "")
        if not q or q in name.lower() or q == code.lower():
            results.append(s)
            if len(results) >= 30:
                break
    print(json.dumps(results, ensure_ascii=False))

def action_set_station_cli(station_name):
    cfg = load_config()
    st = find_station(station_name)
    target = st["name"] if st else station_name
    cfg["current_station"] = target
    save_config(cfg)
    signal_waybar()
    print(json.dumps({"status": "ok", "current_station": target}, ensure_ascii=False))

def action_set_trip_from_cli(station_name):
    cfg = load_config()
    st = find_station(station_name)
    target = st["name"] if st else station_name
    cfg["trip_from"] = target
    save_config(cfg)
    signal_waybar()
    print(json.dumps({"status": "ok", "trip_from": target}, ensure_ascii=False))

def action_set_trip_to_cli(station_name):
    cfg = load_config()
    st = find_station(station_name)
    target = st["name"] if st else station_name
    cfg["trip_to"] = target
    save_config(cfg)
    signal_waybar()
    print(json.dumps({"status": "ok", "trip_to": target}, ensure_ascii=False))

def action_toggle_favorite_cli(station_name):
    cfg = load_config()
    st = find_station(station_name)
    target = st["name"] if st else station_name
    favs = cfg.get("favorites", [])
    if target in favs:
        favs.remove(target)
    else:
        favs.append(target)
    cfg["favorites"] = favs
    save_config(cfg)
    signal_waybar()
    print(json.dumps({"status": "ok", "favorites": favs}, ensure_ascii=False))

def action_open_url_cli(url):
    try:
        subprocess.run(["xdg-open", url], check=False)
    except Exception:
        pass
    print(json.dumps({"status": "ok"}))

def action_menu():
    # Trigger native Noctalia shell panel instead of rofi
    try:
        res = subprocess.run(["noctalia", "msg", "panel-toggle", "lars/treinposities:panel"], check=False)
        if res.returncode == 0:
            return
    except Exception:
        pass
    notify("Treinposities", "Kon Noctalia shell panel niet openen.")

def action_show_departures(station_name=None):
    if station_name:
        action_set_station_cli(station_name)
    action_menu()

def action_change_station():
    action_menu()

def action_plan_trip():
    action_menu()

def action_swap_trip():
    cfg = load_config()
    current_from = cfg.get("trip_from", "Utrecht Centraal")
    current_to = cfg.get("trip_to", "Amsterdam Centraal")
    cfg["trip_from"] = current_to
    cfg["trip_to"] = current_from
    save_config(cfg)
    notify("Treinposities Richting Omgedraaid", f"Nieuwe route: {current_to} ➔ {current_from}")
    signal_waybar()

def action_toggle_mode():
    cfg = load_config()
    old_mode = cfg.get("mode", "station")
    new_mode = "trip" if old_mode == "station" else "station"
    cfg["mode"] = new_mode
    save_config(cfg)
    mode_name = "Reisplanner (Woon-werk)" if new_mode == "trip" else "Station Live Vertrektijden"
    notify("Treinposities Modus Gewijzigd", f"Actieve modus: {mode_name}")
    signal_waybar()

def action_favorites_menu():
    action_menu()

def action_next_favorite():
    cfg = load_config()
    favorites = cfg.get("favorites", [])
    if not favorites:
        return
    current = cfg.get("current_station", favorites[0])
    try:
        idx = favorites.index(current)
        next_idx = (idx + 1) % len(favorites)
    except ValueError:
        next_idx = 0
    next_st = favorites[next_idx]
    cfg["current_station"] = next_st
    save_config(cfg)
    notify("Treinposities Station", f"Geschakeld naar: {next_st}")
    signal_waybar()

def action_refresh():
    cfg = load_config()
    try:
        for f in os.listdir(CACHE_DIR):
            if f.endswith(".json"):
                os.remove(os.path.join(CACHE_DIR, f))
    except Exception:
        pass
    signal_waybar()
    notify("Treinposities", "Cache gewist en widget vernieuwd.")

# ---------------------------------------------------------
# Main CLI dispatcher
# ---------------------------------------------------------

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "waybar":
        print(format_waybar_output())
    elif sys.argv[1] == "menu":
        action_menu()
    elif sys.argv[1] == "departures":
        action_show_departures()
    elif sys.argv[1] == "plan":
        action_plan_trip()
    elif sys.argv[1] == "station":
        action_change_station()
    elif sys.argv[1] == "toggle-mode":
        action_toggle_mode()
    elif sys.argv[1] == "swap-trip":
        action_swap_trip()
    elif sys.argv[1] == "panel-data":
        action_panel_data()
    elif sys.argv[1] == "search-stations":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        action_search_stations(query)
    elif sys.argv[1] == "set-station":
        if len(sys.argv) > 2:
            action_set_station_cli(sys.argv[2])
    elif sys.argv[1] == "set-trip-from":
        if len(sys.argv) > 2:
            action_set_trip_from_cli(sys.argv[2])
    elif sys.argv[1] == "set-trip-to":
        if len(sys.argv) > 2:
            action_set_trip_to_cli(sys.argv[2])
    elif sys.argv[1] == "toggle-favorite":
        if len(sys.argv) > 2:
            action_toggle_favorite_cli(sys.argv[2])
    elif sys.argv[1] == "open-url":
        if len(sys.argv) > 2:
            action_open_url_cli(sys.argv[2])
    elif sys.argv[1] == "refresh":
        action_refresh()
    else:
        print(f"Onbekend commando: {sys.argv[1]}")
        print("Beschikbare commando's: waybar, panel-data, search-stations, set-station, set-trip-from, set-trip-to, toggle-mode, swap-trip, next-favorite, toggle-favorite, open-url, refresh")

if __name__ == "__main__":
    main()
