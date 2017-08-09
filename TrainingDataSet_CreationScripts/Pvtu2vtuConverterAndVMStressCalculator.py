#######################################################################
# Python script for evaluation of the von Mises stress distribution
# for mitral valve leaflets tissue:
# 
# The script needs the following input:
#  - a (series of) vtu/pvtu file(s), which contains 3 scalar-valued arrays 
#    named {'u0', 'u1', 'u2'} as PointData
#    (which is the standard output format of HiFlow3-based simulations, 
#    when using the CellVisualization() functionalities).
# 
# Using the arrays specified above, the program computes the 
# displacement vector, the strain tensor and the von Mises stress 
# for material parameters \lambda={28466-40666-56933} and \mu={700-1000-1400}, 
# which corresponds to mitral valve leaflets tissue (according to [Mansi-2012]).
# Furthermore, the displacement vector will be added to the given 
# coordinates of the points.
# 
# The output is the following:
#  - a (series of) vtu file(s) that contains all the data of the
#    original file, however with modified coordinates of the points and the 
#    displacement vector as additional PointData and the strain tensor 
#    along with the von Mises stress distribution as additional CellData.
# 
# To run the script, call:
#   python vMStress.py <path_to_(series_of)_inputfile(s)> <lambda> <mu>
# 
# Example with pvtu:
# python Pvtu2vtuConverterAndVMStressCalculator.py SimResults/ 28466 700
# 
# author = {Nicolai Schoch}
# date = {2017-07-21}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-07-21"

import sys
import vtk
import glob


print('==========================')
print('Pvtu2vtuConverter started. \n')

# Get path/directory of simulation results, and set path combined with datatype:
path = sys.argv[1]
path_and_datatype = path + '*.pvtu'

# Get set of files to be processed by vMStress-Evaluator-Script:
files_to_be_iterated_over = glob.glob(path_and_datatype)

# filter out the '_deformedSolution_' files from this list:
files_to_be_really_iterated_over  = [ i for i in files_to_be_iterated_over if (i.find("_deformedSolution_") == -1 and i.find("_initial_mesh_") == -1 and i.find("_REALDATA_") == -1) ]

print('The following file list will be iterated over and processed by the pvtu2vtu converter:')
#print files_to_be_iterated_over
#print('\n VS. \n')
print files_to_be_really_iterated_over 

# Get material parameters:
matParamMVtissue_Lambda_string = sys.argv[2]
matParamMVtissue_Lambda = float(matParamMVtissue_Lambda_string)
matParamMVtissue_Mu_string = sys.argv[3]
matParamMVtissue_Mu = float(matParamMVtissue_Mu_string)

#if sys.argv[2] != 'NONE':
#  matParamMVtissue_Lambda_string = sys.argv[2]
#  matParamMVtissue_Lambda = float(matParamMVtissue_Lambda_string)
#else:
#  matParamMVtissue_Lambda = 28466
#
#if sys.argv[3] != 'NONE':
#  matParamMVtissue_Mu_string = sys.argv[3]
#  matParamMVtissue_Mu = float(matParamMVtissue_Mu_string)
#else:
#  matParamMVtissue_Mu = 700


# Iterate over all pvtu-files in SimResults-directory and evaluate vonMises-Stress:
for i in range(0,len(files_to_be_really_iterated_over )):
    
    # Get path and name of inputfile:
    inputfilename = files_to_be_really_iterated_over [i]
    
    # Get path and name of outputfile:
    if inputfilename[-4] == 'p':
      outputfilename = inputfilename[:-5] + '_outVis.vtu'
    else:
      #outputfilename = 'outVis_' + inputfilename
      print ('ERROR: THIS CASE IS NOT ALLOWED! PLEASE PROVIDE PVTU-FILES.')
    
    print ('current outputfilename: ', outputfilename)
    
    # Read (p)vtu file
    if inputfilename[-4] == 'p':
      reader = vtk.vtkXMLPUnstructuredGridReader()
      reader.SetFileName(inputfilename)
      reader.Update()
    else:
      print ('ERROR: THIS CASE IS NOT ALLOWED! PLEASE PROVIDE PVTU-FILES.')
      reader = vtk.vtkXMLUnstructuredGridReader()
      reader.SetFileName(inputfilename)
      reader.Update()
    
    grid = reader.GetOutput()
    
    
    # Get point data arrays u0, u1 and u2
    u0 = grid.GetPointData().GetArray('u0')
    u1 = grid.GetPointData().GetArray('u1')
    u2 = grid.GetPointData().GetArray('u2')
    
    # Set scalars
    grid.GetPointData().SetScalars(u0)
    
    # Warp by scalar u0
    warpScalar = vtk.vtkWarpScalar()
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      warpScalar.SetInputData(grid)
    else:
      warpScalar.SetInput(grid)
    warpScalar.SetNormal(1.0,0.0,0.0)
    warpScalar.SetScaleFactor(1.0)
    warpScalar.SetUseNormal(1)
    warpScalar.Update()
    
    # Get output and set scalars
    grid = warpScalar.GetOutput()
    grid.GetPointData().SetScalars(u1)
    
    # Warp by scalar u1
    warpScalar = vtk.vtkWarpScalar()
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      warpScalar.SetInputData(grid)
    else:
      warpScalar.SetInput(grid)
    warpScalar.SetNormal(0.0,1.0,0.0)
    warpScalar.SetScaleFactor(1.0)
    warpScalar.SetUseNormal(1)
    warpScalar.Update()
    
    # Get output and set scalars
    grid = warpScalar.GetOutput()
    grid.GetPointData().SetScalars(u2)
    
    # Warp by scalar u2
    warpScalar = vtk.vtkWarpScalar()
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      warpScalar.SetInputData(grid)
    else:
      warpScalar.SetInput(grid)
    warpScalar.SetNormal(0.0,0.0,1.0)
    warpScalar.SetScaleFactor(1.0)
    warpScalar.SetUseNormal(1)
    warpScalar.Update()
    
    # Get ouput and add point data arrays that were deleted before
    grid = warpScalar.GetOutput()
    grid.GetPointData().AddArray(u0)
    grid.GetPointData().AddArray(u1)
    grid.GetPointData().AddArray(u2)
    
    
    # Compute displacement vector
    calc = vtk.vtkArrayCalculator()
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      calc.SetInputData(grid)
    else:
      calc.SetInput(grid)
    calc.SetAttributeModeToUsePointData()
    calc.AddScalarVariable('x', 'u0', 0)
    calc.AddScalarVariable('y', 'u1', 0)
    calc.AddScalarVariable('z', 'u2', 0)
    calc.SetFunction('x*iHat+y*jHat+z*kHat')
    calc.SetResultArrayName('DisplacementSolutionVector')
    calc.Update()
    
    
    # Compute strain tensor
    derivative = vtk.vtkCellDerivatives()
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      derivative.SetInputData(calc.GetOutput())
    else:
      derivative.SetInput(calc.GetOutput())
    derivative.SetTensorModeToComputeStrain()
    derivative.Update()
    
    
    # Compute von Mises stress
    calc = vtk.vtkArrayCalculator()
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      calc.SetInputData(derivative.GetOutput())
    else:
      calc.SetInput(derivative.GetOutput())
    calc.SetAttributeModeToUseCellData()
    calc.AddScalarVariable('Strain_0', 'Strain', 0)
    calc.AddScalarVariable('Strain_1', 'Strain', 1)
    calc.AddScalarVariable('Strain_2', 'Strain', 2)
    calc.AddScalarVariable('Strain_3', 'Strain', 3)
    calc.AddScalarVariable('Strain_4', 'Strain', 4)
    calc.AddScalarVariable('Strain_5', 'Strain', 5)
    calc.AddScalarVariable('Strain_6', 'Strain', 6)
    calc.AddScalarVariable('Strain_7', 'Strain', 7)
    calc.AddScalarVariable('Strain_8', 'Strain', 8)
    
    #calc.SetFunction('sqrt( (2*1400*Strain_0 + 56933*(Strain_0+Strain_4+Strain_8))^2 + (2*1400*Strain_4 + 56933*(Strain_0+Strain_4+Strain_8))^2 + (2*1400*Strain_8 + 56933*(Strain_0+Strain_4+Strain_8))^2 - ( (2*1400*Strain_0 + 56933*(Strain_0+Strain_4+Strain_8))*(2*1400*Strain_4 + 56933*(Strain_0+Strain_4+Strain_8)) ) - ( (2*1400*Strain_0 + 56933*(Strain_0+Strain_4+Strain_8))*(2*1400*Strain_8 + 56933*(Strain_0+Strain_4+Strain_8)) ) - ( (2*1400*Strain_4 + 56933*(Strain_0+Strain_4+Strain_8))*(2*1400*Strain_8 + 56933*(Strain_0+Strain_4+Strain_8)) ) + 3 * ((2*1400*Strain_3)^2 + (2*1400*Strain_6)^2 + (2*1400*Strain_7)^2) )') # DEPRECATED.
    vMstressFunction_string = 'sqrt( (2*' + matParamMVtissue_Mu_string + '*Strain_0 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8))^2 + (2*' + matParamMVtissue_Mu_string + '*Strain_4 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8))^2 + (2*' + matParamMVtissue_Mu_string + '*Strain_8 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8))^2 - ( (2*' + matParamMVtissue_Mu_string + '*Strain_0 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8))*(2*' + matParamMVtissue_Mu_string + '*Strain_4 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8)) ) - ( (2*' + matParamMVtissue_Mu_string + '*Strain_0 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8))*(2*' + matParamMVtissue_Mu_string + '*Strain_8 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8)) ) - ( (2*' + matParamMVtissue_Mu_string + '*Strain_4 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8))*(2*' + matParamMVtissue_Mu_string + '*Strain_8 + ' + matParamMVtissue_Lambda_string + '*(Strain_0+Strain_4+Strain_8)) ) + 3 * ((2*' + matParamMVtissue_Mu_string + '*Strain_3)^2 + (2*' + matParamMVtissue_Mu_string + '*Strain_6)^2 + (2*' + matParamMVtissue_Mu_string + '*Strain_7)^2) )'
    calc.SetFunction(vMstressFunction_string)
    
    #calc.SetResultArrayName('vonMisesStress_forMV_mu1400_lambda56933') # DEPRECATED.
    vMstressArrayName_string = 'vonMisesStress_forMV_lambda' + matParamMVtissue_Lambda_string + '_mu' + matParamMVtissue_Mu_string
    calc.SetResultArrayName(vMstressArrayName_string)
    
    calc.Update()
    
    grid = calc.GetOutput()
    
    
    # Write output to vtu
    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetDataModeToAscii()
    writer.SetFileName(outputfilename)
    if vtk.vtkVersion().GetVTKMajorVersion() >= 6:
      writer.SetInputData(grid)
    else:
      writer.SetInput(grid)
    writer.Write()
    
    # ----------------------------------------------------------------------

print('All files successfully processed.')
print('Pvtu2vtuConverter successfully finished.')

# ----------------------------------------------------------------------
