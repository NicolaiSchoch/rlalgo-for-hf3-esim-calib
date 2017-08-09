#######################################################################
# Python script for running the Reinforcement Q-Learning Algorithm 
# in order to calibrate a HiFlow3-based elasticity simulation setup:
# 
# The script needs the following input:
#   .. NONE: since currently hard-coded ...
# 
# Using the data specified above, the script runs the script and autonomously 
# calls all required sub-programs.
# 
# The output is the following:
#   .. a locally optimally calibrated simulation setup, i.e. xml-inputfile with 
#      optimized parameters, for HiFlow3-based elasticity simulation.
# 
# To run the script, call:
#   python RL_GeneralRunScript.py
# 
# author = {Nicolai Schoch}
# date = {2017-08-03}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-08-04"

#import os
#import sys

import subprocess
from subprocess import PIPE

from termcolor import colored # for colored terminal output for better overview.

import RL_QvalueComputeScriptNEW

# NOTE: RUN SIMULATION WITH NP=1 (in order for unique order of coords)!!!

def main():
    process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True)
    username = process.communicate()[0]
    print colored(username, 'red') #prints the username of the account you're logged in as
    
    action_number_out = -1
    step = 0
    
    #for i in range(0,10): # NOTE: replace the "for"-loop with break/raise-condition insed by means of a return-value combined with a tolerance in a "while"-loop.
    while action_number_out != 0:
        
        #step = i+1
        step += 1
        
        # Read in the current parameter-combination (i.e., the xml-inputfile), and check for all available Actions (1-7) the Q-value.
        # Then choose for the best Q-value the respective action and execute it (i.e., update the parameters accordingly).
        # In subprocess: store/append the new parameter set to existing param-sets-list:
        #cmdForQvalueComputeScript = 'python RL_QvalueComputeScript.py elastScen_Beam_RLalgo_TestInput_SIMDATA.xml %s' % str(step)
        #process = subprocess.call(cmdForQvalueComputeScript, shell=True)
        action_number_out = RL_QvalueComputeScriptNEW.qvalue_computer("elastScen_Beam_RLalgo_TestInput_SIMDATA.xml", str(step))
        print('\n')
        print colored('The current steps best ActionNumber is %s.' % str(action_number_out), 'green')
        print('\n')
        print colored('QvalueComputeScript successfully finished.', 'green')
        print colored('========================================== \n', 'green')
        
        # Etc. Repeat!


if __name__ == '__main__':
    print('\n')
    print colored('RLalgo_GeneralRunScript STARTED. \n', 'yellow')
    main()
    print('\n')
    print colored('RLalgo_GeneralRunScript FINISHED. \n', 'yellow')

