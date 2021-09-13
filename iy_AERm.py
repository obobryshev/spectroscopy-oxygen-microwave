#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameters:

Returns:
@author: alex
"""


def run_arts(nelem=1125, model="O2-AER", verbosity=2):
    import pyarts as py
    import datetime

    # verbosity = 2
    ws = py.workspace.Workspace(verbosity)
    ws.execute_controlfile("general/general.arts")
    ws.execute_controlfile("general/continua.arts")
    ws.execute_controlfile("general/agendas.arts")
    ws.execute_controlfile("general/planet_earth.arts")

    ws.verbositySetScreen(ws.verbosity, verbosity)

    ws.AtmosphereSet1D()
    ws.IndexSet(ws.stokes_dim, 1)
    ws.StringSet(ws.iy_unit, "PlanckBT")

    # monochromatic frequency grid
    # VectorNLinSpace( 	out, nelem, start, stop )
    ws.VectorNLinSpace(ws.f_grid, nelem, 5e9, 500e9)

    #    common_metmm.arts
    ws.output_file_formatSetZippedAscii()
    ws.NumericSet(ws.ppath_lmax, float(250))

    # Agenda for scalar gas absorption calculation
    ws.Copy(ws.abs_xsec_agenda, ws.abs_xsec_agenda__noCIA)

    # Surface
    ws.Copy(
        ws.surface_rtprop_agenda,
        ws.surface_rtprop_agenda__Specular_NoPol_ReflFix_SurfTFromt_surface,
    )

    # (standard) emission calculation
    ws.Copy(ws.iy_main_agenda, ws.iy_main_agenda__Emission)

    # cosmic background radiation
    ws.Copy(ws.iy_space_agenda, ws.iy_space_agenda__CosmicBackground)

    # standard surface agenda (i.e., make use of surface_rtprop_agenda)
    ws.Copy(ws.iy_surface_agenda, ws.iy_surface_agenda__UseSurfaceRtprop)

    # sensor-only path
    ws.Copy(ws.ppath_agenda, ws.ppath_agenda__FollowSensorLosPath)

    # no refraction
    ws.Copy(ws.ppath_step_agenda, ws.ppath_step_agenda__GeometricPath)

    # Set propmat_clearsky_agenda to use on-the-fly absorption
    ws.Copy(ws.propmat_clearsky_agenda, ws.propmat_clearsky_agenda__OnTheFly)

    # Spectroscopy
    species = [
        "H2O, H2O-SelfContCKDMT252, H2O-ForeignContCKDMT252",
        "O2, O2-v1v0CKDMT100",
        "N2,  N2-CIAfunCKDMT252, N2-CIArotCKDMT252",
        "O3",
    ]
    # ws.abs_speciesSet( species=species )

    ws.abs_speciesSet(
        species=species,
    )

    ws.ReadLBLRTM(
        filename="aer_v_3.2",
        fmin=0.0,
        fmax=float(2e12),
        globalquantumnumbers="",
        localquantumnumbers="",
        normalization_option="SFS",
        mirroring_option="None", # "Option Lorentz causes Exception error
        population_option="LTE",
        lineshapetype_option="VP",
        cutoff_option="None",
        cutoff_value=-1.0,
        linemixinglimit_value=-1.0,
    )

    ws.abs_linesSetNormalization(option="VVH")
    ws.abs_lines_per_speciesCreateFromLines()
    ws.abs_lines_per_speciesSetCutoffForSpecies(
        option="ByLine", value=750e9, species_tag="H2O"
    )
    ws.abs_lines_per_speciesSetCutoffForSpecies(
        option="ByLine", value=750e9, species_tag="N2"
    )
    ws.abs_lines_per_speciesSetCutoffForSpecies(
        option="ByLine", value=5e9, species_tag="O3"
    )

    ws.VectorSetConstant(ws.surface_scalar_reflectivity, 1, 0.05)

    # Atmospheric scenario
    # A pressure grid rougly matching 0 to 80 km, in steps of 2 km.
    ws.VectorNLogSpace(ws.p_grid, 900, 1013e2, 10.0)
    ws.AtmRawRead(basename="planets/Earth/Fascod/midlatitude-summer/midlatitude-summer")
    ws.AtmFieldsCalc(interp_order=3)
    # get some surface properties from corresponding atmospheric fields
    ws.Extract(ws.z_surface, ws.z_field, 0)
    ws.Extract(ws.t_surface, ws.t_field, 0)

    ws.abs_xsec_agenda_checkedCalc()
    ws.lbl_checkedCalc()

    # Optionally set Jacobian parameters.
    ws.jacobianOff()

    # No scattering
    ws.cloudboxOff()

    # No sensor
    ws.sensorOff()

    # Definition of sensor position and LOS
    # ---
    ws.VectorSet(ws.rte_pos, 850e3)
    ws.VectorSet(ws.rte_los, 180)
    ws.VectorSet(ws.rte_pos2, [])

    # Checks
    ws.propmat_clearsky_agenda_checkedCalc()
    ws.atmfields_checkedCalc()
    ws.atmgeom_checkedCalc()
    ws.cloudbox_checkedCalc()

    # Perform RT calculations
    ws.iyCalc()

    # =====================================================================
    #### Output ####
    # =====================================================================

    tt_time = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

    print("Success! We reached the finish!")

    # Store results
    ws.WriteXML( "ascii", ws.f_grid, "Output/fgrid_" + model + "_" + tt_time + ".xml" )
    ws.WriteXML( "ascii", ws.iy, "Output/iy_" + model + "_midlat-s_" + tt_time + ".xml" )
    return tt_time


def main():
    for nelem in [1125]:
        run_arts(nelem)


if __name__ == "__main__":
    main()
