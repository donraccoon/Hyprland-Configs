#!/usr/bin/env python3
"""
Waybar widget script for omdrop (AirDrop on Linux via omdrop-owl & omdrop CLI).
Handles status polling, Pango-formatted tooltips, instant signals, Rofi control menu,
and AUTOMATIC Wi-Fi channel swapping (swaps to compatible channel when omdrop is used,
and auto-restores to the fastest channel when omdrop is off).
"""

import sys
import os
import json
import time
import shutil
import subprocess

# Ensure ~/.local/bin is in PATH for finding omdrop
LOCAL_BIN = os.path.expanduser("~/.local/bin")
if LOCAL_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{LOCAL_BIN}:{os.environ.get('PATH', '')}"

OMDROP_BIN = shutil.which("omdrop") or os.path.expanduser("~/.local/share/omdrop/bin/omdrop")
PROBE_BIN = "/usr/lib/omdrop/omdrop-discoverable"
WAYBAR_SIGNAL = 9

SWAP_MARKER = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "omdrop_wifi_swapped")

ICON_DROPOFF = "󰛴"  # AirDrop / File drop glyph
ICON_WARN = "󰀦"
ICON_CLOCK = "󱑎"


def signal_waybar():
    try:
        subprocess.run(["pkill", f"-RTMIN+{WAYBAR_SIGNAL}", "waybar"], stderr=subprocess.DEVNULL)
    except Exception:
        pass
    try:
        subprocess.run(["noctalia", "msg", "plugin", "lars/omdrop:omdrop", "all", "refresh"], stderr=subprocess.DEVNULL)
    except Exception:
        pass


def notify(title, message, urgency="normal"):
    try:
        subprocess.run(
            ["notify-send", "-a", "omdrop", "-u", urgency, title, message],
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass


def get_status():
    if not os.path.exists(OMDROP_BIN):
        return None
    try:
        proc = subprocess.run([OMDROP_BIN, "status", "--json"], capture_output=True, text=True, timeout=3)
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip())
    except Exception:
        pass
    return None


def get_probe():
    if not os.path.exists(PROBE_BIN):
        return None
    try:
        proc = subprocess.run([PROBE_BIN, "probe", "--json"], capture_output=True, text=True, timeout=2)
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip())
    except Exception:
        pass
    return None


def get_current_connection():
    try:
        res = subprocess.run(["nmcli", "-t", "-f", "NAME,DEVICE,TYPE", "connection", "show", "--active"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            parts = line.strip().split(":")
            if len(parts) >= 3 and parts[2] == "802-11-wireless":
                return parts[0], parts[1]
    except Exception:
        pass
    return None, None


def get_current_ssid():
    try:
        res = subprocess.run(["iw", "dev"], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if "ssid" in line:
                return line.strip().split()[1]
    except Exception:
        pass
    return None


def find_airdrop_bssids():
    ssid = get_current_ssid()
    if not ssid:
        return []
    try:
        res = subprocess.run(["nmcli", "-t", "-f", "BSSID,SSID,CHAN,FREQ,SIGNAL", "dev", "wifi", "list"], capture_output=True, text=True)
        matching = []
        for line in res.stdout.splitlines():
            parts = line.strip().split(":")
            if len(parts) >= 10:
                bssid = ":".join(parts[:6]).replace("\\", "")
                net_ssid = parts[6]
                chan = parts[7]
                freq = parts[8]
                signal = parts[9]
                if net_ssid == ssid and chan in ("6", "44", "149"):
                    matching.append({"bssid": bssid, "chan": chan, "freq": freq, "signal": signal})
        return matching
    except Exception:
        return []


def auto_prepare_wifi_for_omdrop():
    """If current Wi-Fi is on an incompatible channel, auto-swap to a compatible BSSID on the same SSID."""
    probe = get_probe()
    if not probe or not probe.get("missing"):
        return True  # already compatible

    radio_issue = any(m.get("id") == "radio" for m in probe.get("missing", []))
    if not radio_issue:
        return True

    alt_bssids = find_airdrop_bssids()
    if not alt_bssids:
        return False

    def score(b):
        sig = int(b.get("signal", 0))
        # Prefer 5 GHz (channels 149 / 44) over 2.4 GHz if available
        if b.get("chan") in ("149", "44"):
            sig += 15
        return sig

    best = max(alt_bssids, key=score)
    con_name, _ = get_current_connection()
    if con_name:
        notify("omdrop Wi-Fi", f"Auto-switching Wi-Fi to Channel {best['chan']} for AirDrop...")
        subprocess.run(["nmcli", "connection", "modify", con_name, "802-11-wireless.bssid", best["bssid"]], capture_output=True)
        res = subprocess.run(["nmcli", "connection", "up", con_name], capture_output=True, text=True)
        if res.returncode == 0:
            try:
                with open(SWAP_MARKER, "w") as f:
                    f.write(con_name)
            except Exception:
                pass
            time.sleep(1.5)  # wait for connection to settle
            return True
    return False


def auto_restore_wifi_if_needed():
    """If Wi-Fi was temporarily swapped for AirDrop, restore it back to Auto (fastest channel)."""
    if os.path.exists(SWAP_MARKER):
        con_name = None
        try:
            with open(SWAP_MARKER, "r") as f:
                con_name = f.read().strip()
            os.remove(SWAP_MARKER)
        except Exception:
            con_name = None
            if os.path.exists(SWAP_MARKER):
                try:
                    os.remove(SWAP_MARKER)
                except Exception:
                    pass

        if not con_name:
            con_name, _ = get_current_connection()
        if con_name:
            notify("omdrop Wi-Fi", f"AirDrop finished: restoring {con_name} to fastest channel...")
            subprocess.run(["nmcli", "connection", "modify", con_name, "802-11-wireless.bssid", ""], capture_output=True)
            subprocess.run(["nmcli", "connection", "up", con_name], capture_output=True)


def format_remaining(seconds):
    if seconds is None:
        return ""
    try:
        sec = int(seconds)
        if sec < 60:
            return f"{sec}s"
        mins = sec // 60
        rem_sec = sec % 60
        if rem_sec > 0:
            return f"{mins}m{rem_sec:02d}s"
        return f"{mins}m"
    except Exception:
        return ""


def rofi_dmenu(prompt, items, message=None):
    cmd = ["rofi", "-dmenu", "-i", "-p", prompt]
    if message:
        cmd.extend(["-mesg", message])
    try:
        proc = subprocess.run(cmd, input="\n".join(items), text=True, capture_output=True)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return None


def action_status():
    status = get_status()
    probe = get_probe()

    if status is None:
        output = {
            "text": f"{ICON_DROPOFF} !",
            "alt": "error",
            "tooltip": "<b>omdrop</b>: CLI not found or failed to execute.<br/>Run <code>omdrop setup</code> to configure.",
            "class": "error"
        }
        print(json.dumps(output))
        return

    receiving = status.get("receiving", False)
    visible = status.get("visible", False)
    mode = status.get("mode", "off")
    remaining = status.get("remaining")
    name = status.get("name", "Unknown")
    download_dir = status.get("dir", "~/Downloads")
    visibility = status.get("visibility", "everyone")
    reason = status.get("reason") or ""

    # If omdrop is no longer receiving but we had swapped Wi-Fi, auto-restore now!
    if not receiving and os.path.exists(SWAP_MARKER):
        auto_restore_wifi_if_needed()

    # Check probe for any hardware/radio warnings
    probe_warning = None
    if probe and probe.get("missing"):
        for m in probe.get("missing", []):
            if m.get("id") == "radio":
                probe_warning = m.get("say")
                break
        if not probe_warning and len(probe.get("missing")) > 0:
            probe_warning = probe["missing"][0].get("say")

    classes = []
    if receiving:
        classes.append("receiving")
        classes.append("active")
        if visible:
            classes.append("visible")
        else:
            classes.append("settling")

        rem_str = format_remaining(remaining)
        if mode == "forever":
            text = f"{ICON_DROPOFF} ∞"
        elif mode == "once":
            text = f"{ICON_DROPOFF} 1x"
        elif rem_str:
            text = f"{ICON_DROPOFF} {rem_str}"
        else:
            text = f"{ICON_DROPOFF} ON"
    else:
        classes.append("off")
        if probe_warning:
            classes.append("warning")
        text = ICON_DROPOFF

    # Build Pango markup tooltip
    tooltip_lines = [
        "<b><span size='large'>AirDrop (omdrop)</span></b>",
        "───────────────────────────────"
    ]

    if receiving:
        status_line = "<span color='#a6e3a1'>● Active (Receiving)</span>" if visible else "<span color='#f9e2af'>◐ Starting / Waking radio...</span>"
        tooltip_lines.append(f"<b>Status:</b> {status_line}")
        if mode == "forever":
            tooltip_lines.append("<b>Window:</b> Until turned off")
        elif mode == "once":
            tooltip_lines.append("<b>Window:</b> Single file transfer")
        elif remaining is not None:
            tooltip_lines.append(f"<b>Time Left:</b> {format_remaining(remaining)}")
    else:
        tooltip_lines.append("<b>Status:</b> <span color='#6c7086'>○ Off (Standby)</span>")

    tooltip_lines.append(f"<b>Device Name:</b> {name}")
    tooltip_lines.append(f"<b>Visibility:</b> {visibility.capitalize()}")
    tooltip_lines.append(f"<b>Save To:</b> {download_dir}")

    if probe_warning:
        tooltip_lines.append("───────────────────────────────")
        tooltip_lines.append(f"<b><span color='#fab387'>⚠️ Wi-Fi Channel Notice:</span></b>\n<i>Auto-swaps to Ch 149/6 when AirDrop starts</i>")

    tooltip_lines.append("───────────────────────────────")
    tooltip_lines.append("🖱️ <b>Left-Click:</b> Toggle On / Off (Auto Wi-Fi Swap)")
    tooltip_lines.append("🖱️ <b>Right-Click:</b> Menu & Duration")
    tooltip_lines.append("🖱️ <b>Middle-Click:</b> Send File(s)")

    output = {
        "text": text,
        "alt": "receiving" if receiving else "off",
        "tooltip": "\n".join(tooltip_lines),
        "class": " ".join(classes)
    }
    print(json.dumps(output))


def action_toggle():
    status = get_status()
    if status and status.get("receiving", False):
        subprocess.run([OMDROP_BIN, "off"], capture_output=True, text=True)
        auto_restore_wifi_if_needed()
        notify("omdrop", "AirDrop turned off. Wi-Fi restored to fastest channel.")
    else:
        # Auto-swap Wi-Fi if current channel is incompatible
        auto_prepare_wifi_for_omdrop()
        proc = subprocess.run([OMDROP_BIN, "on", "10m"], capture_output=True, text=True)
        if proc.returncode != 0:
            err = proc.stderr.strip() or proc.stdout.strip() or "Could not start omdrop"
            notify("omdrop Error", err, urgency="critical")
        else:
            notify("omdrop", "AirDrop receiving on (10 minutes).")
    signal_waybar()


def action_on(duration="10m"):
    auto_prepare_wifi_for_omdrop()
    proc = subprocess.run([OMDROP_BIN, "on", duration], capture_output=True, text=True)
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or f"Could not start omdrop on {duration}"
        notify("omdrop Error", err, urgency="critical")
    else:
        notify("omdrop", f"AirDrop receiving on ({duration}).")
    signal_waybar()


def action_off():
    subprocess.run([OMDROP_BIN, "off"], capture_output=True, text=True)
    auto_restore_wifi_if_needed()
    notify("omdrop", "AirDrop turned off. Wi-Fi restored to fastest channel.")
    signal_waybar()


def action_send():
    auto_prepare_wifi_for_omdrop()
    try:
        subprocess.Popen([OMDROP_BIN, "send", "--pick"])
    except Exception as e:
        notify("omdrop Send Error", str(e), urgency="critical")


def action_probe():
    probe = get_probe()
    if not probe:
        notify("omdrop Diagnostic", "Probe binary not found.")
        return

    missing = probe.get("missing", [])
    if not missing:
        notify("omdrop Diagnostic", "✅ Radio backend (owl) is healthy and ready!")
    else:
        reasons = "\n".join([f"• {m.get('say')}" for m in missing])
        notify("omdrop Diagnostic", f"⚠️ Issues found:\n{reasons}", urgency="critical")


def action_peers():
    notify("omdrop Peers", "Scanning for nearby Apple devices...")
    try:
        proc = subprocess.run([OMDROP_BIN, "peers", "--json"], capture_output=True, text=True, timeout=15)
        if proc.returncode == 0 and proc.stdout.strip():
            peers = json.loads(proc.stdout.strip())
            if not peers:
                notify("omdrop Peers", "No Apple devices discovered nearby.")
            else:
                lines = [f"• {p.get('name', 'Unknown')} ({p.get('model', 'Apple device')})" for p in peers]
                notify("omdrop Nearby Devices", "\n".join(lines))
        else:
            notify("omdrop Peers", "No devices responded or scanning timed out.")
    except Exception as e:
        notify("omdrop Peers Error", str(e), urgency="critical")


def action_switch_wifi(bssid, chan):
    con_name, _ = get_current_connection()
    if not con_name:
        notify("omdrop Wi-Fi", "No active Wi-Fi connection found.", urgency="critical")
        return
    notify("omdrop Wi-Fi", f"Switching {con_name} to Channel {chan} ({bssid})...")
    subprocess.run(["nmcli", "connection", "modify", con_name, "802-11-wireless.bssid", bssid], capture_output=True)
    res = subprocess.run(["nmcli", "connection", "up", con_name], capture_output=True, text=True)
    if res.returncode == 0:
        notify("omdrop Wi-Fi", f"Connected to Channel {chan}! AirDrop is ready.")
    else:
        notify("omdrop Wi-Fi Error", res.stderr.strip() or "Failed to connect", urgency="critical")
    signal_waybar()


def action_reset_wifi():
    con_name, _ = get_current_connection()
    if not con_name:
        return
    notify("omdrop Wi-Fi", f"Restoring {con_name} to fastest channel (Auto)...")
    subprocess.run(["nmcli", "connection", "modify", con_name, "802-11-wireless.bssid", ""], capture_output=True)
    subprocess.run(["nmcli", "connection", "up", con_name], capture_output=True)
    notify("omdrop Wi-Fi", "Wi-Fi channel lock removed (automatic roaming enabled).")
    signal_waybar()


def action_menu():
    status = get_status()
    probe = get_probe()

    receiving = status.get("receiving", False) if status else False
    visibility = status.get("visibility", "everyone") if status else "everyone"
    dev_name = status.get("name", "Device") if status else "Device"
    d_dir = status.get("dir", "~/Downloads") if status else "~/Downloads"

    toggle_label = "󰐥  Turn Off AirDrop (Restore Fastest Wi-Fi)" if receiving else "󰐥  Turn On AirDrop (Auto-Swap Channel, 10m)"
    next_vis = "Contacts Only" if visibility == "everyone" else "Everyone"

    menu_items = [
        toggle_label,
        "󱑎  Turn On: 5 minutes",
        "󱑎  Turn On: 10 minutes",
        "󱑎  Turn On: 15 minutes",
        "󱑎  Turn On: 30 minutes",
        "󱑎  Turn On: 1 hour",
        "󱑎  Turn On: Until turned off (forever)",
        "󱑎  Turn On: Single file transfer (once)",
        "󰒓  Send File(s) to nearby Apple device...",
        f"󰀵  Switch Visibility to {next_vis}",
        "󰐷  Scan for Nearby Apple Devices",
        "󰀦  Wi-Fi Channel & Radio Diagnostics",
        "󰖩  Restore Wi-Fi to Fastest Channel (Auto Roam)",
    ]

    alt_bssids = find_airdrop_bssids()
    channel_actions = {}
    if alt_bssids:
        for b in alt_bssids:
            label = f"󰖩  Manually Switch to Channel {b['chan']} ({b['freq']}, signal {b['signal']}%)"
            menu_items.append(label)
            channel_actions[label] = (b["bssid"], b["chan"])

    menu_items.extend([
        f"󰉋  Open Downloads Folder ({d_dir})",
        f"󰒓  Rename Device (currently '{dev_name}')"
    ])

    header_msg = f"Status: {'Active' if receiving else 'Off'} | Name: {dev_name} | Visibility: {visibility.capitalize()}"

    choice = rofi_dmenu("omdrop AirDrop", menu_items, message=header_msg)
    if not choice:
        return

    if "Turn Off AirDrop" in choice:
        action_off()
    elif "Turn On AirDrop" in choice or "10 minutes" in choice:
        action_on("10m")
    elif "5 minutes" in choice:
        action_on("5m")
    elif "15 minutes" in choice:
        action_on("15m")
    elif "30 minutes" in choice:
        action_on("30m")
    elif "1 hour" in choice:
        action_on("1h")
    elif "forever" in choice:
        action_on("forever")
    elif "Single file" in choice:
        action_on("once")
    elif "Send File" in choice:
        action_send()
    elif "Switch Visibility" in choice:
        new_mode = "contacts" if visibility == "everyone" else "everyone"
        subprocess.run([OMDROP_BIN, "visibility", new_mode], capture_output=True)
        notify("omdrop", f"Visibility set to {new_mode.capitalize()}.")
        signal_waybar()
    elif "Scan for Nearby" in choice:
        action_peers()
    elif "Radio Diagnostics" in choice:
        action_probe()
    elif "Restore Wi-Fi to Fastest Channel" in choice:
        action_reset_wifi()
    elif choice in channel_actions:
        bssid, ch = channel_actions[choice]
        action_switch_wifi(bssid, ch)
    elif "Open Downloads Folder" in choice:
        folder = os.path.expanduser(d_dir)
        subprocess.Popen(["xdg-open", folder])
    elif "Rename Device" in choice:
        new_name = rofi_dmenu("New Device Name", [dev_name], message="Enter the name nearby Apple devices will see:")
        if new_name and new_name.strip():
            subprocess.run([OMDROP_BIN, "name", new_name.strip()], capture_output=True)
            notify("omdrop", f"Device name changed to: {new_name.strip()}")
            signal_waybar()


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "status":
        action_status()
    elif sys.argv[1] == "toggle":
        action_toggle()
    elif sys.argv[1] == "menu":
        action_menu()
    elif sys.argv[1] == "send":
        action_send()
    elif sys.argv[1] == "probe":
        action_probe()
    elif sys.argv[1] == "peers":
        action_peers()
    elif sys.argv[1] == "switch":
        if len(sys.argv) >= 4:
            action_switch_wifi(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "reset-wifi":
        action_reset_wifi()
    elif sys.argv[1] == "off":
        action_off()
    elif sys.argv[1] == "on":
        dur = sys.argv[2] if len(sys.argv) > 2 else "10m"
        action_on(dur)
    else:
        print(f"Unknown command: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
