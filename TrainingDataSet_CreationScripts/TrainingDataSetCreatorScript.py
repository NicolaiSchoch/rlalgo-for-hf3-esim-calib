#######################################################################
# Python script for running the script to create a training data set for 
# training a reinforcement learning algorithm in order to calibrate a 
# HiFlow3-based elasticity simulation setup:
# 
# The script needs the following input:
#   .. NONE: since currently hard-coded ...
# 
# Using the data specified above, the script runs the script and autonomously 
# calls all required sub-programs.
# 
# The output is the following:
#   .. a training data set of (S_t, A_t; S_tp1; R_tp1) quadrupels.
# 
# To run the script, call:
#   python TrainingDataSetCreatorScript.py <xxx> <xxx>
# 
# author = {Nicolai Schoch}
# date = {2017-07-31}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-07-31"

#import os
#import sys

import subprocess
from subprocess import PIPE

from termcolor import colored # for colored terminal output for better overview.

# NOTE: RUN SIMULATION WITH NP=1 (in order for unique order of coords)!!!

def main():
    process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True)
    username = process.communicate()[0]
    print colored(username, 'red') #prints the username of the account you're logged in as
    
    for i in range(0,1000):
        
        step = i+1
        
        # Random-select an Action (1-7) to manipulate the parameter set of the previously existing XML Inputfile, and
        # set up the subsequent Simulation Scenario (through re-defining the XML InputFile) 
        # by means of updating the previous scenario's parameter set with a new parameter set:
        # In subprocess: store/append the new parameter set to existing param-sets-list:
        cmdForActionSelectorAndSimSetupper = 'python ActionSelectorAndSimSetupper.py elastScen_Beam_ActionSelector_Input.xml %s' % str(step)
        process = subprocess.call(cmdForActionSelectorAndSimSetupper, shell=True)
        print('\n')
        print colored('ActionSelectorAndSimSetupper successfully finished.', 'green')
        print colored('=================================================== \n', 'green')
        
        # Run Simulation App with np=1 and with newly-defined XML Inputfile:
        cmdForSimulationRunner = 'python SimulationRunner.py 1 elastScen_Beam_ActionSelector_Input.xml'
        process = subprocess.call(cmdForSimulationRunner, shell=True)
        print('\n')
        print colored('SimulationRunner successfully finished.', 'green')
        print colored('======================================= \n', 'green')
        
        # Convert Pvtu sim output to vtu sim output, 
        # and store/append deformed-coords (x1,x2,x3) to existing coords-lists:
        cmdForPvtu2vtuConverter = 'python Pvtu2vtuConverterAndVMStressCalculator.py TestSimResults/ 140000 50000'  # note the lambda and mu parameters are not effective here.
        process = subprocess.call(cmdForPvtu2vtuConverter, shell=True)
        print('\n')
        print colored('Pvtu2vtuConverter successfully finished.', 'green')
        print colored('======================================== \n', 'green')
        
        # Read the vtk-xml-tree of the deformedCoords and extract the coords list, i.e. "nodes_numpy_array_simdata", in order to append it to a stored nodes_numpy_array_simdata-list.
        # Then compare the 'simulation results' with the 'real data' and compute the RMSE value, 
        # and append/store the RMSE-value to a stored RMSE-values-list:
        #cmdForSimResultsComparisonOperator = 'python SimResultsComparisonOperator.py TestSimResults/ Test_Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu Test_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu'
        cmdForSimResultsComparisonOperator = 'python SimResultsComparisonOperator.py TestSimResults/ Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu %s' % str(step)
        process = subprocess.call(cmdForSimResultsComparisonOperator, shell=True)
        print('\n')
        # In subprocess: store/append "deformed-coords (x1,x2,x3)", i.e. the "nodes_numpy_array_simdata", to existing coords-lists.
        # In subprocess: store/append "RMSE-value" to stored RMSE-values-list.
        print colored('SimResultsComparisonOperator successfully finished.', 'green')
        print colored('=================================================== \n', 'green')
        
        # Etc. Repeat!
        # QUESTION: get output/return value from one python program here or into another python program.
    
#    # Dummy python progs:
#    # Source: https://stackoverflow.com/questions/32318909/run-a-python-script-from-another-python-script-and-pass-variables-to-it
#    process = subprocess.call('python py1.py --help', shell=True)
#    process = subprocess.call('python py2.py --help', shell=True)
#    process = subprocess.call('python py3.py --help', shell=True)


if __name__ == '__main__':
    print('\n')
    print colored('TrainingDataSetCreatorScript STARTED. \n', 'yellow')
    main()
    print('\n')
    print colored('TrainingDataSetCreatorScript FINISHED. \n', 'yellow')

