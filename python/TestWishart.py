# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 17:03:42 2017

@author: komot
"""

import numpy as np 
import scipy.stats as ss

w = ss.wishart(df=3, scale=np.matrix([[1.0, 0.5], [0.5, 1.0]]))
print(w.rvs(10))
iw = ss.invwishart(df=3, scale=np.matrix([[1.0, 0.5], [0.5, 1.0]]))
print(iw.rvs(10))

w = ss.wishart(df=6, scale=np.matrix([[1.0, 0.5, 0, 0, 0], [0.5, 1.0, 0.5, 0, 0], [0, 0.5, 1.0, 0.5, 0], [0, 0, 0.5, 1.0, 0.5], [0, 0, 0, 0.5, 1.0]]))
print(w.rvs(10))
