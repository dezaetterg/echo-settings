from backends.sound_backend import SoundBackend

class SoundService:
    def __init__(self):
        self.backend = SoundBackend()
        
    def get_output_devices(self):
        return self.backend.get_output_devices()
        
    def get_active_output_device(self):
        return self.backend.get_active_output_device()
        
    def set_active_output_device(self, name):
        self.backend.set_active_output_device(name)

    def get_active_device_info(self):
        return self.backend.get_active_device_info()

    def get_output_volume(self):
        return self.backend.get_output_volume()
        
    def set_output_volume(self, value):
        self.backend.set_output_volume(value)
        
    def get_output_balance(self):
        return self.backend.get_output_balance()

    def set_output_balance(self, value):
        self.backend.set_output_balance(value)

    def test_speakers(self):
        self.backend.test_speakers()
        
    def get_input_devices(self):
        return self.backend.get_input_devices()
        
    def get_active_input_device(self):
        return self.backend.get_active_input_device()
        
    def set_active_input_device(self, name):
        self.backend.set_active_input_device(name)

    def get_input_volume(self):
        return self.backend.get_input_volume()
        
    def set_input_volume(self, value):
        self.backend.set_input_volume(value)
        
    def get_system_sounds_enabled(self):
        return self.backend.get_system_sounds_enabled()

    def set_system_sounds_enabled(self, enabled):
        self.backend.set_system_sounds_enabled(enabled)
