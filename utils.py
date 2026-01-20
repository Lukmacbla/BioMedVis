import colorsys
import pandas as pd
import re

class color_utils:
    """
    Utility functions for color manipulation.
    This was generated with the help of generative AI (Claude Sonnet 4.5)
    """

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        )

    def desaturate(hex_color, saturation, value):
        r, g, b = color_utils.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        s = s * saturation
        v = v * value
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return color_utils.rgb_to_hex((r, g, b))


def icd9_to_category(code: str) -> str:
    """
    Map an ICD-9(-CM) diagnosis code (001-999, V, E) to a high-level category.
    This was generated with the help of generative AI (Perplexity)
    """

    if pd.isna(code):
        return "Unknown"

    code_str = str(code).strip().upper()

    # V codes: factors influencing health status / contact with health services
    if code_str.startswith("V"):
        return "Factors influencing health status / contact with health services"

    # E codes: external causes of injury/poisoning
    if code_str.startswith("E"):
        return "External causes of injury and poisoning"

    # Otherwise treat as numeric 001–999
    m = re.match(r"(\d+)", code_str)
    if not m:
        return "Unknown"
    num = int(m.group(1))

    if 1 <= num <= 139:
        return "Infectious and parasitic"
    elif 140 <= num <= 239:
        return "Neoplasms"
    elif 240 <= num <= 279:
        return "Endocrine, nutritional, metabolic, immunity"
    elif 280 <= num <= 289:
        return "Diseases of the blood"
    elif 290 <= num <= 319:
        return "Mental disorders"
    elif 320 <= num <= 389:
        return "Nervous system and sense organs"
    elif 390 <= num <= 459:
        return "Circulatory system"
    elif 460 <= num <= 519:
        return "Respiratory system"
    elif 520 <= num <= 579:
        return "Digestive system"
    elif 580 <= num <= 629:
        return "Genitourinary system"
    elif 630 <= num <= 679:
        return "Pregnancy, childbirth, puerperium"
    elif 680 <= num <= 709:
        return "Skin and subcutaneous tissue"
    elif 710 <= num <= 739:
        return "Musculoskeletal and connective tissue"
    elif 740 <= num <= 759:
        return "Congenital anomalies"
    elif 760 <= num <= 779:
        return "Perinatal conditions"
    elif 780 <= num <= 799:
        return "Symptoms, signs, ill-defined"
    elif 800 <= num <= 999:
        return "Injury and poisoning"
    else:
        return "Unknown"