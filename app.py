import streamlit as st
import pandas as pd
from streamlit.components.v1 import html as st_html

from settings import get_logo_image, get_logo_data_uri
from settings import (
    COLOR_NAVY, COLOR_NAVY_TEXT,
    APP_USER, APP_PASS,
)

from filters import distinct_aircraft, distinct_flights
from mock_data import pivot_table
from utility import render_table_html

st.set_page_config(
    page_title="Centrum Air Flight Monitor (Powered by Diyorbek)",
    page_icon=get_logo_image(),
    layout="wide",
)


LOGO_DATA_URI = get_logo_data_uri()


def render_login():
    st.markdown(
        f"""
        <style>
          .ca-login-wrap{{
            min-height: 40vh; display:flex; align-items:flex-start; justify-content:center;
            padding:40px 16px;
          }}
          .ca-login{{
            width:520px; border-radius:22px;
            background:#0E1A30;
            border:1px solid rgba(148,163,184,.18);
            box-shadow: 0 35px 70px rgba(2,6,23,.45);
            color:#E5E7EB; padding:28px 26px 22px;
          }}
          .ca-login .title{{
            display:flex; flex-direction:column; align-items:center; gap:14px; margin:0 0 6px 0;
          }}
          .ca-login .title img{{height:56px;width:56px;border-radius:14px;}}
          .ca-login .title h2{{margin:0; font-size:24px; font-weight:800; color:#fff; letter-spacing:.2px;}}
          .ca-login [data-testid="stMarkdownContainer"] h1 a,
          .ca-login [data-testid="stMarkdownContainer"] h2 a{{display:none!important;}}
          .ca-login [data-testid="stForm"]{{background:transparent!important; padding:0!important; border:none!important;}}
          .ca-login .field-label{{font-size:13px; color:#cbd5e1; margin:12px 2px 6px 2px; font-weight:600;}}
          .ca-login .stTextInput > div > div{{
            background:#ffffff !important;
            border:1px solid #E2E8F0 !important;
            border-radius:12px; padding:2px 12px;
          }}
          .ca-login input[type="text"],
          .ca-login input[type="password"]{{
            height:46px; background:#ffffff !important;
            color:#0f172a !important;
            border:none !important; box-shadow:none !important; border-radius:9px; font-size:15px;
          }}
          .ca-login input::placeholder{{ color:#64748b !important; opacity:1; }}
          .ca-login input:-webkit-autofill{{
            -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
            -webkit-text-fill-color:#0f172a !important; caret-color:#0f172a !important;
          }}
          .ca-login .stButton > button{{
            width:100%; height:48px; border-radius:12px;
            background:#F43F5E !important; color:#fff !important; border:1px solid #F43F5E !important;
            font-weight:800; letter-spacing:.2px; margin-top:10px; font-size:15px;
          }}
          .ca-login .stButton > button:hover{{ filter:brightness(1.06); }}
          #MainMenu{{visibility:hidden;}}
          header [data-testid="stToolbar"]{{display:none!important;}}
          footer{{visibility:hidden;}}
          div[data-testid="stStatusWidget"]{{display:none!important;}}
        </style>
        <div class="ca-login-wrap">
          <div class="ca-login">
            <div class="title">
              <img src="{LOGO_DATA_URI}" />
              <h2>Sign in to continue</h2>
            </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False, border=False):
        st.markdown('<div class="field-label">Username</div>', unsafe_allow_html=True)
        u = st.text_input("", key="login_username", placeholder="login", label_visibility="collapsed")

        st.markdown('<div class="field-label">Password</div>', unsafe_allow_html=True)
        p = st.text_input("", key="login_password", type="password", placeholder="password",
                          label_visibility="collapsed")

        ok = st.form_submit_button("Sign In")
        if ok:
            if u == APP_USER and p == APP_PASS:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("Incorrect username or password")

    st.markdown('</div></div>', unsafe_allow_html=True)


if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

if not st.session_state.auth_ok:
    render_login()
    st.stop()

st.markdown(
    f"""
<style>
#MainMenu {{ visibility: hidden; }}
header [data-testid="stToolbar"] {{ display: none; }}
footer {{ visibility: hidden; }}
h1.app-title {{ font-size: 28px !important; margin: 0 !important; font-weight: 700 !important; letter-spacing: .2px; }}
div.app-time {{ font-size: 18px; font-weight: 600; letter-spacing: .5px; opacity: 0.95; }}
.table-wrap {{ overflow:auto; border:1px solid #E5E7EB; border-radius:10px; max-height:92vh; }}
table thead th {{
  font-size: 13px !important; line-height: 1.25; vertical-align: bottom; white-space: normal; word-break: break-word;
  position: sticky; top: 0; background:{COLOR_NAVY}; color:#FFFFFF; padding:8px; text-align:left;
}}
.tabs label {{
  border: 1px solid #cbd5e1; padding: 8px 12px; margin-right: 8px; border-radius: 10px; background: #ffffff; color: #0f172a;
  cursor: pointer; transition: all .15s ease;
}}
.tabs label:hover {{ border-color: {COLOR_NAVY}; }}
.tabs label[data-checked="true"] {{ background: {COLOR_NAVY}; color: #FFFFFF; border-color: {COLOR_NAVY}; }}
.tabs input[type="radio"] {{ display:none; }}
.filter-label {{ font-size:13px; color:#475569; margin-bottom:6px; }}
@media (prefers-color-scheme: dark) {{ .table-wrap {{ border-color: #1f2937; }} }}
</style>
<div style="display:flex;justify-content:space-between;align-items:center;background:{COLOR_NAVY};color:#FFFFFF;padding:12px 16px;border-radius:12px;margin-bottom:10px;">
  <div style="display:flex;gap:12px;align-items:center;">
    <img src="{LOGO_DATA_URI}" style="height:40px;width:auto;border-radius:6px;object-fit:contain;" />
    <h1 class="app-title">Centrum Air — Ground Handling Tasks (Powered by Diyorbek)</h1>
  </div>
  <div class="app-time"><span id="local-clock"></span></div>
</div>
""",
    unsafe_allow_html=True,
)

st_html(
    """
<script>
(function(){
  function pad(n){return n.toString().padStart(2,'0');}
  function tick(){
    const d = new Date();
    const s = pad(d.getDate())+'-'+pad(d.getMonth()+1)+'-'+d.getFullYear()
            +' '+pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds());
    const el = window.parent.document.querySelector('.app-time #local-clock');
    if(el) el.textContent = s;
  }
  tick();
  setInterval(tick, 1000);
})();
</script>
""",
    height=0,
)

st.markdown(
    """
<style>
iframe[title="streamlit.components.v1.html"]{
  pointer-events:none !important; width:0 !important; height:0 !important;
  position:absolute !important; left:-9999px !important; opacity:0 !important; z-index:-1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

if "selected_table" not in st.session_state:
    st.session_state.selected_table = "all"

st.markdown('<div class="tabs">', unsafe_allow_html=True)
tab = st.radio(
    "",
    ["All", "Departure", "Arrival"],
    horizontal=True,
    index=["all", "departure", "arrival"].index(st.session_state.selected_table),
    key="tab_choice",
)
st.markdown('</div>', unsafe_allow_html=True)
st.session_state.selected_table = tab.lower()

fc1, fc2, fc3 = st.columns([2, 2, 1.2])

with fc3:
    st.markdown('<div class="filter-label">Date</div>', unsafe_allow_html=True)
    date_choice = st.selectbox("", ["All dates", "Today", "Yesterday"], index=0, key="date_choice_select")

aircraft_opts = distinct_aircraft(date_choice, st.session_state.get("filter_flights", []))
with fc1:
    st.markdown('<div class="filter-label">Aircraft number</div>', unsafe_allow_html=True)
    aircraft_selected = st.multiselect(
        "",
        options=aircraft_opts,
        default=st.session_state.get("filter_aircraft", []),
        placeholder="Type or pick aircraft",
        key="aircraft_ms",
    )
    st.session_state["filter_aircraft"] = aircraft_selected

flight_opts = distinct_flights(date_choice, aircraft_selected)
with fc2:
    st.markdown('<div class="filter-label">Flight number</div>', unsafe_allow_html=True)
    flight_selected = st.multiselect(
        "",
        options=flight_opts,
        default=st.session_state.get("filter_flights", []),
        placeholder="Type or pick flight",
        key="flight_ms",
    )
    st.session_state["filter_flights"] = flight_selected

df = pivot_table(st.session_state.selected_table, date_choice, aircraft_selected, flight_selected)

if df.empty:
    st.warning("No Information")
    st.stop()

from utility import render_table_html

st.markdown(render_table_html(df), unsafe_allow_html=True)
