------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
hl.monitor({
    output   = "eDP-1",
    mode     = "2560x1600@120",
    position = "0x0",
    scale    = 1.25,
})
hl.monitor({ 
    output = "", 
    mode = "preferred", 
    position = "auto", 
    scale = 1, 
    mirror = "eDP-1" 
})

hl.monitor({ 
    output = "desc:LG Electronics W2442", 
    mode = "preferred", 
    position = "auto", 
    scale = 1, 
    transform = 1 
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
    position = "auto-left", 
    scale = 1.60, 
    transform = 0 
})

hl.monitor({ 
    output = "desc:Panasonic Industry Company Panasonic-TV", 
    mode = "1920x1080@60", 
    position = "auto-up", 
    scale = 1, 
    transform = 0 
})

hl.monitor({ 
    output = "desc:Samsung Electric Company LC27G7xT H4ZT900075", 
    mode = "2560x1440@240", 
    position = "auto-right", 
    scale = 1, 
    transform = 0 
})

hl.monitor({ 
    output = "", 
    mode = "preferred", 
    position = "auto", 
    scale = 1, 
    mirror = "eDP-1" 
})