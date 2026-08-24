from backends.general_backend import GeneralBackend

class GeneralService:
    def __init__(self):
        self.backend = GeneralBackend()

    def get_device_info(self):
        return {
            "Hostname": self.backend.get_hostname(),
            "CPU": self.backend.get_cpu(),
            "GPU": self.backend.get_gpu(),
            "RAM": self.backend.get_ram(),
            "Kernel": self.backend.get_kernel(),
            "Architecture": self.backend.get_architecture(),
            "Disk": self.backend.get_disk()
        }

    def get_default_browser(self):
        return self.backend.get_default_browser()
        
    def set_default_browser(self, desktop_file):
        self.backend.set_default_browser(desktop_file)
        
    def get_installed_browsers(self):
        return self.backend.get_installed_browsers()
        
    def get_startup(self): return self.backend.get_startup()
    def set_startup(self, v): self.backend.set_startup(v)
    
    def get_restore_page(self): return self.backend.get_restore_page()
    def set_restore_page(self, v): self.backend.set_restore_page(v)
    
    def get_remember_size(self): return self.backend.get_remember_size()
    def set_remember_size(self, v): self.backend.set_remember_size(v)
    
    def get_ntp(self): return self.backend.get_ntp()
    def set_ntp(self, v): self.backend.set_ntp(v)
    
    def get_timezone(self): return self.backend.get_timezone()
    def set_timezone(self, v): self.backend.set_timezone(v)
    def get_all_timezones(self): return self.backend.get_all_timezones()
    
    def get_24_hour(self): return self.backend.get_24_hour()
    def set_24_hour(self, v): self.backend.set_24_hour(v)
    
    def get_dnd(self): return self.backend.get_dnd()
    def set_dnd(self, v): self.backend.set_dnd(v)
    
    def get_notif_sounds(self): return self.backend.get_notif_sounds()
    def set_notif_sounds(self, v): self.backend.set_notif_sounds(v)
    
    def get_locales(self): return self.backend.get_locales()
    def get_current_locale(self): return self.backend.get_current_locale()
    def set_locale(self, loc): self.backend.set_locale(loc)
    
    def get_region(self): return self.backend.get_region()
    def set_region(self, reg): self.backend.set_region(reg)
    
    def check_updates(self):
        return self.backend.check_updates()

    # Session actions
    def lock_screen(self):
        self.backend.lock_screen()

    def log_out(self):
        self.backend.log_out()

    def restart(self):
        self.backend.restart()

    def power_off(self):
        self.backend.power_off()
