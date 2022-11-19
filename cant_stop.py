#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 14:28:20 2022

@author: manuel
"""
import numpy as np
import itertools
import streamlit as st
from collections import Counter
from collections.abc import Iterable

class CantStop(object):
    initialized = False
    unique_options = []
    expected_num_per_throw = {}
    # the "init" function is called when the instance is
    # created and ready to be initialized
    def __init__(self):
        if not self.initialized:
            self.NUMBERS = np.array(range(2,13))
            self.STEPS_PER_NUMBER = dict(zip(self.NUMBERS, np.concatenate((np.linspace(3,13,6), np.linspace(11,3,5)))))
            # generate all possible outcomes for a throw with 4 dices
            self.all_outcomes = [[i, j, k, l] for i in range(1,7) for j in range(1,7) for k in range(1,7) for l in range(1,7)]
    
            # total number of outcomes
            self.num_outcomes = len(self.all_outcomes)
    
            # determine the combinations that you can make given the outcome of the dice
            # that you have. Given that each of outcomes in "all_outcomes" is equally
            # likely, we can use this to determine the probabilty of obtaining a number
            # 2-12 in a single throw
            self.options = [[np.sort([throws[0] + throws[1], throws[2] + throws[3]]), \
                    np.sort([throws[0] + throws[2], throws[1] + throws[3]]), \
                    np.sort([throws[0] + throws[3], throws[1] + throws[2]])] for throws in self.all_outcomes]
        
            # remove doubles (i.e. [3, 7] is the same as [7, 3])    
            self.options  = [[list(y) for y in set([tuple(x) for x in self.options[i]])] for i in range(len(self.options))]
        
            # remove non-unique combinations of throws
            self.unique_options = [np.unique(self.options[i]) for i in range(self.num_outcomes)]
        
            # calculate the chance of obtaining at least once each of the numbers 2-12 with
            # a single throw
            # chance_per_num contains the chance of being able to make the combination "n"
            # in a throw with 4 dices at least once    
            self.chance_per_num = {}
            for n in self.NUMBERS:
                count = 0
                for i in range(self.num_outcomes):
                    if n in self.unique_options[i]:
                        count += 1
                chance = count / self.num_outcomes
                self.chance_per_num.update({n : chance})
        
            # now calculate the chance to obtain a number twice with a single throw
            self.chance_twice_num = {}
            for n in self.NUMBERS:
                count = 0
                for i in range(self.num_outcomes):
                    if n in self.unique_options[i]:
                        for doubles in self.options[i]:
                            if doubles[0] == n and doubles[1] == n:
                                count += 1
                chance = count / self.num_outcomes
                self.chance_twice_num.update({n : chance})
        
            # and together with the chance to obtain a number at least once, obtain the
            # chance of exactly once.
            self.chance_once_num = {}
            # chance_once_num = {key: value for (key, value) in iterable}
            for key in self.chance_per_num.keys():
                chance = self.chance_per_num[key] - self.chance_twice_num[key]
                self.chance_once_num.update({key : chance})
        
        
            # there are in total 165 combinations of 3 numbers you can choose out of the
            # numbers 2-12. Once you have chosen these 3 numbers, there is a chance that
            # you will not throw any of these as the sum of 2 dices
            self.possible_combs_chosen = [list(comb) for comb in itertools.combinations(self.NUMBERS, 3)]
        
            # determine now the chance of throwing at least one number 
            self.chance_per_comb = {}
            for comb in self.possible_combs_chosen:
                count = 0
                for i in range(self.num_outcomes):
                    if any([t in self.unique_options[i] for t in comb]):
                        count += 1
                chance = count / self.num_outcomes
                self.chance_per_comb.update({tuple(comb) : chance})
        
            # calculate the expected number of throws that you need to obtain the required
            # number of (remaining?) steps in each of the numbers 2-12
            # or put differently: the expected number of times to throw numbers 2-12. 
            # number of remaining steps divided by expected number of times to throw the
            # number is the expected number of remaining throws required
            self.expected_num_per_throw = {}
            for key in self.chance_per_num.keys():
                num = 2*self.chance_twice_num[key] + self.chance_once_num[key]
                self.expected_num_per_throw.update({key : num})
            
            self.initialized = True


class Player:
    def __init__(self, name, color):
        self.game_setup = CantStop()
        self.unique_options = self.game_setup.unique_options
        self.expected_num_per_throw = self.game_setup.expected_num_per_throw
        self.NUMBERS = [i for i in range(2,13)]
        self.STEPS_PER_NUMBER = dict(zip(self.NUMBERS, np.concatenate((np.linspace(3,13,6), np.linspace(11,3,5))).tolist()))
        self.name = name
        self.color = color
        self.positions = dict(zip(self.NUMBERS, [0 for i in range(len(self.NUMBERS))]))
        self.temp_positions = dict(zip(self.NUMBERS, [0 for i in range(len(self.NUMBERS))]))
    
    def __eq__(self, other):
        if isinstance(other, Player):
            return self.color == other.color and self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        eq = Player.__eq__(self, other)
        return NotImplemented if eq is NotImplemented else not eq
        
    def moveposition(self, move = None, failed = None, finished = None):
        if failed:
            self.temp_positions = dict(zip(self.NUMBERS, [0 for i in range(len(self.NUMBERS))]))
        elif finished:
            for key in self.temp_positions:
                if self.temp_positions[key] > 0:
                    self.positions[key] = self.temp_positions[key]
                    self.temp_positions[key] = 0
        elif move:
            if isinstance(move, Iterable):
                for val in move:
                    if self.temp_positions[val] > self.positions[val]:
                        self.temp_positions[val] += 1
                    else:
                        self.temp_positions[val] = self.positions[val] + 1
            else:
                val = move
                if self.temp_positions[val] > self.positions[val]:
                    self.temp_positions[val] += 1
                else:
                    self.temp_positions[val] = self.positions[val] + 1


    def throwdice(self, ignore = []):
        throws = np.random.randint(1,6,4).tolist()
        throw_str = "Player '{0}' has thrown ".format(self.name) + ', '.join(map(str,throws[:-1])) + " and {0}".format(throws[-1])
        
        # generate all 2-pair combinations with 4 dice
        options = [list(np.sort([throws[0] + throws[1], throws[2] + throws[3]])), \
                list(np.sort([throws[0] + throws[2], throws[1] + throws[3]])), \
                list(np.sort([throws[0] + throws[3], throws[1] + throws[2]]))]
        
        # remove non-unique combinations of throws
        options = list(set(tuple(sorted(sub)) for sub in options))
        
        for key, value in self.temp_positions.items():
            if value == self.STEPS_PER_NUMBER[key]:
                ignore.append(key)
        
        num_steps_tempos = np.fromiter(self.temp_positions.values(), dtype = int)

        
        single_options = []
        
        options_copy = options[:]
        for val in options_copy:
            if any([x in ignore for x in val]):
                options.remove(val)
                for single_val in val:
                    if not single_val in ignore:
                        if self.temp_positions[single_val] > 0 or sum(num_steps_tempos > 0) <= 2:
                            single_options.append([single_val])

        options_copy = options[:]
        for val in options_copy:
            if val[0] == val[1]:
                if self.temp_positions[val[0]] > 0 or sum(num_steps_tempos > 0) <= 2:
                    if self.temp_positions[val[1]] + 1 == self.STEPS_PER_NUMBER[val[1]]:
                        options.remove(val)
                        single_options.append([val[1]])
                        
        options_copy = options[:]
        for val in options_copy:
            if sum(num_steps_tempos > 0) + sum([self.temp_positions[ind] == 0 for ind in val]) > 3:
                options.remove(val)
                if sum(num_steps_tempos > 0) + int(self.temp_positions[val[0]] == 0) <= 3:
                    single_options.append([val[0]])
                if sum(num_steps_tempos > 0) + int(self.temp_positions[val[1]] == 0) <= 3:   
                    single_options.append([val[1]])

        for single_val in single_options:
            options.append(single_val)      
        
        options = list(set(tuple(sorted(sub)) for sub in options))
        
        return options, throw_str
    
    def calc_chance_after(self, choice, ignore):
        num_steps_tempos = np.fromiter(self.temp_positions.values(), dtype = int)

        viable_numbers = choice[:]
        for key in self.temp_positions:
            if key not in ignore and key not in viable_numbers:
                if self.temp_positions[key] > 0:
                    if self.temp_positions[key] < self.STEPS_PER_NUMBER[key]:
                        viable_numbers.append(key)
                elif sum(num_steps_tempos > 0) + sum([self.temp_positions[i] == 0 for i in choice]) < 3:
                    viable_numbers.append(key)
                    
        positive_outcomes = 0
        for throw_options in self.unique_options:
            for num in viable_numbers:
                if num in throw_options:
                    positive_outcomes += 1
                    break
        
        chance_after = positive_outcomes/len(self.unique_options)
        
        return chance_after
    
    
    def AI(self, moves = None, ignore = None):
  
        num_steps_tempos = np.fromiter(self.temp_positions.values(), dtype = int)
        
        # average expected throws remaining for each move option
        avg_E_throws = dict()
        for val in moves:
            avg_E_throws[tuple(val)] = 0
            for sing_val in val:
                steps_remain = self.STEPS_PER_NUMBER[sing_val] - max(self.temp_positions[sing_val], self.positions[sing_val])
                steps_per_throw = self.expected_num_per_throw[sing_val]
                avg_E_throws[tuple(val)] += (steps_remain/steps_per_throw)/len(val)

        choice = list(min(avg_E_throws, key=avg_E_throws.get))
        chance_after = self.calc_chance_after(choice, ignore)
        
        num_victories = sum([max(self.temp_positions[key], self.positions[key]) == self.STEPS_PER_NUMBER[key] for key in self.positions])
        
        if len(choice) > 1:
            if choice[0] == choice[1]:
                key = choice[0]
                num_victories += int(max(self.temp_positions[key], self.positions[key]) + 2 == self.STEPS_PER_NUMBER[key])
                
        for key in choice:
            num_victories += int(max(self.temp_positions[key], self.positions[key]) + 1 == self.STEPS_PER_NUMBER[key])
        
        if chance_after == 1:
            keep_going = True
        elif num_victories >= 3:
            keep_going = False
        else:
            current_pos = np.fromiter(self.positions.values(), dtype = int)
            num_temp_steps = sum(num_steps_tempos) - sum(current_pos[num_steps_tempos > 0])
            num_current_steps = len(choice)
            expected_remaining_steps = 1/(1-chance_after)
            if num_temp_steps + num_current_steps > expected_remaining_steps:
                keep_going = False
            else:
                keep_going = True
        
        return choice, keep_going

