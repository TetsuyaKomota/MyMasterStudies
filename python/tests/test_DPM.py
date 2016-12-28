# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 18:02:40 2016

@author: komot
"""
import unittest
import DPM
import GMMv2
import numpy as np

class TestDPM(unittest.TestCase):
    
    def setUp(self):
        print("set up")
        self.dpm = DPM.DPM()
        c = 3
        means = [[0, 0], [-10, -10], [5, 10]]
        sigmas = [[[1, 0], [0, 1]], [[1, 0.5], [0.5, 1]], [[1, 0], [0, 2]]]
        rates = [0.3, 0.4, 0.3]
        size = 100
        self.data = GMMv2.getData(c, means, sigmas, rates, size)
        
    def test_getPartialParam(self):
        x = [np.array([1, 2]), np.array([2, 4]), np.array([3, 6]), np.array([4, 10]), np.array([5, 11]), np.array([6, 12])]
        l = [0, 0, 0, 1, 1, 1]        
        self.dpm.input(x)
        self.dpm.setLabel(l)
        
        result = self.dpm.getPartialParam(0)   
        print(result)
        self.assertEqual(np.allclose(result[0], np.array([2, 4])), True)
        self.assertEqual(np.allclose(result[1], np.array([[1, 2], [2, 4]])), True)
        
    def test_mnd(self):
        self.assertEqual(self.dpm.mnd(0, 0, 1) , 0.3989422804014327)

    def tearDown(self):
        print("tear Down")        