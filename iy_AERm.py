#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameters:

Returns:
"""

import numpy as np
import pyarts as py
import pyarts.workspace
import datetime

def main(nelem):
    verbosity = 2
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
    ws.VectorNLinSpace( ws.f_grid, nelem, 5e9, 500e9 )

    ########    common_metmm.arts
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
    ws.Copy(ws.propmat_clearsky_agenda, ws.propmat_clearsky_agenda__OnTheFly )

    # Spectroscopy
    species = [
        "H2O, H2O-SelfContCKDMT252, H2O-ForeignContCKDMT252",
        "O2, O2-v1v0CKDMT100",
        #"N2,  N2-CIAfunCKDMT252, N2-CIArotCKDMT252",
        #"O3",
    ]
    # ws.abs_speciesSet( species=species )

    ws.abs_speciesSet(
        species=species,
    )

    ws.ReadLBLRTM(
        filename="/scratch/uni/u237/data/catalogue/aer/aer_v_3.2/line_file/aer_v_3.2",
        fmin=0.0,
        fmax=float(1e99),
        globalquantumnumbers="",
        localquantumnumbers="",
        normalization_option="None",
        mirroring_option="None",
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

    ws.VectorSetConstant(ws.surface_scalar_reflectivity, 1, 0.4)

    ws.ReadXML(ws.batch_atm_fields_compact, "testdata/garand_profiles.xml.gz")

    ws.batch_atm_fields_compactAddConstant(
        name="abs_species-O2", value=0.2095, condensibles=[]
    )
    ws.batch_atm_fields_compactAddConstant(
        name="abs_species-N2", value=0.7808, condensibles=[]
    )

    ws.abs_xsec_agenda_checkedCalc()
    ws.lbl_checkedCalc()

    # Setting the agenda for batch calculation 
    # Garand profiles have 42 different. We will make RT calculations for all of them.
    ws.ArrayOfMatrixCreate("out")
    ws.ArrayOfMatrixCreate("temp_tensor")
    ws.VectorCreate("temp_vector")
    ws.MatrixCreate("temp_matrix")
    
    ws.IndexSet(ws.ybatch_index, 0)

  
    # Extract the atmospheric profiles for this case:
    ws.Extract(
        ws.atm_fields_compact, 
        ws.batch_atm_fields_compact, 
        ws.ybatch_index
    )

    # Split up *atm_fields_compact* to
    # generate p_grid, t_field, z_field, vmr_field:
    ws.AtmFieldsAndParticleBulkPropFieldFromCompact()

    # Optionally set Jacobian parameters.
    ws.jacobianOff()

    # No scattering
    ws.cloudboxOff()
    
    # No sensor
    ws.sensorOff()
    
    # Definition of sensor position and LOS
    # ---
    #MatrixSetConstant( sensor_pos, 1, 1, 850e3 )
    #MatrixSet( sensor_los, [ 180 ] )
    ws.VectorSet( ws.rte_pos, 850e3 )
    ws.VectorSet( ws.rte_los, 180 )
    ws.VectorSet( ws.rte_pos2, [] )   

    # get some surface properties from corresponding atmospheric fields
    ws.Extract( ws.z_surface, ws.z_field, 0 )
    ws.Extract( ws.t_surface, ws.t_field, 0 )

    # Checks
    #sensor_checkedCalc
    ws.propmat_clearsky_agenda_checkedCalc()
    ws.atmfields_checkedCalc()
    ws.atmgeom_checkedCalc()
    ws.cloudbox_checkedCalc()


# Perform RT calculations
    ws.ArrayOfStringSet( ws.iy_aux_vars, [
      "Radiative background",
      "Optical depth"
      ]
    )

    ws.iyCalc()
    
    #=====================================================================
            #### Output ####
    #=====================================================================
      
    # ybatchCalc braucht y, y_aux und jacobian als Output. Da diese nicht
    # erzeugt werden, kann ARTS mit Touch() mitgeteilt werden, dass die 
    # Variable benutzt wurde.
    ws.Touch( ws.y )
    ws.Touch( ws.y_aux )
    ws.Touch( ws.jacobian )

    # Zusammenfassen aller Output-Variablen in die Variable out

    ws.Matrix1ColFromVector( ws.temp_matrix, ws.f_grid )
    ws.Append( ws.out, ws.temp_matrix )

    ws.Matrix1ColFromVector( ws.temp_matrix, ws.p_grid )
    ws.Append( ws.out, ws.temp_matrix )

    ws.Reduce( ws.temp_vector, ws.z_field )
    ws.Matrix1ColFromVector( ws.temp_matrix, ws.temp_vector )
    ws.Append( ws.out, ws.temp_matrix )

    ws.Reduce( ws.temp_vector, ws.t_field )
    ws.Matrix1ColFromVector( ws.temp_matrix, ws.temp_vector )
    ws.Append( ws.out, ws.temp_matrix )

    ws.Append( ws.out, ws.iy )

    #Print(iy_aux)
    #Exit
    
    tt_time = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    
    # out = ( f_grid, p_grid, z_field, t_field, vmr H20, 
    # abs H20, abs O2, abs[f,z], PlacnkBT )
    ws.WriteXMLIndexed( "ascii", ws.ybatch_index, ws.out, "Output/" + tt_time + "_out" )

# ====================================================================

# Store results
    ws.WriteXML( "ascii", ws.f_grid, "Output/" + tt_time + "_fgrid.xml" )
    ws.WriteXML( "ascii", ws.ybatch_index, "Output/" + tt_time + "_out_ybatch_n.xml" )

    print("Success! We reached the finish!")


if __name__ == "__main__":
    for nelem in [1125]:
        main(nelem)
