#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameters:

Returns:
@author: alex
"""


def run_arts(nelem=1125, model="O2-MPM2020", verbosity=3):
    import pyarts as py
    import datetime

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
    ws.VectorNLinSpace( ws.f_grid, nelem, 5e9, 1500e9 )

    #    common_metmm.arts
    ws.output_file_formatSetZippedAscii()
    ws.NumericSet(ws.ppath_lmax, float(250))

    # Agenda for scalar gas absorption calculation
    ws.Touch(ws.abs_nlte)

    @py.workspace.arts_agenda
    def abs_xsec_agenda(ws):
        ws.Ignore(ws.abs_nlte)
        ws.abs_xsec_per_speciesInit()
        #ws.propmat_clearskyAddPredefinedO2MPM2020()
        ws.abs_xsec_per_speciesAddConts()

    ws.Copy(ws.abs_xsec_agenda, abs_xsec_agenda)

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

    @py.workspace.arts_agenda
    def propmat_clearsky_agenda(ws):
        ws.Ignore(ws.rtp_mag)
        ws.Ignore(ws.rtp_los)
        ws.propmat_clearskyInit()
        ws.propmat_clearskyAddXsecAgenda()
        ws.propmat_clearskyAddLines()
        ws.propmat_clearskyForceNegativeToZero()
        ws.propmat_clearskyAddPredefinedO2MPM2020()
    ws.Copy(ws.propmat_clearsky_agenda, propmat_clearsky_agenda)

    # Spectroscopy
    species = [
        "H2O, H2O-SelfContCKDMT252, H2O-ForeignContCKDMT252",
        "O2-MPM2020",
        "N2,  N2-CIAfunCKDMT252, N2-CIArotCKDMT252",
        "O3",
    ]

    ws.abs_speciesSet(
        species=species,
    )

    ws.ReadARTSCAT(
        filename="instruments/metmm/abs_lines_metmm.xml.gz",
        fmin=0.0,
        fmax=float(1e99),
        globalquantumnumbers="",
        localquantumnumbers="",
        normalization_option="None",
        mirroring_option="None",
        population_option="LTE",
        lineshapetype_option="VP",
        cutoff_option="None",
        cutoff_value=750e9,
        linemixinglimit_value=-1.0,
    )

    ws.abs_linesSetCutoff(option="ByLine", value=750e9)
    ws.abs_linesSetNormalization(option="VVH")
    ws.abs_lines_per_speciesCreateFromLines()
    ws.abs_lines_per_speciesSetCutoffForSpecies(
        option="ByLine", value=5e9, species_tag="O3"
    )

    ws.VectorSetConstant(ws.surface_scalar_reflectivity, 1, 0.05)

    # Atmospheric profiles
    ws.ArrayOfMatrixCreate( "arrayofmatrix_1" )
    ws.ReadXML(ws.arrayofmatrix_1, "lin_567_2017-10-19T13-29-77_vertical50.xml")

    # The values taken for O2 and N2 are from Wallace&Hobbs, 2nd edition.
    ws.batch_atm_fields_compactFromArrayOfMatrix(
        ws.batch_atm_fields_compact,
        ws.atmosphere_dim,
        ws.arrayofmatrix_1,
        ['T', 'z', 'abs_species-H2O', 'abs_species-O3']
    )

    # add constant profiles for O2 and N2
    ws.batch_atm_fields_compactAddConstant(name="abs_species-O2", value=0.2095)
    ws.batch_atm_fields_compactAddConstant(name="abs_species-N2", value=0.7808)
    # Delete original data array to conserve memory:
    # ---
    ws.Delete(ws.arrayofmatrix_1)
    ws.Extract(ws.atm_fields_compact, ws.batch_atm_fields_compact, 0)

    ws.abs_xsec_agenda_checkedCalc()
    ws.lbl_checkedCalc()

    # Split up *atm_fields_compact* to
    # generate p_grid, t_field, z_field, vmr_field:
    ws.AtmFieldsAndParticleBulkPropFieldFromCompact()


    # get some surface properties from corresponding atmospheric fields
    ws.Extract(ws.z_surface, ws.z_field, 0)
    ws.Extract(ws.t_surface, ws.t_field, 0)

    # Optionally set Jacobian parameters.
    ws.jacobianOff()

    # No scattering
    ws.cloudboxOff()

    # Checks
    ws.propmat_clearsky_agenda_checkedCalc()
    ws.atmfields_checkedCalc()
    ws.atmgeom_checkedCalc()
    ws.cloudbox_checkedCalc()
    ws.sensor_checkedCalc()

    # Perform RT calculations
    ws.yCalc()

    # ====================================================================
    # Output ####
    # ====================================================================

    tt_time = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    # Store results
    ws.WriteXML("ascii", ws.y, "Output/y_" + model + tt_time + ".xml" )

    print("Success! We reached the finish!")
    return tt_time


def main():
    for nelem in [1125]:
        run_arts(nelem)


if __name__ == "__main__":
    main()