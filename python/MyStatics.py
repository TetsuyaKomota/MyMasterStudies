# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 21:34:38 2016

@author: komot
"""

import numpy as np

ALPHA=1.0
BETA=1/3
DF=15
SCALE=np.matrix([[0.1, 0], [0, 0.1]])

# DPM の繰り返しにおける 非更新回数限界
MAX_ITER_NON = 30