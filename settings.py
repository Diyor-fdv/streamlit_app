from pathlib import Path
import base64
from PIL import Image


LOGO_PATH = Path(__file__).parent / "logo.jpg"


def get_logo_image():
    return Image.open(LOGO_PATH)


def get_logo_data_uri() -> str:
    with open(LOGO_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


APP_USER = "flight"
APP_PASS = "task123"


COLOR_NAVY = "#1E293B"
COLOR_NAVY_TEXT = "#FFFFFF"
COLOR_DEPARTURE = "#DCFCE7"
COLOR_ARRIVAL_TIME = "#FEE2E2"
COLOR_ROW_EVEN = "#F1F5F9"
COLOR_ROW_ODD = "#FFFFFF"
COLOR_DELAY = "#DC2626"


DEFAULT_WIDTH = 140
WIDTHS = {"Aircraft number": 160, "Flight number": 140, "Time of Arrival": 140, "Time of Departure": 140}
