from core.camera import DotaCamera
from core.other import DotaOther
from memory.memory import Memory
from data.weather import Weather
import logging

logger = logging.getLogger("dota_minihack")

class DotaManager:
    def __init__(self) -> None:
        self.memory = Memory("dota2.exe")
        self.camera = DotaCamera(self.memory)
        self.other = DotaOther(self.memory)
        self.states = {
            "fog_enabled": True,
            "show_teleports": False
        }

    def set_camera_distance(self, distance: float) -> None:
        self.camera.set_distance(distance)

    def set_camera_fov(self, fov: float) -> None:
        self.camera.set_fov(fov)

    def set_camera_farz(self, farz: float) -> None:
        self.camera.set_farz(farz)

    def set_weather(self, weather: Weather) -> None:
        self.other.set_weather(weather.value)

    def toggle_fog(self) -> None:
        self.states["fog_enabled"] = not self.states["fog_enabled"]
        self.camera.set_fog_enable(self.states["fog_enabled"])

    def toggle_teleports(self) -> None:
        self.states["show_teleports"] = not self.states["show_teleports"]
        self.other.show_teleports(self.states["show_teleports"])

    def restore_defaults(self) -> None:
        logger.info("Restoring default settings...")
        self.camera.set_distance()
        self.camera.set_fov()
        self.camera.set_farz()
        self.camera.set_fog_enable()
        self.other.set_weather()
        self.other.show_teleports()
