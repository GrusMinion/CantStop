import streamlit as st
from cant_stop import CantStop
from cant_stop import Player
import matplotlib.pyplot as plt


def render_page():
    st.header('Create your Cant stop game')
    st.markdown('''Add players to the game by selecting a color and
                typing the players name. After all players have been
                added, start the game by pressing "play game"''')

    col1, col2, col3, col4, col5 = st.columns([2,1/2,1,1/2,2], gap = "small")

    with col1:
        name = st.text_input('Add player name',)
    with col2:
        st.write('')
    with col3:
        color = st.color_picker('Pick color')
    with col4:
        st.write('')
    with col5:
        computer = st.checkbox('Add Computer player', value = True)
        if st.button('Play game'):
            if computer:
                st.session_state.players.append(Player('Computer', '#000000'))
            st.session_state.start_game = True
            st.spinner('Building game and players, this may take a minute...')
            st.experimental_rerun()

            
    add_player_col = st.columns([4/3,4/3,4/3,2], gap = "small")[1]
    with add_player_col:
        if st.button('Add player'):
            if 'players' in st.session_state:
                st.session_state.players.append(Player(name, color))
            else:
                st.session_state.players = [Player(name, color)]
    
    player_list_col1, player_list_col2 = st.columns([4,0.5,0.25,1.5])[1:3]
        
    with player_list_col1:
        if 'players' in st.session_state:
            for player in st.session_state.players:
                name = player.name
                st.write(name)
                
    with player_list_col2:
        if 'players' in st.session_state:
            for player in st.session_state.players:
                fig, ax = plt.subplots()
                poly = plt.Polygon([[0, 0], [0,1], [1, 1], [1,0]], True, color = player.color)
                ax.add_line(poly)
                ax.axis('off')
                st.pyplot(fig)
                

            
    new_game_col = st.columns(3)[1]
    with new_game_col:
        if 'start_game' in st.session_state:
            if st.session_state.start_game:
                if st.button('New game'):
                    for k in st.session_state.keys():
                        del st.session_state[k]
                        st.experimental_rerun()

        
