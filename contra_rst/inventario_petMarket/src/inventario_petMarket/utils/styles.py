"""Paleta y estilos compartidos para las pantallas Toga."""
from toga.style import Pack
from toga.style.pack import COLUMN

BG_APP = "#1a1a1a"
BG_SIDEBAR = "#111111"
BG_CARD = "#242424"
BG_CARD2 = "#2a2a2a"
BG_INPUT = "#2e2e2e"
BORDER = "#333333"
TXT_WHITE = "#f0f0f0"
TXT_GRAY = "#888888"
TXT_LGRAY = "#aaaaaa"
GREEN = "#1D9E75"
GREEN_LT = "#0d3d2d"
GREEN_DIM = "#155c44"
RED = "#e05252"
AMBER = "#d4922a"
BLUE = "#4a9eff"
NAV_ACTIVE_BG = "#1e2e28"

FONT_H = ("Segoe UI", 14, "bold")
FONT_N = ("Segoe UI", 12)
FONT_S = ("Segoe UI", 11)
F_LOGO = ("Segoe UI", 15, "bold")
F_SUB = ("Segoe UI", 10)
F_TITLE = ("Segoe UI", 16, "bold")
F_NAV = ("Segoe UI", 12)
F_BTN = ("Segoe UI", 11, "bold")
F_SMALL = ("Segoe UI", 10)
F_MONO = ("Consolas", 11)


def card_style(margin=15, margin_right=5):
    return Pack(direction=COLUMN, margin=margin, margin_right=margin_right,
                background_color=BG_CARD, font_family="Segoe UI", font_size=12)


def input_style():
    return Pack(margin=10, background_color=BG_INPUT, color=TXT_WHITE,
                font_family="Segoe UI", font_size=12)


def button_primary():
    return Pack(margin=12, background_color=BLUE, color=TXT_WHITE,
                font_size=14, font_weight="bold", font_family="Segoe UI")


def button_success():
    return Pack(margin=12, background_color=GREEN, color=TXT_WHITE,
                font_size=14, font_weight="bold", font_family="Segoe UI")


def button_danger():
    return Pack(margin=12, background_color=RED, color=TXT_WHITE,
                font_size=14, font_weight="bold", font_family="Segoe UI")


COLORS = {
    "app_background": BG_APP, "background": BG_APP,
    "sidebar_background": BG_SIDEBAR, "card_background": BG_CARD,
    "primary": BLUE, "primary_light": GREEN_LT,
    "secondary": BG_CARD2, "success": GREEN, "danger": RED,
    "warning": AMBER, "info": BLUE, "white": TXT_WHITE,
    "gray_50": BG_CARD, "gray_100": BG_INPUT, "gray_200": BORDER,
    "gray_300": "#666666", "gray_400": "#777777", "gray_500": TXT_GRAY,
    "gray_600": TXT_GRAY, "gray_700": TXT_LGRAY, "gray_800": BG_INPUT,
    "gray_900": BG_SIDEBAR, "text_primary": TXT_WHITE,
    "text_secondary": TXT_LGRAY, "text_light": TXT_WHITE,
    "border": BORDER, "border_light": BORDER, "transparent": BG_APP,
    "danger_light": "#3b2424", "success_light": "#155c44",
    "warning_light": "#3d301c",
}
STYLES = {
    "title": {"font_size": 24, "font_weight": "bold", "color": TXT_WHITE, "font": F_TITLE},
    "subtitle": {"font_size": 18, "font_weight": "bold", "color": TXT_WHITE, "font": FONT_H},
    "heading": {"font_size": 16, "font_weight": "bold", "color": TXT_WHITE, "font": F_TITLE},
    "body": {"font_size": 14, "color": TXT_WHITE, "font": FONT_N},
    "small": {"font_size": 12, "color": TXT_LGRAY, "font": F_SMALL},
}
SPACING = {"padding_small": 5, "padding_medium": 10, "padding_large": 20,
           "margin_small": 5, "margin_medium": 10, "margin_large": 20}
