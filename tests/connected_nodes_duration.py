#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 12:27:24 2022

@author: lpeurey
"""
import pandas as pd
import random
import numpy as np
import time

from conversations.conversation import Conversation

np.random.seed(2424) #usage of a seed allows for consistency in generated dataframes
onsets = np.random.randint(10e5, size=1000) #generate random onsets, maximum being 10e5 (so this represents an audio of ~1000s so around 17min)
durations = np.random.randint(10e3, size=1000) #generate random durations, meximum duration being 10s

offsets = onsets + durations

segments = pd.DataFrame({'segment_onset': onsets,
                        'segment_offset':offsets,
                        })
segments['name']= segments.index
segments['speaker_type']= 'CHI'

segments.sort_values('segment_onset', inplace=True)

cv = Conversation(allow_segment_jump=True)

start = time.time()
connected_nodes = cv._find_connected_nodes(segments)
stop = time.time()

print("finding connected nodes took {}s".format(stop - start))