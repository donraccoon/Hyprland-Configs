-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--
 hl.on("hyprland.start", function ()
  hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP DISPLAY && dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP DISPLAY")
   hl.exec_cmd(terminal)
   hl.exec_cmd("nm-applet --indicator")
   hl.exec_cmd("nm-tray")
   hl.exec_cmd("swaync")
   hl.exec_cmd("wl-paste --type text --watch cliphist store && wl-paste --type image --watch cliphist store")
   hl.exec_cmd("hypridle")
   hl.exec_cmd("waybar")
   hl.exec_cmd("qs")
   hl.exec_cmd("qs -c overview")
   hl.exec_cmd("hyprpaper")
   hl.exec_cmd("hyprctl hyprpaper wallpaper 'eDP-1, /home/lars/Pictures/wallpapers/kitty_dark.png, cover'")
   hl.exec_cmd("kdeconnectd")
   hl.exec_cmd("xhost + local")
   hl.exec_cmd(browser)
   hl.exec_cmd(mail)
   hl.exec_cmd(music)
   hl.exec_cmd("discord")
 end)

