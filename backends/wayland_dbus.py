import dbus
import sys
import json

def apply_config(target_connector, config):
    bus = dbus.SessionBus()
    display_config = bus.get_object('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig')
    serial, physical_monitors, logical_monitors, properties = display_config.GetCurrentState(dbus_interface='org.gnome.Mutter.DisplayConfig')
    
    new_logical_monitors = []
    set_primary = config.get('is_primary', False)
    
    for lm in logical_monitors:
        x, y, scale, transform, primary, lm_phys_monitors, _ = lm
        
        is_target_lm = any(str(pm[0]) == target_connector for pm in lm_phys_monitors)
        
        if set_primary:
            primary = is_target_lm
        elif is_target_lm and 'is_primary' in config:
            primary = config['is_primary']
            
        if is_target_lm and 'orientation' in config:
            transform = int(config['orientation'])
            
        new_linked = []
        for pm_info in lm_phys_monitors:
            connector = str(pm_info[0])
            best_mode = ""
            
            for pm in physical_monitors:
                if str(pm[0][0]) == connector:
                    for mode in pm[1]:
                        if mode[6].get('is-current', False):
                            best_mode = str(mode[0])
                            break
                    break
            
            if is_target_lm and connector == target_connector and 'mode' in config:
                target_res = config['mode']
                target_rate = config.get('rate')
                for pm in physical_monitors:
                    if str(pm[0][0]) == connector:
                        for mode in pm[1]:
                            m_id, m_w, m_h, m_rate = str(mode[0]), int(mode[1]), int(mode[2]), float(mode[3])
                            if f"{m_w}x{m_h}" == target_res:
                                if target_rate is None or abs(m_rate - float(target_rate)) < 0.2:
                                    best_mode = m_id
                                    break
                        break
            
            new_linked.append(dbus.Struct((connector, best_mode, {}), signature='ssa{sv}'))
            
        new_logical_monitors.append(dbus.Struct((int(x), int(y), float(scale), int(transform), bool(primary), new_linked), signature='iiduba(ssa{sv})'))
        
    display_config.ApplyMonitorsConfig(dbus.UInt32(serial), dbus.UInt32(2), new_logical_monitors, {}, dbus_interface='org.gnome.Mutter.DisplayConfig')

def apply_arrangement(positions):
    bus = dbus.SessionBus()
    display_config = bus.get_object('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig')
    serial, physical_monitors, logical_monitors, properties = display_config.GetCurrentState(dbus_interface='org.gnome.Mutter.DisplayConfig')
    
    new_logical_monitors = []
    for lm in logical_monitors:
        x, y, scale, transform, primary, lm_phys_monitors, _ = lm
        
        matched_connector = None
        for pm in lm_phys_monitors:
            if str(pm[0]) in positions:
                matched_connector = str(pm[0])
                break
                
        if matched_connector:
            x = positions[matched_connector]['x']
            y = positions[matched_connector]['y']
            
        new_linked = []
        for pm_info in lm_phys_monitors:
            connector = str(pm_info[0])
            best_mode = ""
            for pm in physical_monitors:
                if str(pm[0][0]) == connector:
                    for mode in pm[1]:
                        if mode[6].get('is-current', False):
                            best_mode = str(mode[0])
                            break
                    break
                    
            new_linked.append(dbus.Struct((connector, best_mode, {}), signature='ssa{sv}'))
            
        new_logical_monitors.append(dbus.Struct((int(x), int(y), float(scale), int(transform), bool(primary), new_linked), signature='iiduba(ssa{sv})'))
        
    display_config.ApplyMonitorsConfig(dbus.UInt32(serial), dbus.UInt32(2), new_logical_monitors, {}, dbus_interface='org.gnome.Mutter.DisplayConfig')

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "config":
        connector = sys.argv[2]
        cfg = json.loads(sys.argv[3])
        apply_config(connector, cfg)
    elif action == "arrange":
        pos = json.loads(sys.argv[2])
        apply_arrangement(pos)
