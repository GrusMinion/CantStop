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
        throws = np.random.random_integers(1,6,4).tolist()
        throw_str = "Player '{0}' has thrown ".format(self.name) + ', '.join(map(str,throws[:-1])) + " and {0}".format(throws[-1])
        
        # generate all 2-pair combinations with 4 dice
        options = [np.sort([throws[0] + throws[1], throws[2] + throws[3]]).tolist(), \
                np.sort([throws[0] + throws[2], throws[1] + throws[3]]).tolist(), \
                np.sort([throws[0] + throws[3], throws[1] + throws[2]]).tolist()]
        
        # remove non-unique combinations of throws
        options = [list(y) for y in set([tuple(x) for x in options])]
        
        num_steps_tempos = np.fromiter(self.temp_positions.values(), dtype = int)
        
        for val in reversed(options):
            if (val[0] in ignore or val[1] in ignore) and val in options:
                options.remove(val)
            elif val[0] == val[1] and self.temp_positions[val[0]] + 1 == self.STEPS_PER_NUMBER[val[0]]:
                options.remove(val)
            elif self.temp_positions[val[1]] >= self.STEPS_PER_NUMBER[val[1]]:
                options.remove(val)
            elif self.temp_positions[val[0]] >= self.STEPS_PER_NUMBER[val[0]]:
                options.remove(val)
            elif self.temp_positions[val[0]] > 0 and self.temp_positions[val[1]] > 0:
                # both numbers are already selected, continue
                continue
            elif self.temp_positions[val[0]] > 0 and sum(num_steps_tempos > 0) < 3:
                # one number is already selected and there is at least one position left
                continue
            elif self.temp_positions[val[1]] > 0 and sum(num_steps_tempos > 0) < 3:
                # same, other number
                continue 
            elif sum(num_steps_tempos > 0) < 2:
                # there are at least 2 more positions left
                continue
            else:
                # otherwise, remove the value...
                options.remove(val)
            
                
        # add single values
        single_values = [throws[0] + throws[1], throws[0] + throws[2], throws[0] + throws[3],\
                          throws[1] + throws[2], throws[1] + throws[3], throws[2] + throws[3]]
        
        for val in single_values:
            if not val in options and not val in ignore:
                if self.positions[val] < self.STEPS_PER_NUMBER[val] and self.temp_positions[val] < self.STEPS_PER_NUMBER[val]:
                    if self.temp_positions[val] > 0:
                        # the position is already chosen
                        options.append(val)
                    elif sum(num_steps_tempos > 0) < 3:
                        # there is at least 1 free position
                        options.append(val)
        
        return options, throw_str
    
    def calc_chance_per(self, val_s, ignore):
        num_steps_tempos = np.fromiter(self.temp_positions.values(), dtype = int)
        
        chance_after = dict()
        for val in val_s:
            if isinstance(val, list):
                viable_numbers = val[:]
                nums = len(val)
            else:
                viable_numbers = [val]
                nums = 1
            for key in self.temp_positions:
                if key not in ignore and key not in viable_numbers:
                    if self.temp_positions[key] > 0:
                        if self.temp_positions[key] < self.STEPS_PER_NUMBER[key]:
                            viable_numbers.append(key)
                    elif sum(num_steps_tempos > 0) < 4 - nums:
                        viable_numbers.append(key)
                        
            positive_outcomes = 0
            for throw_options in self.unique_options:
                for num in viable_numbers:
                    if num in throw_options:
                        positive_outcomes += 1
                        break
            
            # 'chance_after' gives the chance that you survive another dice-throw
            # if you choose to now take a step in a direction of val
            if isinstance(val, list):
                chance_after[tuple(val)] = positive_outcomes/len(self.unique_options)
                if positive_outcomes > len(self.unique_options):
                    print('something is wrong')
            else:
                chance_after[val] = positive_outcomes/len(self.unique_options)
                if positive_outcomes > len(self.unique_options):
                    print('something is wrong')
                        
        return chance_after
    
    
    def AI(self, moves = None, ignore = None):
        keep_going = False
        choice = []

        single_vals = [val for val in moves if isinstance(val, int)]
        double_vals = [val for val in moves if isinstance(val, list)]
        
        num_steps_tempos = np.fromiter(self.temp_positions.values(), dtype = int)

        expected_throws_remaining = dict()
        for val in self.temp_positions:
            steps_remain = self.STEPS_PER_NUMBER[val] - max(self.temp_positions[val], self.positions[val])
            steps_per_throw = self.expected_num_per_throw[val]
            expected_throws_remaining[val] = steps_remain/steps_per_throw
        
        first_val = 0
        throws_for_val = max(expected_throws_remaining.values())
        for key in self.temp_positions:
            if expected_throws_remaining[key] <= throws_for_val and key in single_vals:
                temp = key
                if expected_throws_remaining[key] > 0:
                    first_val = key
                    throws_for_val = expected_throws_remaining[key]
        
        if first_val == 0:
            first_val = temp
            print('something is wrong')
        
        if double_vals:
            for val in double_vals:
                if val[0] == val[1]:
                    steps_remain = self.STEPS_PER_NUMBER[val[0]] - self.temp_positions[val[0]] - 1
                    steps_per_throw = self.expected_num_per_throw[val[0]]
                    expected_throws_remaining[val[0]] = steps_remain/steps_per_throw
            
            max_required_throws = 0
            for val in self.temp_positions:
                if (self.temp_positions[val] > 0 or self.positions[val] > 0) and \
                    expected_throws_remaining[val] > max_required_throws:
                        max_required_throws = expected_throws_remaining[val]
            
            for val in double_vals:
                if not choice:
                    if (val[0] == first_val and self.temp_positions[val[1]] > 0) or \
                    (val[1] == first_val and self.temp_positions[val[0]] > 0):
                        choice = val
                if val[0] == first_val and expected_throws_remaining[val[1]] < max_required_throws:
                    choice = val
                elif val[1] == first_val and expected_throws_remaining[val[0]] < max_required_throws:
                    choice = val
        
        if single_vals:
            all_options = single_vals[:]
        else:
            all_options = []
        if choice:
            all_options.append(choice)
            
        chance_after = self.calc_chance_per(all_options, ignore)
        
        if not choice:
            choice = first_val
            num_steps = 1
            if not chance_after[choice] == 1:
                expected_remaining_steps = 1/(1-chance_after[choice])
            else:
                keep_going = True
        else:
            if not chance_after[tuple(choice)] == 1:
                expected_remaining_steps = 1/(1-chance_after[tuple(choice)])
            else:
                keep_going = True
            num_steps = 2
        
        current_pos = np.fromiter(self.positions.values(), dtype = int)
        num_temp_steps = sum(num_steps_tempos) - sum(current_pos[num_steps_tempos > 0])
        if keep_going:
            keep_going = True
        elif num_temp_steps + num_steps > expected_remaining_steps:
            keep_going = False
        else:
            keep_going = True
        
        return choice, keep_going
        
