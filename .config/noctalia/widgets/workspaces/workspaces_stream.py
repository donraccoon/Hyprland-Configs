#!/usr/bin/env python3
"""
Hyprland Workspaces & Window Icons Streamer for Noctalia.
Reads Waybar window-rewrite rules and streams live workspace states
with matched Nerd Font icons over Hyprland's socket2.
"""

import sys
import os
import json
import re
import socket
import select
import time
import subprocess

WAYBAR_MODULES = "/home/lars/.config/waybar/modules.jsonc"
DEFAULT_ICON = " "

# Fallback window rewrite rules in case config file cannot be read
DEFAULT_RULES = [
    ("title", re.compile(r".*amazon.*", re.I), " "),
    ("title", re.compile(r".*reddit.*", re.I), " "),
    ("class", re.compile(r"firefox|org\.mozilla\.firefox|librewolf|floorp|mercury-browser|[Cc]achy-browser"), " "),
    ("class", re.compile(r"zen"), "󰰷 "),
    ("class", re.compile(r"waterfox|waterfox-bin"), " "),
    ("class", re.compile(r"microsoft-edge"), " "),
    ("class", re.compile(r"Chromium|Thorium|[Cc]hrome"), " "),
    ("class", re.compile(r"brave-browser"), "🦁 "),
    ("class", re.compile(r"tor browser"), " "),
    ("class", re.compile(r"firefox-developer-edition"), "🦊 "),
    ("class", re.compile(r"kitty|konsole|[Aa]lacritty"), " "),
    ("class", re.compile(r"kitty-dropterm"), " "),
    ("class", re.compile(r"com\.mitchellh\.ghostty"), " "),
    ("class", re.compile(r"org\.wezfurlong\.wezterm"), " "),
    ("class", re.compile(r"Warp|warp|dev\.warp\.Warp|warp-terminal"), "󰰭 "),
    ("class", re.compile(r"[Tt]hunderbird|[Tt]hunderbird-esr"), " "),
    ("class", re.compile(r"eu\.betterbird\.Betterbird"), " "),
    ("title", re.compile(r".*gmail.*", re.I), "󰊫 "),
    ("class", re.compile(r"[Tt]elegram-desktop|org\.telegram\.desktop|io\.github\.tdesktop_x64\.TDesktop"), " "),
    ("class", re.compile(r"discord|discord-canary|[Ww]ebcord|[Vv]esktop|com\.discordapp\.Discord|dev\.vencord\.Vesktop"), " "),
    ("class", re.compile(r"[Ss]ignal|signal-desktop|org\.signal\.Signal"), "󰍩 "),
    ("title", re.compile(r".*Signal.*"), "󰍩 "),
    ("title", re.compile(r".*whatsapp.*", re.I), " "),
    ("title", re.compile(r".*zapzap.*", re.I), " "),
    ("title", re.compile(r".*messenger.*", re.I), " "),
    ("title", re.compile(r".*facebook.*", re.I), " "),
    ("title", re.compile(r".*Discord.*"), " "),
    ("title", re.compile(r".*ChatGPT.*", re.I), "󰚩 "),
    ("title", re.compile(r".*deepseek.*", re.I), "󰚩 "),
    ("title", re.compile(r".*qwen.*", re.I), "󰚩 "),
    ("class", re.compile(r"subl"), "󰅳 "),
    ("class", re.compile(r"slack"), " "),
    ("class", re.compile(r"mpv"), " "),
    ("class", re.compile(r"celluloid|Zoom"), " "),
    ("class", re.compile(r"Cider"), "󰎆 "),
    ("title", re.compile(r".*Picture-in-Picture.*"), " "),
    ("title", re.compile(r".*youtube.*", re.I), " "),
    ("class", re.compile(r"vlc"), "󰕼 "),
    ("class", re.compile(r"[Kk]denlive|org\.kde\.kdenlive"), "🎬 "),
    ("title", re.compile(r".*Kdenlive.*"), "🎬 "),
    ("title", re.compile(r".*cmus.*"), " "),
    ("class", re.compile(r"[Ss]potify"), " "),
    ("class", re.compile(r"Plex"), "󰚺 "),
    ("class", re.compile(r"virt-manager|\.virt-manager-wrapped|remote-viewer|virt-viewer"), " "),
    ("class", re.compile(r"virtualbox manager"), "💽 "),
    ("title", re.compile(r"virtualbox", re.I), "💽 "),
    ("class", re.compile(r"remmina|org\.remmina\.Remmina"), "🖥️ "),
    ("class", re.compile(r"VSCode|code|code-url-handler|code-oss|codium|codium-url-handler|VSCodium|com\.microsoft\.VSCode"), "󰨞 "),
    ("class", re.compile(r"dev\.zed\.Zed"), "󰵁"),
    ("class", re.compile(r"codeblocks"), "󰅩 "),
    ("title", re.compile(r".*github.*", re.I), " "),
    ("class", re.compile(r"mousepad"), " "),
    ("class", re.compile(r"libreoffice-writer"), " "),
    ("class", re.compile(r"libreoffice-startcenter"), "󰏆 "),
    ("class", re.compile(r"libreoffice-calc"), " "),
    ("title", re.compile(r".*nvim.*|.*vim.*"), " "),
    ("title", re.compile(r".*figma.*", re.I), " "),
    ("title", re.compile(r".*jira.*", re.I), " "),
    ("class", re.compile(r"jetbrains-idea"), " "),
    ("class", re.compile(r"obs|com\.obsproject\.Studio"), " "),
    ("class", re.compile(r"polkit-gnome-authentication-agent-1"), "󰒃 "),
    ("class", re.compile(r"nwg-look"), " "),
    ("class", re.compile(r"nwg-displays"), " "),
    ("class", re.compile(r"[Pp]avucontrol|org\.pulseaudio\.pavucontrol"), "󱡫 "),
    ("class", re.compile(r"steam"), " "),
    ("class", re.compile(r"thunar|nemo"), "󰝰 "),
    ("class", re.compile(r"Gparted"), ""),
    ("class", re.compile(r"gimp"), " "),
    ("class", re.compile(r"emulator"), "📱 "),
    ("class", re.compile(r"android-studio"), " "),
    ("class", re.compile(r"org\.pipewire\.Helvum"), "󰓃"),
    ("class", re.compile(r"localsend"), ""),
    ("class", re.compile(r"PrusaSlicer|UltiMaker-Cura|OrcaSlicer"), "󰹛"),
    ("class", re.compile(r"io\.github\.kolunmi\.Bazaar"), " "),
    ("title", re.compile(r"^Bazaar$"), " "),
    ("class", re.compile(r"com\.gabm\.satty"), " "),
    ("title", re.compile(r"^satty$"), " "),
    ("class", re.compile(r"[Bb]ox[Bb]uddy|io\.github\.dvlv\.boxbuddy"), " "),
    ("title", re.compile(r".*BoxBuddy.*"), " "),
]

def load_rules():
    if not os.path.exists(WAYBAR_MODULES):
        return DEFAULT_RULES, DEFAULT_ICON
    try:
        with open(WAYBAR_MODULES, "r", encoding="utf-8") as f:
            content = f.read()
        def_icon = DEFAULT_ICON
        m_def = re.search(r'"window-rewrite-default":\s*"([^"]+)"', content)
        if m_def:
            def_icon = m_def.group(1)

        m_sec = re.search(r'"window-rewrite":\s*\{([^}]+)\}', content)
        if not m_sec:
            return DEFAULT_RULES, def_icon

        rules = []
        for line in m_sec.group(1).splitlines():
            line = line.strip()
            m = re.match(r'"(class|title)<([^>]+)>":\s*"([^"]+)"', line)
            if m:
                target, pattern, icon = m.group(1), m.group(2), m.group(3)
                try:
                    compiled = re.compile(pattern)
                    rules.append((target, compiled, icon))
                except re.error:
                    pass
        return rules if rules else DEFAULT_RULES, def_icon
    except Exception:
        return DEFAULT_RULES, DEFAULT_ICON

RULES, REWRITE_DEFAULT = load_rules()

def get_window_icon(cls, title):
    cls = cls or ""
    title = title or ""
    for target, pattern, icon in RULES:
        if target == "class" and pattern.search(cls):
            return icon
        elif target == "title" and pattern.search(title):
            return icon
    return REWRITE_DEFAULT

def get_hyprland_state():
    try:
        ws_out = subprocess.check_output(["hyprctl", "-j", "workspaces"], timeout=2)
        workspaces = json.loads(ws_out.decode("utf-8"))
    except Exception:
        workspaces = []

    try:
        act_out = subprocess.check_output(["hyprctl", "-j", "activeworkspace"], timeout=2)
        active_ws = json.loads(act_out.decode("utf-8")).get("id", 1)
    except Exception:
        active_ws = 1

    try:
        cli_out = subprocess.check_output(["hyprctl", "-j", "clients"], timeout=2)
        clients = json.loads(cli_out.decode("utf-8"))
    except Exception:
        clients = []

    # Map clients to workspaces
    ws_clients = {}
    urgent_ws = set()
    for c in clients:
        ws_id = c.get("workspace", {}).get("id")
        if ws_id is None or ws_id <= 0:
            continue
        ws_clients.setdefault(ws_id, []).append(c)
        if c.get("urgent", False):
            urgent_ws.add(ws_id)

    # Collect workspace IDs: persistent 1..5, plus any workspace with windows or active
    all_ws_ids = set(range(1, 6))
    for ws in workspaces:
        wid = ws.get("id")
        if wid and wid > 0:
            all_ws_ids.add(wid)
    for wid in ws_clients.keys():
        if wid > 0:
            all_ws_ids.add(wid)
    if active_ws > 0:
        all_ws_ids.add(active_ws)

    result = []
    for wid in sorted(all_ws_ids):
        w_clients = ws_clients.get(wid, [])
        icons = []
        for c in w_clients:
            icon = get_window_icon(c.get("class", ""), c.get("title", ""))
            icons.append(icon.strip())

        result.append({
            "id": wid,
            "focused": (wid == active_ws),
            "occupied": (len(w_clients) > 0),
            "urgent": (wid in urgent_ws),
            "icons": icons,
            "icons_str": " ".join(icons),
        })

    return result

def main():
    if "--once" in sys.argv:
        print(json.dumps(get_hyprland_state()))
        return

    # Print initial snapshot
    sys.stdout.write(json.dumps(get_hyprland_state()) + "\n")
    sys.stdout.flush()

    runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE", "")
    sock_path = f"{runtime}/hypr/{sig}/.socket2.sock"

    while True:
        try:
            if not os.path.exists(sock_path):
                time.sleep(2)
                continue

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(sock_path)
            buf = ""

            while True:
                r, _, _ = select.select([sock], [], [], 30.0)
                if not r:
                    # Periodic heartbeat / refresh
                    sys.stdout.write(json.dumps(get_hyprland_state()) + "\n")
                    sys.stdout.flush()
                    continue

                chunk = sock.recv(4096)
                if not chunk:
                    break

                buf += chunk.decode("utf-8", errors="replace")
                lines = buf.split("\n")
                buf = lines[-1]

                needs_update = False
                for line in lines[:-1]:
                    if ">>" in line:
                        ev = line.split(">>")[0]
                        if ev in (
                            "workspace", "workspacev2", "focusedmon", "focusedmonv2",
                            "createworkspace", "createworkspacev2", "destroyworkspace", "destroyworkspacev2",
                            "moveworkspace", "moveworkspacev2", "openwindow", "closewindow", "movewindow", "movewindowv2",
                            "urgent"
                        ):
                            needs_update = True

                if needs_update:
                    time.sleep(0.015)  # debounce bursts
                    sys.stdout.write(json.dumps(get_hyprland_state()) + "\n")
                    sys.stdout.flush()

        except Exception:
            time.sleep(1)
        finally:
            try:
                sock.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
