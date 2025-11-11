import html
import pandas as pd
from settings import (
    DEFAULT_WIDTH, WIDTHS,
    COLOR_ROW_EVEN, COLOR_ROW_ODD, COLOR_DELAY,
    COLOR_DEPARTURE, COLOR_ARRIVAL_TIME
)


def col_width(col_name: str) -> int:
    return WIDTHS.get(col_name, DEFAULT_WIDTH)


def _hex_to_rgb(hx: str):
    hx = hx.lstrip('#')
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def _luminance(rgb):
    def f(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def pick_text_color_for_bg(bg_hex: str) -> str:
    try:
        lum = _luminance(_hex_to_rgb(bg_hex))
    except Exception:
        return "#0f172a"
    return "#ffffff" if lum < 0.5 else "#0f172a"


def match_delay_series(df_full: pd.DataFrame, col: str) -> pd.Series:
    for c in (f"{col}_delay", f"Departure_{col}_delay", f"Arrival_{col}_delay"):
        if c in df_full.columns:
            s = df_full[c]
            return s.astype(str).isin(["1", "True", "true"]).astype(bool)
    return pd.Series(False, index=df_full.index)


DEFAULT_WIDTH = DEFAULT_WIDTH
WIDTHS = WIDTHS


def render_table_html(df_full: pd.DataFrame) -> str:
    dur_cols = [c for c in df_full.columns if not c.endswith("_delay")]
    colgroup = "<colgroup>" + "".join([f'<col style="min-width:{col_width(c)}px;">' for c in dur_cols]) + "</colgroup>"
    ths = [f"<th>{html.escape(c)}</th>" for c in dur_cols]
    thead = "<thead><tr>" + "".join(ths) + "</tr></thead>"

    rows_html = []
    for r_idx, row in df_full.iterrows():
        base_bg = COLOR_ROW_EVEN if (r_idx % 2 == 0) else COLOR_ROW_ODD
        base_fg = pick_text_color_for_bg(base_bg)
        tds = []
        for col in dur_cols:
            val = row[col]

            if isinstance(val, pd.Series):
                val = val.iloc[0]

            sval = "" if pd.isna(val) else str(val)
            sval = html.escape(sval)

            bg = base_bg
            fg = base_fg
            weight = "400"

            delay_mask = match_delay_series(df_full, col)
            if delay_mask.iloc[r_idx]:
                bg = COLOR_DELAY;
                fg = "#ffffff";
                weight = "600"
            else:
                if col == "Time of Departure":
                    bg = COLOR_DEPARTURE;
                    fg = pick_text_color_for_bg(COLOR_DEPARTURE);
                    weight = "600"
                elif col == "Time of Arrival":
                    bg = COLOR_ARRIVAL_TIME;
                    fg = pick_text_color_for_bg(COLOR_ARRIVAL_TIME);
                    weight = "600"

            style = (
                f"background:{bg}; color:{fg}; font-weight:{weight}; "
                f"padding:6px 8px; text-align:center; vertical-align:middle; white-space:normal; word-break:break-word;"
            )
            tds.append(f'<td style="{style}">{sval}</td>')
        rows_html.append("<tr>" + "".join(tds) + "</tr>")

    tbody = "<tbody>" + "".join(rows_html) + "</tbody>"
    table_css = """
    <style>
    .table-wrap{ width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,.06); }
    .table-wrap table{ width:100%; table-layout:fixed; border-collapse:separate; border-spacing:0; }
    .table-wrap thead th{ position:sticky; top:0; z-index:1; }
    .table-wrap th, .table-wrap td{
      word-break:break-word; white-space:normal; text-align:center; vertical-align:middle; padding:6px 8px;
    }
    @media (max-width: 768px){
      .table-wrap table{ font-size: 12.5px; }
    }
    </style>
    """
    return f"""
    {table_css}
    <div class="table-wrap">
      <table>
        {colgroup}{thead}{tbody}
      </table>
    </div>
    """
