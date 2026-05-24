import streamlit as st
import pandas as pd
from card import card

df = pd.read_csv("pg_catalog.csv")

# Page entière
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.logo("Logo.svg", size="large", icon_image="Logo.svg")
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Sidebar
st.sidebar.header("NLP Bookstore")
book = st.sidebar.selectbox("Choose a book", df["Title"])
interface = st.sidebar.selectbox("Interface", ["User-Friendly", "Developer"])

if interface == "User-Friendly":
    # Première ligne
    st.markdown("## About this book")
    c1, space, c2 = st.columns((3, 0.5, 7))

    with c1:
        book_id = df[df["Title"] == book]["Text#"].iloc[0]
        cover_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
        st.image(cover_url)

    with c2:
        data = card(book_id)

        st.markdown("#### Title")
        st.write(book)
        st.markdown("---")

        st.markdown("#### Author")
        st.write(data["info"]["author"])
        st.markdown("---")

        st.markdown("#### Bookshelves")
        bookshelves = data["info"]["bookshelves"].split(";")
        cleaned_bookshelves = set()
        for bookshelve in bookshelves:
            bookshelve = bookshelve.replace("Category: ", "")
            bookshelve = bookshelve.strip()
            cleaned_bookshelves.add(bookshelve)
        cols = st.columns(3)
        for i, genre in enumerate(sorted(list(cleaned_bookshelves))):
            cols[i % 3].markdown(f"- {genre}")

    # Deuxième ligne
    st.markdown("## Characters")
    st.markdown("""
        <style>
        .card {
            position: relative;
            padding: 12px 0px 12px 20px;
            margin: 10px 0px 10px 0px;
            border: 2px solid rgb(38, 39, 48);
            border-radius: 8px;
            overflow: hidden;
        }

        .card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;

            background: linear-gradient(
                to bottom,
                #0051a2,
                #45a1f7,
                #ffffff
            );
        }
        </style>
        """, unsafe_allow_html=True)

    cols = st.columns(3)
    characters = data["entities"]["characters"]
    for i, character in enumerate(characters):
        cols[i % 3].markdown(f"""
        <div class=card>
            {character}
        </div>
        """, unsafe_allow_html=True)

    # Troisième ligne
    st.markdown("## Locations")
    cols = st.columns(3)
    locations = data["entities"]["locations"]
    for i, location in enumerate(locations):
        cols[i % 3].markdown(f"""
        <div class=card>
            {location}
        </div>
        """, unsafe_allow_html=True)
    
    # Quatrième ligne
    st.markdown("## Similar books")
    cols = st.columns(5)
    sim_books = data["similar"]
    i=0
    for sim_book in sim_books:
        sim_book_id = df[df["Title"] == sim_book]["Text#"].iloc[0]

        cols[i].image(f"https://www.gutenberg.org/cache/epub/{sim_book_id}/pg{sim_book_id}.cover.medium.jpg")

        i+=1

if interface == "Developer":
    # Première ligne
    book_id = df[df["Title"] == book]["Text#"].iloc[0]
    data = card(book_id)
    st.json(data)
