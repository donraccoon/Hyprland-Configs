-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

hl.on("hyprland.start", function()
    -- 1. Session & Environment (must run first so systemd & D-Bus have display info)
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP DISPLAY")

    -- 2. Security & System Daemons
    hl.exec_cmd("hyprpm reload -n")
    hl.exec_cmd("xhost +SI:localuser:root")

    -- 3. Clipboard Management (split into two commands so both text and images are stored)
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")

    -- 4. Shell & UI Components
    hl.exec_cmd("noctalia")
    hl.exec_cmd("qs")
    hl.exec_cmd("qs -c overview")

    -- 5. Background Services
    hl.exec_cmd("kdeconnectd")
    hl.exec_cmd("sunshine &")

    -- 6. User Applications
    hl.exec_cmd("bitwarden-desktop")
    hl.exec_cmd(terminal)
    hl.exec_cmd(browser)

    ----------------------------------------------------------------------------
    -- DISABLED / UNUSED (Handled by Noctalia or systemd, or obsolete)
    ----------------------------------------------------------------------------
    -- hl.exec_cmd("systemctl --user start hyprpolkitagent")          -- Polkit agent built into Noctalia (shell.toml)
    -- hl.exec_cmd("gnome-keyring-daemon --start --components=secrets") -- Handled by gnome-keyring-daemon.service
    -- hl.exec_cmd("swaync")                                           -- Handled by swaync.service
    -- hl.exec_cmd("hypridle")                                         -- Idle & locking handled by Noctalia (idle.toml)
    -- hl.exec_cmd("hyprpaper")                                        -- Wallpapers handled by Noctalia (wallpaper.toml)
    -- hl.exec_cmd("nm-applet --indicator")                            -- Network widget built into Noctalia
    -- hl.exec_cmd("nm-tray")                                          -- Network widget built into Noctalia
    -- hl.exec_cmd("blueman-applet")                                   -- Bluetooth widget built into Noctalia
    -- hl.exec_cmd("/usr/lib/xdg-desktop-portal -v &")                  -- Activated automatically via systemd / D-Bus
    -- hl.exec_cmd("/home/lars/batteryEmpty.sh &")                     -- Script not found (battery handled by Noctalia)
end)
