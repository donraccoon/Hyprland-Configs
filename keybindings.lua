hl.bind("SUPER + Return", hl.dsp.exec_cmd("kitty"))
hl.bind("SUPER + Q", hl.dsp.window.close())
--hl.bind("SUPER + SHIFT + P", hl.dsp.exec_cmd("/bin/true")) -- TODO: change this
hl.bind("SUPER + B", hl.dsp.exec_cmd("librewolf"))
hl.bind("SUPER + E", hl.dsp.exec_cmd("thunar"))
hl.bind("SUPER + Space", hl.dsp.window.float({ action = "toggle" }))
hl.bind("SUPER + D", hl.dsp.exec_cmd("rofi -show drun"))
hl.bind("SUPER + P", hl.dsp.window.pseudo())
hl.bind("SUPER + F", hl.dsp.layout("togglesplit"))
hl.bind("SUPER + L", hl.dsp.exec_cmd("hyprlock --immediate-render"))
hl.bind("SUPER + S", hl.dsp.exec_cmd("hyprshot -m output -z"))
hl.bind("SUPER + ALT + S", hl.dsp.exec_cmd("hyprshot -m window -z"))

hl.bind("Print", hl.dsp.exec_cmd("hyprshot -m output -z"))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd("hyprshot -m region -z"))
hl.bind("SUPER + H", hl.dsp.exec_cmd("thunderbird"))
hl.bind("SUPER + ALT + V", hl.dsp.exec_cmd("/home/lars/.config/hypr/ClipManager.sh"))
hl.bind("SUPER + Y", hl.dsp.exec_cmd("hyprctl dispatch workspace 1"))
--bindd = $mainMod ALT, V, clipboard manager, exec, $scriptsDir/ClipManager.sh

hl.bind("SUPER + M",
    hl.dsp.exec_cmd("command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown || hyprctl dispatch 'hl.dsp.exit()'"))

hl.bind("SUPER + left", hl.dsp.focus({ direction = "left" }))
hl.bind("SUPER + right", hl.dsp.focus({ direction = "right" }))
hl.bind("SUPER + up", hl.dsp.focus({ direction = "up" }))
hl.bind("SUPER + down", hl.dsp.focus({ direction = "down" }))

for i = 0, 9 do
    -- If i is 0, set target workspace to 10, otherwise use i
    local workspace_num = (i == 0) and 10 or i
    local key = tostring(i)

    hl.bind("SUPER + " .. key, hl.dsp.focus({ workspace = workspace_num }))
    hl.bind("SUPER + SHIFT + " .. key, hl.dsp.window.move({ workspace = workspace_num }))
end
--hl.bind("SUPER + +", hl.dsp.focus({ relative = 1 }))
--hl.bind("SUPER + -", hl.dsp.focus({ relative = -1 }))

-- Special workspace is not needed:

-- hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special("magic"))
-- hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))


hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })

hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"),
    { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
    { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
    { locked = true, repeating = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),
    { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -d amdgpu_bl1 set 5%+"),
    { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -d amdgpu_bl1 set 5%-"),
    { locked = true, repeating = true })

hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

--hl.bind("switch:on:Lid Switch", hl.dsp.exec_cmd("hyprlock --immediate-render"), { locked = true })

hl.bind("SUPER + SHIFT + code:201", hl.dsp.exec_cmd("code"))                                                        -- Run VScode on pressing Copilot key
hl.bind("SUPER + SHIFT + M", hl.dsp.exec_cmd("/home/lars/Documents/MathWorks/bin/matlab -licmode onlinelicensing")) -- Run VScode on pressing Copilot key
hl.bind("XF86Calculator", hl.dsp.exec_cmd("qalculate-gtk"))
hl.bind("XF86Display", hl.dsp.exec_cmd("hyprctl reload"))
hl.bind("XF86Launch8", hl.dsp.exec_cmd("kate"))


hl.bind("SUPER + W",
    hl.dsp.exec_cmd(
    "mpvpaper -o \"no-audio --loop-playlist shuffle\" ALL 'https://www.youtube.com/watch?v=alEeyCEaGSE&list=PLhR6gO7SaCn_PyU_J8tga4OQwKiigoykn'"))
