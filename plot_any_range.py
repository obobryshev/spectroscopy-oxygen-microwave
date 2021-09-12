#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def build_results_path(model="TRE05", tt_model="2021-08-29_0126"):
    """
    model = "O2-TRE05"
    model = "O2-MPM2020"
    model = "O2-AER"
    """
    from os.path import join, realpath, dirname

    main_path = join(dirname(realpath(__file__)), "Output")

    results = join(
        main_path,
        "iy_" + model + "_midlat-s_" + tt_model + ".xml"
    )

    fgrid = join(
        main_path,
        "fgrid_" + model + "_" + tt_model + ".xml"
    )

    res_path = list()
    res_path.append(results)
    res_path.append(fgrid)

    return res_path


def read_arts_output_models(timestamp={}):
    """

    Returns
    -------
    iy : list
        DESCRIPTION.
    fgrid : np.array 1-D
        DESCRIPTION.

    """
    import numpy as np
    from pyarts import xml

    if not timestamp:
        timestamp['O2-TRE05'] = "2021-08-29_0126"
        timestamp['O2-AER'] = "2021-08-30_2245"
        timestamp['O2-MPM2020'] = "2021-08-29_0205"

    l = dict()
    for key in timestamp.keys():
        l[key] = build_results_path(model=key, tt_model=timestamp[key])

    # l_tre = build_results_path(model="O2-TRE05", tt_model=tt_tre)
    # l_aer = build_results_path(model="O2-AER", tt_model=tt_aer)
    # l_mpm = build_results_path(model="O2-MPM2020", tt_model=tt_mpm)


    for key in timestamp.keys():
        l[key].append(np.squeeze(xml.load(l[key][0])))
        l[key].append(xml.load(l[key][1]) / 1e9)

    return l


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

    print('stop')
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


def main():
    # TODO: first run arts with latest settings
    import iy_AERm
    import iy_MPM2020m
    import iy_TRE05m

    timestamp = dict()
    # timestamp['O2-AER'] = iy_AERm.run_arts(verbosity=0)
    # timestamp['O2-TRE05'] = iy_TRE05m.run_arts(verbosity=0)
    # timestamp['O2-MPM2020'] = iy_MPM2020m.run_arts(verbosity=0)

    # TRE, AER, MPM
    xmldata = read_arts_output_models(timestamp)

    # plot_5_500GHz(iy, fgrid)
    plot_any_range(xmldata, start=5, end=500)
    pass


if __name__ == "__main__":
    main()
    # pass
