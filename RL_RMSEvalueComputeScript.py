#######################################################################
# Python script for comparing two meshes (with the same number of nodes and the same connectivity), 
# and for computing the root-mean-square error (RMSE) of realdata-mesh1 and simulateddata-mesh2:
# 
# The script needs the following input:
#   .. realdata-mesh1:      ...
#   .. simulateddata-mesh2: ...
# 
# Using the data specified above, the program computes the root-mean-square error (RMSE):
# RMSE := \sqrt{\frac{\sum_{i=1}^n (\hat y_i - y_i)^2}{n}}.
# 
# The output is the following:
#   .. RMSE-value: a scalar value as a comparison measure for the two input meshes.
# 
# To run the script, call:
#   python SimResultsComparisonOperator.py <path-to-files> <realdata-name> <simdata-name>
# 
# Example:
#   python SimResultsComparisonOperator.py <PATH> realdata_filename_tsX.vtu simdata_filename_tsX.vtu
#   python SimResultsComparisonOperator.py TestData2/ e_sim_solution_np4_RefLvl0_Tstep.0003_outVis.vtu e_sim_solution_np4_RefLvl0_Tstep.0004_outVis.vtu
# 
# author = {Nicolai Schoch}
# date = {2017-08-08}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-07-31"

import sys
import os
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
#from vtk.util import numpy_support
#import glob
from termcolor import colored # for colored terminal output for better overview.


def rmsevalue_computer(arg1, arg2, arg3, arg4, arg5):
    
    print('=====================================')
    print('SimResultsComparisonOperator started. \n')
    
    # Get path/directory of the real mesh data AND of the simulation-results-based mesh data,
    # and the specification of the respective simulated and real data:
    path = arg1 #sys.argv[1]
    realdata = arg2 #sys.argv[2]
    simdata = arg3 #sys.argv[3]
    stepnum = arg4 #sys.argv[4]
    action_number = arg5
    
    path_and_realdata = path + realdata
    path_and_simdata = path + simdata
    
    print('Control Output: Path to real data:      ', path_and_realdata)
    print('Control Output: Path to simulated data: ', path_and_simdata)
    
    # ------------------------------------------------
    # Read first vtu file (representing the real data)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(path_and_realdata)
    reader.Update()
    
    # Get the coordinates of nodes in the mesh
    nodes_vtk_array_realdata = reader.GetOutput().GetPoints().GetData()
    
    # ------------------------------------------------
    # Read second vtu file (representing the simulated data)
    readerTwo = vtk.vtkXMLUnstructuredGridReader()
    readerTwo.SetFileName(path_and_simdata)
    readerTwo.Update()
    
    # Get the coordinates of nodes in the mesh
    nodes_vtk_array_simdata = readerTwo.GetOutput().GetPoints().GetData()
    
    # ------------------------------------------------
    #Get the coordinates of the nodes of the real-data-mesh as a numpy-array:
    nodes_numpy_array_realdata = vtk_to_numpy(nodes_vtk_array_realdata)
    x_rd,y_rd,z_rd = nodes_numpy_array_realdata[:,0] , nodes_numpy_array_realdata[:,1] , nodes_numpy_array_realdata[:,2]
    #Get the coordinates of the nodes of the simulated-data-mesh as a numpy-array:
    nodes_numpy_array_simdata = vtk_to_numpy(nodes_vtk_array_simdata)
    x_sd,y_sd,z_sd = nodes_numpy_array_simdata[:,0] , nodes_numpy_array_simdata[:,1] , nodes_numpy_array_simdata[:,2]
    
    print('Control Output: nodes_numpy_array_simdata.shape = ', nodes_numpy_array_simdata.shape) # num_points x dim
    
    # Compute real_coords{0,1,2} - sim_coords{0,1,2}
    x_diff = x_rd - x_sd
    y_diff = y_rd - y_sd
    z_diff = z_rd - z_sd
    
    #print(x_diff.shape) # num_points x 1
    print('Control Output: num_points = nodes_numpy_array_realdata.size/3 = ', nodes_numpy_array_realdata.size/3)
    
    # Compute the RMSE (which represents the sample standard deviation of the differences 
    # between the simulated/predicted values and real/observed values:
    
    error_scaler = 0.0
    num_points = nodes_numpy_array_realdata.size/3
    #total_error = 0.0
    
    for i in range(0,num_points):
    	
    	# compute the length of the diff vector for every node in the mesh:
    	#error_scaler += np.sqrt( (x_diff[i])**2 + (y_diff[i])**2 + (z_diff[i])**2 )
    	# square the length in order to stronger account for large errors:
    	error_scaler += (x_diff[i])**2 + (y_diff[i])**2 + (z_diff[i])**2
    	# ...
    
    print('The error_scaler in Step %s is: %s.' % (stepnum, error_scaler))
    
    # Compute the mean of squared errors, i.e., divide by the number of mesh points:
    error_scaler = error_scaler/num_points
    
    # Compute the root of the mean of squared errors, i.e., the RMSE:
    rmse_value = np.sqrt(error_scaler)
    print('The RMSE in Step %s is: %s.' % (stepnum, rmse_value))
    
    
    # Return the RMSE-value: --> rather: Append it to an existing list of RMSE-values:
    #return rmse_value
    # Return the nodes_numpy_array_simdata: --> rather: Append it to an existing list of nodes_numpy_array_simdata-list:
    #return nodes_numpy_array_simdata
    
    
    # Store/Append the RMSE-value in/to a list:
    rmsefilename = 'RL_rmse_value_list.txt'
    
    if os.path.exists(rmsefilename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    
    rmse_value_list_file = open(rmsefilename,append_write)
    rmse_value_list_file.write("RMSE-Value in Step " + str(stepnum) + " Action Number " + str(action_number) + ": " + str(rmse_value) + '\n')
    rmse_value_list_file.close()
    
    
#    # Store/Append the obtained simulation-results deformed coords 'nodes_numpy_array_simdata' in/to a list:
#    simfilename_base = 'RL_simresults_defcoords_list' #.csv'
#    simfilename = ''
#    stepnum = int(stepnum)
#    
#    if stepnum < 101:
#        simfilename = simfilename_base + '_part1.csv'
#    elif stepnum < 201:
#        simfilename = simfilename_base + '_part2.csv'
#    elif stepnum < 301:
#        simfilename = simfilename_base + '_part3.csv'
#    elif stepnum < 401:
#        simfilename = simfilename_base + '_part4.csv'
#    elif stepnum < 501:
#        simfilename = simfilename_base + '_part5.csv'
#    elif stepnum < 601:
#        simfilename = simfilename_base + '_part6.csv'
#    elif stepnum < 701:
#        simfilename = simfilename_base + '_part7.csv'
#    elif stepnum < 801:
#        simfilename = simfilename_base + '_part8.csv'
#    elif stepnum < 901:
#        simfilename = simfilename_base + '_part9.csv'
#    elif stepnum < 1001:
#        simfilename = simfilename_base + '_part10.csv'
#    
#    if os.path.exists(simfilename):
#        append_write = 'a' # append if already exists
#    else:
#        append_write = 'w' # make a new file if not
#    
#    simresults_list_file = open(simfilename,append_write)
#    #simresults_list_file.write("\nSimResultsDefCoords:\n" + str(nodes_numpy_array_simdata) + '\n')
#    simresults_list_file.write("\nSimResultsDefCoords in Step " + str(stepnum) + " Action Number " + str(action_number) + ":\n")
#    nodes_numpy_array_simdata.tofile(simresults_list_file, sep=',', format="%s")
#    simresults_list_file.close()
    
    
    print('SimResultsComparisonOperator successfully finished.')
    
    return rmse_value


if __name__ == '__main__':
    print('\n')
    print colored('RMSEvalueComputeFunction STARTED. \n', 'yellow')
    rmsevalue_computer(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    print('\n')
    print colored('RMSEvalueComputeFunction FINISHED. \n', 'yellow')

