import dbus
import sys

def apply_config(target_connector, target_res, target_rate=None):
    bus = dbus.SessionBus()
    display_config = bus.get_object('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig')
    
    # Get current state
    serial, physical_monitors, logical_monitors, properties = display_config.GetCurrentState(dbus_interface='org.gnome.Mutter.DisplayConfig')
    
    # We will build the new logical monitors array
    new_logical_monitors = []
    
    for lm in logical_monitors:
        x = lm[0]
        y = lm[1]
        scale = lm[2]
        transform = lm[3]
        primary = lm[4]
        lm_phys_monitors = lm[5] # array of (connector, vendor, product, serial)
        
        new_linked = []
        for pm_info in lm_phys_monitors:
            connector = pm_info[0]
            
            # Find the physical monitor definition to get its current mode
            best_mode = None
            
            for pm in physical_monitors:
                info = pm[0]
                modes = pm[1]
                if info[0] == connector:
                    # Find current mode
                    for mode in modes:
                        if mode[6].get('is-current', False):
                            best_mode = mode[0]
                            break
                            
                    # If this is the target connector, find the requested mode
                    if connector == target_connector:
                        for mode in modes:
                            m_id, m_w, m_h, m_rate, m_scale, m_su, m_props = mode
                            res_str = f"{m_w}x{m_h}"
                            if res_str == target_res:
                                if target_rate is None or abs(m_rate - float(target_rate)) < 0.2:
                                    best_mode = m_id
                                    break
                    break
                    
            if best_mode is None:
                continue
                
            new_linked.append(dbus.Struct((connector, best_mode, {}), signature='ssa{sv}'))
            
        new_logical_monitors.append(dbus.Struct((x, y, scale, transform, primary, new_linked), signature='iiduba(ssa{sv})'))
        
    try:
        # method 1 = verify, 2 = apply (persistent)
        display_config.ApplyMonitorsConfig(dbus.UInt32(serial), dbus.UInt32(2), new_logical_monitors, {}, dbus_interface='org.gnome.Mutter.DisplayConfig')
        print("Success")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        apply_config(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
