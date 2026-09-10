------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/

-- Lock screen and disable monitor when closing the lid
-- Helper function to get the first connected external monitor (not eDP-1)
--local function get_external_monitor()
--local monitors = hl.get_monitors()
--for _, mon in ipairs(monitors) do
-- Check for any monitor that is not the internal display, is not disabled, and has a valid name
--if mon.name ~= "eDP-1" and mon.disabled == false and mon.name ~= "" then
--return mon
--end
--end
--return nil
--end

-- Lock screen and handle monitor switching
--hl.bind("switch:on:Lid Switch", function()
-- Always trigger the lock
--hl.exec("hyprlock --immediate-render")

--local external = get_external_monitor()
--if external then
-- Disable internal only if external is present
--hl.monitor({
--output = "eDP-1",
--disabled = true
--})
-- Pin external to 0x0 so bars/background don't shift
--hl.monitor({
--output = external.name,
--mode = "preferred",
--position = "0x0",
--scale = 1.0 })
--end
-- If no external monitor, do nothing (let logind.conf handle)
--end, { locked = true })

-- Enable monitor when opening the lid
--hl.bind("switch:off:Lid Switch", function()
-- Re-enable internal monitor
--hl.monitor({
--output = "eDP-1",
--mode = "2560x1600@120",
--position = "0x0",
--scale = 1.25,
--disabled = false
--})

-- Reset external position back to the right
--local external = get_external_monitor()
--if external then
--hl.monitor({
--output = external.name,
--position = "2048x0",
--scale = 1.0
--})
--end
--end, { locked = true })

hl.monitor({
    output = "eDP-1",
    mode = "2560x1600@120",
    position = "0x0",
    scale = 1.25,
    disabled = false
})

hl.monitor({
    output = "desc:LG Electronics W2442",
    mode = "1920x1080@60",
    position = "auto-up",
    scale = 1,
    transform = 0
})

hl.monitor({
    output = "desc:Eizo Nanao Corporation EV2495",
    mode = "preferred",
    position = "auto",
    scale = 1,
    transform = 1
})

hl.monitor({
    output = "EXT-1",
    mode = "2560x1600@120",
    position = "auto-right",
    scale = 1.60,
    transform = 0
})

--hl.monitor({
--   output = "desc:Panasonic Industry Company Panasonic-TV",
--   mode = "1920x1080@60",
--   position = "auto-up",
--   scale = 1.33,
--   transform = 0
--})

hl.monitor({
    output = "desc:Samsung Electric Company LC27G7xT H4ZT900075",
    mode = "2560x1440@144",
    position = "auto-right",
    scale = 1,
    transform = 0,
    --mirror = "eDP-1"
})

hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = 1,
    mirror = "eDP-1"
})
hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = 1,
    mirror = "eDP-1"
})
