#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameters:
Returns:

@author: alex
"""

def main():
    import pyarts as py
    import numpy as np
    import os



    filenames = [
        '/home/sasha/progs/oxygen_study/spectroscopy-oxygen-microwave/input/lin_567_2017-10-19T13-29-77.xml',
        '/home/sasha/progs/oxygen_study/spectroscopy-oxygen-microwave/input/lin_1155_2017-10-21T14-34-33.xml',
        '/home/sasha/progs/oxygen_study/spectroscopy-oxygen-microwave/input/lin_1433_2017-10-20T12-10-99.xml'
    ]
    filenames = ['/scratch/uni/u237/users/obobryshev/oxygen_study/02_closure_clean_amsua/noaa19/08_mpm2020/matlab_auxillaries/bar_full_noaa19/bar_806_2017-10-21T19-13-58.xml']
    for ff in filenames:
        test = py.xml.load(ff)

        output = list()
        for atm in test:
            output.append(
                atm[range(0, atm.shape[0], 50), :].copy()
            )

        oname = os.path.basename(ff[:-4]) + '_vertical50.xml'
        py.xml.save(output, oname)

    print('Finished successfully! Bye.')
    return test


if __name__ == "__main__":
    test = main()