import streamlit as st
from fonctions.connection_bdd import statistics
from fonctions.async_scrap import *
from PIL import Image


m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(204, 49, 49);
    font-size: 24px;
    padding: 24px 60px;
    font-weight: bold;
}
</style>""", unsafe_allow_html=True)

st.markdown('# Mise à jour de la base de données')

total, total_site, some_comments, years_hotel, years_parc = statistics()
icon = Image.open('./base-de-donnees.png')
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.image(icon)
    with col2:
        st.write(f'Il y a actuellement : {total} commentaires dans la base de données.')
        for x in total_site:
            st.write(f"{x['_id']} : {x['count']}")

for x in some_comments:
        st.markdown(f'## {x["Auteur"]} a mis {x["Note"]}⭐️')
        # st.markdown(f'### Note de {x["Note"]}⭐️')
        st.write(f'le {x["Date_commentaire"]}')
        st.write(f'{x["Commentaire"]}')
