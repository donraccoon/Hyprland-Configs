-------------------------
-- START VAXRY CONFIGS --
-------------------------

hl.config({
    general = {
        gaps_in          = 3,
        gaps_out         = 8,

        border_size      = 2,

        col              = {
            active_border   = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
            inactive_border = "rgba(595959aa)",
        },

        resize_on_border = true,

        allow_tearing    = false,

        layout           = "dwindle",
        
    },

    decoration = {
        rounding         = 10,
        rounding_power   = 2,

        -- Change transparency of focused and unfocused windows
        active_opacity   = 1.0,
        inactive_opacity = 1.0,

        shadow           = {
            enabled      = true,
            range        = 4,
            render_power = 3,
            color        = 0xee1a1a1a,
        },

        blur             = {
            enabled  = true,
            size     = 3,
            passes   = 1,
            vibrancy = 0.1696,
        },
        wobble = {
            enabled = true,
            mass = 1.0,         -- Spring mass for the deformation
            stiffness = 200.0,  -- Higher values create a faster wobble
            damping = 12.0,     -- Controls bounce dissipation (higher = stops sooner)
            intensity = 0.2,    -- Deformation multiplier on movement/resize
    }
        
    },

    animations = {
        enabled = true,
    },
})

hl.config({
    xwayland = {
        force_zero_scaling = true,
    },
})

-- Default curves and animations, see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })

-- Default springs
hl.curve("easy", { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

hl.animation({ leaf = "global", enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "border", enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows", enabled = true, speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.1, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.49, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers", enabled = true, speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4, bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.5, bezier = "linear", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 1.21, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "zoomFactor", enabled = true, speed = 7, bezier = "quick" })

-- Ref https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/
-- "Smart gaps" / "No gaps when only"
-- uncomment all if you wish to use that.
-- hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 0, gaps_in = 0 })
-- hl.workspace_rule({ workspace = "f[1]",   gaps_out = 0, gaps_in = 0 })
-- hl.window_rule({
--     name  = "no-gaps-wtv1",
--     match = { float = false, workspace = "w[tv1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- hl.window_rule({
--     name  = "no-gaps-f1",
--     match = { float = false, workspace = "f[1]" },
--     border_size = 0,
--     rounding    = 0,
-- })

hl.config({
    dwindle = {
        preserve_split = true,
    },
})

hl.config({
    master = {
        new_status = "master",
    },
})

hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})

hl.config({
    misc = {
        force_default_wallpaper = -1,    -- Set to 0 or 1 to disable the anime mascot wallpapers
        disable_hyprland_logo   = false, -- If true disables the random hyprland logo / anime girl background. :(
    },
})
hl.config({
  general = {
    gaps_in = 5,
    gaps_out = 10,
  },

  decoration = {
    rounding = 20,
    rounding_power = 2,

    shadow = {
      enabled = true,
      range = 4,
      render_power = 3,
      color = 0xee1a1a1a,
    },

    blur = {
      enabled = true,
      size = 3,
      passes = 2,
      vibrancy = 0.1696,
    },
  },
})


local suppressMaximizeRule = hl.window_rule({
    -- Ignore maximize requests from all apps. You'll probably like this.
    name           = "suppress-maximize-events",
    match          = { class = ".*" },

    suppress_event = "maximize",
})
suppressMaximizeRule:set_enabled(true)

hl.window_rule({
    -- Fix some dragging issues with XWayland
    name     = "fix-xwayland-drags",
    match    = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})

-- Layer rules also return a handle.
-- local overlayLayerRule = hl.layer_rule({
--     name  = "no-anim-overlay",
--     match = { namespace = "^my-overlay$" },
--     no_anim = true,
-- })
-- overlayLayerRule:set_enabled(false)

-- Hyprland-run windowrule


hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})

hl.window_rule({
    name = "ws2-on-eDP",
    workspace = 2,
    monitor = "eDP-1",
})

hl.window_rule({
    name = "ws1-on-eDP",
    workspace = 1,
    monitor = "eDP-1",
})

hl.window_rule({
    name = "browser-on-ws2",
    match = {
        class = "librewolf|firefox",
    },
    workspace = 2
})

hl.window_rule({
    name = "discord-on-ws4",
    match = {
        class = "discord|vesktop",
    },
    workspace = 4
})

hl.window_rule({
    name = "pin pip",
    match = { title = "Picture-in-Picture" },
    float = true,
    pin = true,
    --move = {100, 200}, 
})


hl.window_rule({
    name = "Float by class",
    match = { 
        class = "blueman-manager|blueman-services|nwg-look|rog-control-center|org.qbittorrent.qBittorrent|kvantummanager|\
                 org.gnome.seahorse.Application|xfce-polkit|org.polymc.PolyMC|engrampa|nm-connection-editor|system-config-printer|hyprland-share-picker|\
                 org.bleachbit.BleachBit|vlc|exo-desktop-item-edit|xdg-desktop-portal-gtk|org.gnome.eog|qt6ct|xfce-polkit|Bitwarden"
    },

    float = true,
    center = true,
    persistent_size = true,
    size = {"(monitor_w*0.5)", "(monitor_h*0.7)"}, 
})

hl.window_rule({
    name = "Float Bitwarden",
    match = {
        class = "firefox",
        title = ".*Bitwarden.*",
    },

    float = true,
    center = true,
    size = {"(monitor_w*0.5)", "(monitor_h*0.7)"},
})

hl.window_rule({
    name = "Kitty opacity and border",
    match = {
        class = "Kitty|peaclock"
    },

    opacity = "0.9 0.8",
    border_size = 2,
})



hl.window_rule({
    -- TODO fullscreens all games apps
    name = "Games in fullscreen",
    match = {
        class = "steam_app_.* | *.x64",
    },
    confine_pointer = true,
    fullscreen = true
})

hl.workspace_rule({ workspace = "1", monitor = "eDP-1", persistent = true})
hl.workspace_rule({ workspace = "2", monitor = "eDP-1", persistent = true})
hl.workspace_rule({ workspace = "3", monitor = "eDP-1", persistent = true})
hl.workspace_rule({ workspace = "4", monitor = "eDP-1", persistent = true})
hl.workspace_rule({ workspace = "5", monitor = "eDP-1", persistent = true})

hl.layer_rule({
  name = "noctalia",
  match = {
    namespace = "^noctalia-(bar-.+|notification|dock|panel|attached-panel|osd|window-switcher)$",
  },
  no_anim = true,
  ignore_alpha = 0.5,
  blur = true,
  blur_popups = true,
})