from enum import IntEnum

class Weather(IntEnum):
    DEFAULT = 0
    SNOW = 1
    RAIN = 2
    MOONBEAM = 3
    PESTILENCE = 4
    HARVEST = 5
    SIROCCO = 6
    SPRING = 7
    ASH = 8
    AURORA = 9

    def __str__(self) -> str:
        return self.name.capitalize()

WEATHER_LABELS = {weather.value: str(weather) for weather in Weather}
