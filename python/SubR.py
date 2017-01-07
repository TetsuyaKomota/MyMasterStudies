# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 21:27:16 2017

@author: komot
"""

from CRP import CRP

class SubR(CRP):
    def __init__(self, alpha):
        CRP.__init__(self, alpha)
        
    def call(self):
        print("This Restaurant's α :", end="")
        print(self.alpha)
        self.debug_show(17)