from PyQt5.QtWidgets import QMainWindow
from gui.ui_main_window import Ui_MainWindow
from core.manager import DotaManager
from data.weather import Weather, WEATHER_LABELS
import keyboard


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.manager = DotaManager()

        self.bind_events()
        
        keyboard.add_hotkey("insert", self.toggle_menu, suppress=True)

    def bind_events(self):
        self.cameraSlider.valueChanged.connect(self.on_camera_slider_changed)
        self.fovSlider.valueChanged.connect(self.on_fov_slider_changed)
        self.farzSlider.valueChanged.connect(self.on_farz_slider_changed)
        self.weatherIDSlider.valueChanged.connect(self.on_weather_changed)

        self.fogButton.clicked.connect(self.on_fog_toggled)
        self.toggleTeleportsButton.clicked.connect(self.on_teleports_toggled)
        self.resetButton.clicked.connect(self.reset_to_default)

    def on_camera_slider_changed(self, value):
        self.cameraLabel.setText(f"Distance (Value: {value})")
        self.manager.set_camera_distance(float(value))

    def on_fov_slider_changed(self, value):
        self.fovLabel.setText(f"FOV (Value: {value})")
        self.manager.set_camera_fov(float(value))

    def on_farz_slider_changed(self, value):
        self.farzLabel.setText(f"FarZ (Value: {value})")
        self.manager.set_camera_farz(float(value))

    def on_weather_changed(self, value):
        self.weatherIDLabel.setText(
            f"Weather (Value: {WEATHER_LABELS[value]})"
        )
        self.manager.set_weather(Weather(value))

    def on_fog_toggled(self):
        value = self.manager.states["fog_enabled"]
        self.fogButton.setText(
            f"Toggle fog (Value: {not value})"
        )
        self.manager.toggle_fog()

    def on_teleports_toggled(self):
        value = self.manager.states["show_teleports"]
        self.toggleTeleportsButton.setText(
            f"Toggle Show Teleports (Value: {value})"
        )
        self.manager.toggle_teleports()

    def reset_to_default(self):
        self.manager.restore_defaults()
        self.retranslateUi(self)

        self.cameraSlider.setProperty("value", 1200)
        self.fovSlider.setProperty("value", 70)
        self.farzSlider.setProperty("value", -1)
        self.weatherIDSlider.setProperty("value", 0)

    def toggle_menu(self):
        self.setVisible(not self.isVisible())

    def closeEvent(self, event):
        keyboard.unhook_all()
        self.reset_to_default()
        event.accept()
