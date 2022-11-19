#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 18:49:55 2022

@author: manuel
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
# import tkinter as tk
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.patches import Patch
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotBoard:
    def __init__(self):
        nums = np.array(range(2,13))
        
        data = [[0, 5/12], [0, 7/12], [1/2, 14/13], [1, 7/12], [1, 5/12], [1/2, -1/13], [0, 5/12]]
        x_vals = [x[0] for x in data]
        y_vals = [x[1] for x in data]
        index_vals = [i for i in range(len(data))]
  
        end_points = pd.DataFrame(dict(index = index_vals, x = x_vals, y = y_vals))
        
        line_chart = alt.Chart(end_points).mark_line().encode(
            alt.X('x', axis = None),
            alt.Y('y', axis = None),
            order='index')

        x_step = 1/11
        y_step = 1/12
        steps_per_num = np.concatenate((np.linspace(3,13,6), np.linspace(11,3,5)))

        points = [[i*x_step + 1/22, (j + (13-steps_per_num[i]) / 2) * y_step] \
                  for i in range(11) for j in range(int(steps_per_num[i]))]
        self.dict_keys = [(val1, val2+1) for val1 in nums for val2 in range(int(steps_per_num[val1-2]))]
        self.position_coordinates = dict(zip(self.dict_keys, points))
        scatter_points = pd.DataFrame(dict(x_vals = [x[0] for x in points], y_vals = [x[1] for x in points]))

        point_chart = alt.Chart(scatter_points).mark_circle(filled=True, size = 180, color = '#1f77b4').encode(
            alt.X('x_vals',scale = alt.Scale(domain=(-1/13, 14/13))),y='y_vals')

        self.base_chart = (line_chart + point_chart).properties(width=800,height=700)
        self.plot_chart = self.base_chart.configure(background='#FFFFFF')
        self.plot_chart.configure_view(strokeWidth=0).configure_axis(grid=False, domain=False)
        
                
    def plot_players(self, players):
        
        new_chart = alt.LayerChart()
        
        temp_coordinates = []
        for player in players:
            player_coordinates = []
            for position in player.temp_positions:
                value = player.temp_positions[position]
                
                if (position, value) in self.dict_keys and value > 0:
                    temp_coordinates.append(self.position_coordinates[(position, value)])
                    
                value = player.positions[position]
                if (position, value) in self.dict_keys and value > 0:
                    player_coordinates.append(self.position_coordinates[(position, value)])
                    
            # plot the fixed positions (colored)
            if player_coordinates:
                scatter_points = pd.DataFrame(dict(x_vals = [x[0] for x in player_coordinates], y_vals = [x[1] for x in player_coordinates]))
                new_chart += alt.Chart(scatter_points).mark_circle(filled=True, size = 160, color = player.color).encode(x='x_vals',y='y_vals')
                
        # plot the temp-positions (white)            
        if temp_coordinates:
            scatter_points = pd.DataFrame(dict(x_vals = [x[0] for x in temp_coordinates], y_vals = [x[1] for x in temp_coordinates]))
            new_chart += alt.Chart(scatter_points).mark_circle(filled=True, size = 160, color = '#ffffff').encode(x='x_vals',y='y_vals')

        
        self.plot_chart = (self.base_chart + new_chart).configure(background='#FFFFFF')
        self.plot_chart.configure_view(strokeWidth=0).configure_axis(grid=False, domain=False)
