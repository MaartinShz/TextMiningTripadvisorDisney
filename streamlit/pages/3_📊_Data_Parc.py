# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 15:51:05 2022

@author: Christelle
"""

import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Chargement des données", page_icon="📈")

st.markdown("# Chargement des données")
st.sidebar.header("Chargement des données")
st.write(
    """Ici, nous pouvons recuperer les commentaires des internautes sur les parc, hotel de DisneyLand"""
)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
chart = st.line_chart(last_rows)

for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0.05)

progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")