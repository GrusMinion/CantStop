#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 18:49:55 2022

@author: manuel
"""


import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import time
# import tkinter as tk
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.patches import Patch
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotBoard:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.axis('off')
        poly = plt.Polygon([[0, 5/12], [0, 7/12], [1/2, 1], [1, 7/12], [1, 5/12], [1/2, 0], [0, 5/12]], True, alpha = 0.5)
        self.ax.add_line(poly)
        x_step = 1/11
        y_step = 1/12
        self.nums = np.array(range(2,13))
        self.steps_per_num = np.concatenate((np.linspace(3,13,6), np.linspace(11,3,5)))
        self.points = [[i*x_step + 1/22, (j + (13-self.steps_per_num[i]) / 2) * y_step] \
                  for i in range(11) for j in range(int(self.steps_per_num[i]))]
        self.ax.scatter([x[0] for x in self.points], [y[1] for y in self.points], c = '#1f77b4')
        self.ax.set_facecolor(color = '#000000')
        
        
        self.dict_keys = [(val1, val2+1) for val1 in self.nums for val2 in range(int(self.steps_per_num[val1-2]))]
        self.position_coordinates = dict(zip(self.dict_keys, self.points))
        
        st.pyplot(self.fig)
        
        
        
    def plot_players(self, players):
        
        self.ax.scatter([x[0] for x in self.points], [y[1] for y in self.points], c = '#1f77b4')
        
        temp_coordinates = []
        for player in players:
            player_coordinates = []
            for position in player.temp_positions:
                value = player.temp_positions[position]
                if (position, value) in self.dict_keys and value > 0:
                    temp_coordinates.append(self.position_coordinates[(position, value)])
        
            for position in player.positions:
                value = player.positions[position]
                if (position, value) in self.dict_keys and value > 0:
                    player_coordinates.append(self.position_coordinates[(position, value)])
            
            # plot the fixed positions (colored)
            if player_coordinates:
                self.ax.scatter([x[0] for x in player_coordinates], [x[1] for x in player_coordinates], c = player.color)
                
        # plot the temp-positions (white)            
        if temp_coordinates:
            self.ax.scatter([x[0] for x in temp_coordinates], [x[1] for x in temp_coordinates], c = '#ffffff')
            
        

