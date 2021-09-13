#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 14:36:52 2021

@author: richard
"""


import os
import pyarts
import matplotlib.pyplot as plt

types ="O2-TRE05", "O2-MPM2020", "AER"

sim_res = os.listdir('Output')

out = {}
for typ in types:
    out[typ] = ''

for fil in sim_res:
    for typ in types:
        if f"fgrid_{typ}" in fil:
            if out[typ] == '':
                out[typ] = fil
            else:
                if os.stat(f"Output/{out[typ]}").st_ctime < os.stat(f"Output/{fil}").st_ctime:
                    out[typ] = fil

for typ in types:
    assert out[typ] != '', "Didn't find some of the requires data!"

plt.figure(1)
plt.clf()
for typ in types:
    f = pyarts.xml.load(f"Output/{out[typ]}")
    y = pyarts.xml.load(f"Output/{out[typ].replace(f'fgrid_{typ}_', f'iy_{typ}_midlat-s_')}")
    plt.plot(f, y, label=typ)
plt.legend()
plt.show()
