#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 14:36:52 2021

@author: richard
"""

def main():
    import os
    import pyarts
    import matplotlib.pyplot as plt

    types ="O2-TRE05", "O2-MPM2020", "O2-AER"

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


def plot_any_range(xmldata, start=5, end=500):
    """
    min start=5, max end=500 GHz
    two plots absolute Tbs and diffs
    """
    import matplotlib.pyplot as plt

    vocab = list(xmldata.keys())
    iy = list()
    for keys in xmldata.keys():
        iy.append(xmldata[keys][2])
    fgrid = xmldata[keys][-1]


    # Apply mask to subselect fgrid 50-60 GHz
    mmask = (fgrid > start) & (fgrid < end)
    fgrid = fgrid[mmask]
    b = list()
    for f in iy:
        b.append(f[mmask])
    iy = b.copy()

    fig, ax = plt.subplots()
    ax.plot(fgrid, iy[0], label=vocab[0][3:])  # TRE05
    ax.plot(fgrid, iy[1], label=vocab[1][3:])  # AER
    ax.plot(fgrid, iy[2], label=vocab[2][3:])  # MPM2020
    ax.set_xlabel('Frequency, GHz')  # ,  fontsize = 12)
    ax.legend()
    plt.show()

    fig2, ax2 = plt.subplots()
    ax2.plot(fgrid, iy[2] - iy[0], label='MPM-TRE05')
    ax2.plot(fgrid, iy[1] - iy[0], label='AER-TRE05')
    ax2.set_xlabel('Frequency, GHz')  # ,  fontsize = 12)
    ax2.legend()
    plt.show()


if __name__ == "__main__":
    main()