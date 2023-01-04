# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 15:17:14 2022

@author: Christelle
"""
import streamlit as st

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)

st.write("# Welcome to DisneyLand! 👋")

st.sidebar.success("Home")
#color = st.color_picker("Choose a background color")
#st.image('C:/Users/USER/Documents/Master_SISE/Projet/Text_mining/app/image.jpg')
st.image('image.jpg',width=600)

st.write("### Who we are? 🤔")

st.markdown(
    
    """
    Within the framework of the Text mining project of the Master 2 SISE, we had to analyze  
    tripadvisor information related to the evaluation of Internet users
of the Disneyland Paris Park. An interactive web application was requested to guide the exploration and analysis of the data.
   This is the homepage of ours Streamlit app. From here, you can navigate to different pages and perform various tasks.
   """
"""
In the page named data, you can scrape new data  👌.
The analysis page presents the different interesting analyses on the existing data in the database👊.
"""
)


names = ['Christelle Kiemdé', 'Martin schultz', 'Tho HOANG ', 'Pierre Dubrulle']

# Use st.write to print the names one by one
st.title("👏 project realized by 👏")
for name in names:
    st.write(name)





