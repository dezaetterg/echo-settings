import dbus
import sys

def set_hdr(enabled):
    bus = dbus.SessionBus()
    display_config = bus.get_object('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig')
    serial, physical_monitors, logical_monitors, properties = display_config.GetCurrentState(dbus_interface='org.gnome.Mutter.DisplayConfig')

    new_logical_monitors = []
    changed = False
    
    for lm in logical_monitors:
        x, y, scale, transform, primary, lm_phys_monitors, _ = lm
        new_linked = []
        
        for pm_info in lm_phys_monitors:
            connector = str(pm_info[0])
            best_mode = ""
            
            supports_hdr = False
            for pm in physical_monitors:
                if str(pm[0][0]) == connector:
                    # Find current mode
                    for mode in pm[1]:
                        if mode[6].get('is-current', False):
                            best_mode = str(mode[0])
                            break
                    # Check HDR support
                    pm_props = pm[2]
                    if "supported-color-modes" in pm_props:
                        if 1 in pm_props["supported-color-modes"]:
                            supports_hdr = True
                if best_mode:
                    break
            
            props = dbus.Dictionary(signature='sv')
            if supports_hdr:
                props['color-mode'] = dbus.UInt32(1 if enabled else 0)
                changed = True
                
            new_linked.append(dbus.Struct((connector, best_mode, props), signature='ssa{sv}'))
        
        new_logical_monitors.append(dbus.Struct((int(x), int(y), float(scale), int(transform), bool(primary), new_linked), signature='iiduba(ssa{sv})'))

    if changed:
        display_config.ApplyMonitorsConfig(dbus.UInt32(serial), dbus.UInt32(2), new_logical_monitors, {}, dbus_interface='org.gnome.Mutter.DisplayConfig')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_hdr(sys.argv[1] == "1")
