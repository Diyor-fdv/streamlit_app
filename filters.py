import streamlit as st
from mock_data import distinct_aircraft as _da, distinct_flights as _df


@st.cache_data(ttl=60)
def distinct_aircraft(date_choice: str, chosen_flights: list) -> list:
    return _da(date_choice, chosen_flights)


@st.cache_data(ttl=60)
def distinct_flights(date_choice: str, chosen_aircraft: list) -> list:
    return _df(date_choice, chosen_aircraft)
