import streamlit as st
import pages.start_game
import pages.play_game
# from functools import partial

st.set_page_config(
    page_title='Cant stop boardgame',
    layout='wide',
    menu_items={'About': '''Application written by Manuel Bastin'''
    }
)

start_game = 'start_game' in st.session_state
st.session_state.new_game = False

available_pages = {  ## pages while creating a new game
    'Create a game': pages.start_game.render_page
}


if start_game:
    available_pages = {  ## pages after creating a new game
        'Play game': pages.play_game.render_page,
        'Create a game': pages.start_game.render_page
    }
    
previous_page_selected = st.session_state.get('previous_page_selected', None)

st.sidebar.title("Navigation")
page_selected = st.sidebar.radio(
    "Go to",
    list(available_pages.keys())
)




available_pages[page_selected]()  ## call dict-value function
