#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 21:10:57 2022

@author: manuel
"""
# from io import StringIO
import streamlit as st
from plot_game_board import PlotBoard
import time
# import numpy as np
import random
# from cant_stop import CantStop


def render_page():
    
    if not 'victory' in st.session_state:
        st.session_state.victory = False
        st.header('Now play the game!')
    elif st.session_state.victory:
        st.header('The game is over, {0} has won'.format(st.session_state.winner))
        st.session_state.end_turn = False
        st.session_state.dice_thrown = False
    else:
        st.header('Now play the game!')
    
    if not 'current_ind' in st.session_state:
        random_player = random.choice(st.session_state.players)
        st.session_state.current_ind = st.session_state.players.index(random_player)
        st.session_state.end_turn = False
        
    if not 'board_placeholder' in st.session_state:
        st.session_state.board_placeholder = st.empty()
        
    if not 'rolldice_placeholder' in st.session_state:
        st.session_state.rolldice_placeholder = st.empty()
        
    if not 'endturn_placeholder' in st.session_state:
        st.session_state.endturn_placeholder = st.empty()
    
    if not 'options_placeholder' in st.session_state:
        st.session_state.options_placeholder = st.empty()
    
    if not 'ignore_list' in st.session_state:
        st.session_state.ignore_list = []
        
    if not 'dice_thrown' in st.session_state:
        st.session_state.dice_thrown = False
        
    if not 'board_fig' in st.session_state:
        with st.session_state.board_placeholder.container():
            current_player_name = st.session_state.players[st.session_state.current_ind].name
            st.markdown('''The current player is {0}'''.format(current_player_name))
            with st.columns([1/2,3,1/2])[1]:
                st.session_state.board_fig = PlotBoard()
                st.altair_chart(st.session_state.board_fig.plot_chart, use_container_width=True)
    else:
        update_game_board()
        
    if st.session_state.players[st.session_state.current_ind].name == 'Computer':
        while not st.session_state.end_turn and not st.session_state.victory:
            throw_dice()
            if not st.session_state.players[st.session_state.current_ind].name == 'Computer':
                update_game_board()
                break
            # if st.session_state.end_turn and st.button("Next player"):
            #     st.session_state.dice_thrown = True

    
    with st.session_state.rolldice_placeholder.container():
        st.button('Roll dice', on_click = throw_dice, disabled = st.session_state.dice_thrown)
    with st.session_state.endturn_placeholder.container():
        if not st.session_state.dice_thrown:
            if not st.session_state.end_turn:
                st.button('End turn', on_click = end_turn, disabled = st.session_state.victory)


def throw_dice():
    # throw the dice for the current player
    player = st.session_state.players[st.session_state.current_ind]
    # the player has decided to throw the dice
    st.session_state.dice_thrown = True
    options, dice_roll_text = player.throwdice(ignore = st.session_state.ignore_list)
    with st.session_state.options_placeholder.container():
        st.write(dice_roll_text)
        if not options:
            st.write('''This dice roll does not allow any combinations... {0} is dead'''.format(player.name))
            time.sleep(1)
            # st.session_state.end_turn = True
            st.session_state.players[st.session_state.current_ind].moveposition(failed = True)
            next_player()

        elif player.name == 'Computer' and options:
            choice, keep_going = player.AI(moves = options, ignore = st.session_state.ignore_list)
            st.write('''Computer chooses steps {0}'''.format(choice))
            time.sleep(1)
            move_position(choice)
            time.sleep(1)
            if not keep_going:
                end_turn()
        else:
            for opt in options:
                print(opt)
            cols = st.columns(len(options))
            for ind, option in enumerate(options):
                with cols[ind]:
                    st.button(label = '''Select {0}'''.format(option), on_click = move_position, args = (option,))
                      
def move_position(option):
    st.session_state.players[st.session_state.current_ind].moveposition(move = option)
    st.session_state.dice_thrown = False
    update_game_board()
        
def end_turn():
    ind = st.session_state.current_ind
    
    # update session state parameters
    st.session_state.players[ind].moveposition(finished = True)
    st.session_state.dice_thrown = False
    st.session_state.end_turn = True
    
    # remove values of other players if current player has reached the limit
    for player in st.session_state.players:
        player_ind = st.session_state.players.index(player)
        for key in player.positions:
            if st.session_state.players[ind].positions[key] == player.STEPS_PER_NUMBER[key]:
                st.session_state.ignore_list.append(key)
                if not player_ind == ind:
                    st.session_state.players[player_ind].positions[key] = 0

    update_game_board()
    check_victory()
    if not st.session_state.victory:
        next_player()
        
def update_game_board():
    with st.session_state.board_placeholder.container():
        current_player_name = st.session_state.players[st.session_state.current_ind].name
        st.markdown('''The current player is {0}'''.format(current_player_name))
        with st.columns([1/2,3,1/2])[1]:
            st.session_state.board_fig.plot_players(st.session_state.players)
            st.altair_chart(st.session_state.board_fig.plot_chart, use_container_width=True)            
            # st.pyplot(st.session_state.board_fig.fig)

def next_player():
    st.session_state.current_ind = (st.session_state.current_ind + 1) % len(st.session_state.players)
    st.session_state.end_turn = False
    st.session_state.dice_thrown = False
            
def check_victory():
    for player in st.session_state.players:
        count = 0
        for key in player.positions:
            if player.positions[key] == player.STEPS_PER_NUMBER[key]:
                count += 1
            if count >= 3:
                st.session_state.victory = True
                st.session_state.winner = player.name
        
