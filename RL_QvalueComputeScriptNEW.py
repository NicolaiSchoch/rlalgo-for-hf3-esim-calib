#######################################################################
# Python script for updating the Q-value-vector for all (5 or 7) available Actions 
# and for then choosing/executing the best Action (which corresponds to 
# the respective manipulation of the parameter values (lambda, mu, grav) 
# in the XML Inputfile).
# 
# The script needs the following input:
#   .. the current state's xml inputfile, i.e., the current parameter value combination.
# 
# Using the data specified above, the script sets up 7 potentially next 
# HiFlow3 simulation xml-inputfiles with respectively manipulated new parameters, 
# and accordingly computes the potentially next resulting Q-values.
# 
# The script produces the following output:
#   .. the following scenario's xml-file with the newly specified/manipulated parameters.
# 
# To run the script, call:
#   python RL_QvalueComputeScript.py <previous-xml-inputfile> <step-number>
# 
# Example:
#   python ActionSelectorAndSimSetupper.py elastScen_Beam_RLalgo_TestInput_SIMDATA.xml numX
# 
# author = {Nicolai Schoch}
# date = {2017-08-04}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-08-04"

import sys
import os

import subprocess
from subprocess import PIPE  # NOTE: probably not needed anymore.

from termcolor import colored # for colored terminal output for better overview.

import xml.etree.ElementTree as ET

import RL_RMSEvalueComputeScript

print('============================')
print('QvalueComputeScript started. \n')


def qvalue_computer(arg1, arg2):
    
    # Read in arguments (xml-file and step-number):
    infilenamestring = arg1 #sys.argv[1] # e.g. 'elastScen_Beam_RLalgo_TestInput.xml'.
    stepnum = arg2 #sys.argv[2] # just counting the steps until sufficient approximation is achieved.
    
    # Declare the parameters:
    parLambda = 0.0
    parMu = 0.0
    #parGrav = 0.0
    
    # Set manipulation (epsilon) values:
    epsilon_lam = 5000.0
    epsilon_mu = 3000.0
    #epsilon_grav = 0.5
    
    # Declare the Q-value-Vector (which gets updated for each learning step):
    qValueVec = [0.0, 0.0, 0.0, 0.0, 0.0] #, 0.0, 0.0]
    
    # Loop over all actions [0,1,2,3,4,(5,6)] and compute the Q-value:
    for action_number in range(0,5):
        
        print colored("Going to update component %s (= action-number) of the Q-value-vector in Step %s.\n" % (action_number, stepnum), 'yellow')
        
        # According to the above selected action-number, conduct an action in the tree below:
        tree = ET.parse(infilenamestring)
        root = tree.getroot()
        
        # ========================================================
        # For CURRENT SIM SETUP: if action_number == 0, i.e., no parameter manipulation:
        if action_number == 0:
            
            # Set up the respective TestAction-xml-inputfile for Action 0:
            outfilenamestring = infilenamestring[:-4] + '_TestAction' + str(action_number) + '.xml'
            print("The outfilenamestring for Action %s is: %s.\n" % (action_number, outfilenamestring))
            tree.write(outfilenamestring)
            
            # Subprocess Function Calls:
            process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True) # NOTE: probably not needed anymore.
            
            # 1.) Run Simulation-App with np=1 and with newly-defined TestAction-XML-Inputfile:
            cmdForSimulationRunner = "python RL_SimulationRunnerScript.py 1 " + outfilenamestring
            #print("CONTROL OUTPUT: The cmdForSimulationRunnerScript is: %s" % cmdForSimulationRunner)
            process = subprocess.call(cmdForSimulationRunner, shell=True)
            print('\n')
            print colored('SimulationRunner successfully finished.', 'green')
            print colored('======================================= \n', 'green')
            
            # 2.) Run Pvtu2vtu-Converter with obtained TestAction simulation results:
            cmdForPvtu2vtuConverter = 'python RL_Pvtu2vtuConverterAndVMStressCalculator.py RL_TestSimResults/ 140000 50000' 
            # note the lambda and mu parameters are not relevant/effective here, but needed for the function call.
            process = subprocess.call(cmdForPvtu2vtuConverter, shell=True)
            print('\n')
            print colored('Pvtu2vtuConverter successfully finished.', 'green')
            print colored('======================================== \n', 'green')
            
            # 3.) Run RMSE-value-Compute-Script, in order to compute the RMSE-value 
            # for the respective TestAction-deformedCoords obtained from the Pvtu2vtu-Converter, ...
            # Therefore, read the vtk-xml-tree of the deformedCoords and extract the coords list, i.e. "nodes_numpy_array_simdata", 
            # in order to append it to a stored nodes_numpy_array_simdata-list.
            # Then compare the 'simulation results' with the 'real data' and compute the RMSE value, 
            # and return the RMSE-value (and additionally append/store the RMSE-value to a stored RMSE-values-list):
            #cmdForRMSEvalueComputeScript = 'python RL_RMSEvalueComputeScriptOLD.py RL_TestSimResults/ Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu %s' % str(stepnum)
            #process = subprocess.call(cmdForRMSEvalueComputeScript, shell=True)
            #rmse_value_out = subprocess.check_output([sys.executable, cmdForRMSEvalueComputeScript])
            rmse_value_out = RL_RMSEvalueComputeScript.rmsevalue_computer("RL_TestSimResults/", "Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", "TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", str(stepnum), str(action_number))
            print('\n')
            print colored("The RMSE value in Step %s for ActionNumber %s is: %s." % (stepnum, action_number, rmse_value_out), 'yellow') #... return value
            print('\n')
            print colored('RMSEvalueComputeScript successfully finished.', 'green')
            print colored('============================================= \n', 'green')
            
            # Transfer RMSE-value into (the respective component = action_number of) the Q-value-Vector:
            qValueVec[action_number] = rmse_value_out
        
        
        # ========================================================
        # For LAMBDA: if action_number == 1 or action_number == 2:
        if action_number == 1:
            for param_lam in root.iter('lambda'):
                prev_param_lam = float(param_lam.text)
                new_lam = prev_param_lam + epsilon_lam
                parLambda = new_lam
                param_lam.text = str(new_lam)
                
                # Set up the respective TestAction-xml-inputfile for Action 1:
                outfilenamestring = infilenamestring[:-4] + '_TestAction' + str(action_number) + '.xml'
                print("The outfilenamestring for Action %s is: %s.\n" % (action_number, outfilenamestring))
                tree.write(outfilenamestring)
                
    #            parameter_set = [parLambda, parMu] #, parGrav]
    #            
    #            # Return or Store the action number in a list, or/and 
    #            # alternatively/additionally store the resulting parameter set:
    #            filename = 'state_list.txt'
    #            
    #            if os.path.exists(filename):
    #                append_write = 'a' # append if already exists
    #            else:
    #                append_write = 'w' # make a new file if not
    #            
    #            state_list_file = open(filename,append_write)
    #            #state_list_file.write("ActionNumber in Step " + str(stepnum) + ": " + str(action_number) + '\n')
    #            #state_list_file.write("ParameterSet in Step " + str(stepnum) + ": " + str(parameter_set) + '\n')
    #            state_list_file.close()
                
                # Subprocess Function Calls:
                process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True) # NOTE: probably not needed anymore.
                
                # 1.) Run Simulation-App with np=1 and with newly-defined TestAction-XML-Inputfile:
                cmdForSimulationRunner = "python RL_SimulationRunnerScript.py 1 " + outfilenamestring
                #print("CONTROL OUTPUT: The cmdForSimulationRunnerScript is: %s" % cmdForSimulationRunner)
                process = subprocess.call(cmdForSimulationRunner, shell=True)
                print('\n')
                print colored('SimulationRunner successfully finished.', 'green')
                print colored('======================================= \n', 'green')
                
                # 2.) Run Pvtu2vtu-Converter with obtained TestAction simulation results:
                cmdForPvtu2vtuConverter = 'python RL_Pvtu2vtuConverterAndVMStressCalculator.py RL_TestSimResults/ 140000 50000' 
                # note the lambda and mu parameters are not relevant/effective here, but needed for the function call.
                process = subprocess.call(cmdForPvtu2vtuConverter, shell=True)
                print('\n')
                print colored('Pvtu2vtuConverter successfully finished.', 'green')
                print colored('======================================== \n', 'green')
                
                # 3.) Run RMSE-value-Compute-Script, in order to compute the RMSE-value 
                # for the respective TestAction-deformedCoords obtained from the Pvtu2vtu-Converter, ...
                # Therefore, read the vtk-xml-tree of the deformedCoords and extract the coords list, i.e. "nodes_numpy_array_simdata", 
                # in order to append it to a stored nodes_numpy_array_simdata-list.
                # Then compare the 'simulation results' with the 'real data' and compute the RMSE value, 
                # and return the RMSE-value (and additionally append/store the RMSE-value to a stored RMSE-values-list):
                #cmdForRMSEvalueComputeScript = 'python RL_RMSEvalueComputeScriptOLD.py RL_TestSimResults/ Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu %s' % str(stepnum)
                #process = subprocess.call(cmdForRMSEvalueComputeScript, shell=True)
                #rmse_value_out = subprocess.check_output([sys.executable, cmdForRMSEvalueComputeScript])
                rmse_value_out = RL_RMSEvalueComputeScript.rmsevalue_computer("RL_TestSimResults/", "Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", "TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", str(stepnum), str(action_number))
                print('\n')
                print colored("The RMSE value in Step %s for ActionNumber %s is: %s." % (stepnum, action_number, rmse_value_out), 'yellow') #... return value
                print('\n')
                print colored('RMSEvalueComputeScript successfully finished.', 'green')
                print colored('============================================= \n', 'green')
                
                # Transfer RMSE-value into (the respective component = action_number of) the Q-value-Vector:
                qValueVec[action_number] = rmse_value_out
        
        
        if action_number == 2:
            for param_lam in root.iter('lambda'):
                prev_param_lam = float(param_lam.text)
                new_lam = prev_param_lam - epsilon_lam
                
                if new_lam >= 0.0:
                    # positive lambda-values are permitted, proceed as above in Action 1:
                    parLambda = new_lam
                    param_lam.text = str(new_lam)
                    
                    # Set up the respective TestAction-xml-inputfile for Action 2:
                    outfilenamestring = infilenamestring[:-4] + '_TestAction' + str(action_number) + '.xml'
                    print("The outfilenamestring for Action %s is: %s.\n" % (action_number, outfilenamestring))
                    tree.write(outfilenamestring)
                    
    #            parameter_set = [parLambda, parMu] #, parGrav]
    #            
    #            # Return or Store the action number in a list, or/and 
    #            # alternatively/additionally store the resulting parameter set:
    #            filename = 'state_list.txt'
    #            
    #            if os.path.exists(filename):
    #                append_write = 'a' # append if already exists
    #            else:
    #                append_write = 'w' # make a new file if not
    #            
    #            state_list_file = open(filename,append_write)
    #            #state_list_file.write("ActionNumber in Step " + str(stepnum) + ": " + str(action_number) + '\n')
    #            #state_list_file.write("ParameterSet in Step " + str(stepnum) + ": " + str(parameter_set) + '\n')
    #            state_list_file.close()
                    
                    # Subprocess Function Calls:
                    process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True) # NOTE: probably not needed anymore.
                    
                    # 1.) Run Simulation-App with np=1 and with newly-defined TestAction-XML-Inputfile:
                    cmdForSimulationRunner = "python RL_SimulationRunnerScript.py 1 " + outfilenamestring
                    #print("CONTROL OUTPUT: The cmdForSimulationRunnerScript is: %s" % cmdForSimulationRunner)
                    process = subprocess.call(cmdForSimulationRunner, shell=True)
                    print('\n')
                    print colored('SimulationRunner successfully finished.', 'green')
                    print colored('======================================= \n', 'green')
                    
                    # 2.) Run Pvtu2vtu-Converter with obtained TestAction simulation results:
                    cmdForPvtu2vtuConverter = 'python RL_Pvtu2vtuConverterAndVMStressCalculator.py RL_TestSimResults/ 140000 50000' 
                    # note the lambda and mu parameters are not relevant/effective here, but needed for the function call.
                    process = subprocess.call(cmdForPvtu2vtuConverter, shell=True)
                    print('\n')
                    print colored('Pvtu2vtuConverter successfully finished.', 'green')
                    print colored('======================================== \n', 'green')
                    
                    # 3.) Run RMSE-value-Compute-Script, in order to compute the RMSE-value 
                    # for the respective TestAction-deformedCoords obtained from the Pvtu2vtu-Converter, ...
                    # Therefore, read the vtk-xml-tree of the deformedCoords and extract the coords list, i.e. "nodes_numpy_array_simdata", 
                    # in order to append it to a stored nodes_numpy_array_simdata-list.
                    # Then compare the 'simulation results' with the 'real data' and compute the RMSE value, 
                    # and return the RMSE-value (and additionally append/store the RMSE-value to a stored RMSE-values-list):
                    #cmdForRMSEvalueComputeScript = 'python RL_RMSEvalueComputeScriptOLD.py RL_TestSimResults/ Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu %s' % str(stepnum)
                    #process = subprocess.call(cmdForRMSEvalueComputeScript, shell=True)
                    #rmse_value_out = subprocess.check_output([sys.executable, cmdForRMSEvalueComputeScript])
                    rmse_value_out = RL_RMSEvalueComputeScript.rmsevalue_computer("RL_TestSimResults/", "Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", "TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", str(stepnum), str(action_number))
                    print('\n')
                    print colored("The RMSE value in Step %s for ActionNumber %s is: %s." % (stepnum, action_number, rmse_value_out), 'yellow') #... return value
                    print('\n')
                    print colored('RMSEvalueComputeScript successfully finished.', 'green')
                    print colored('============================================= \n', 'green')
                    
                    # Transfer RMSE-value into (the respective component = action_number of) the Q-value-Vector:
                    qValueVec[action_number] = rmse_value_out
                
                elif new_lam < 0.0:
                    # negative lambda-values are not permitted, hence reverse the above action, and give it a penalized Q-value.
                    new_lam = new_lam + epsilon_lam
                    parLambda = new_lam
                    param_lam.text = str(new_lam)
                    
                    # Penalize the Action and set a very bad Q-value:
                    qValueVec[action_number] = 10000.0
        
        
        # ========================================================
        # For MU: if action_number == 3 or action_number == 4:
        if action_number == 3:
            for param_mu in root.iter('mu'):
                prev_param_mu = float(param_mu.text)
                new_mu = prev_param_mu + epsilon_mu
                parMu = new_mu
                param_mu.text = str(new_mu)
                
                # Set up the respective TestAction-xml-inputfile for Action 3:
                outfilenamestring = infilenamestring[:-4] + '_TestAction' + str(action_number) + '.xml'
                print("The outfilenamestring for Action %s is: %s.\n" % (action_number, outfilenamestring))
                tree.write(outfilenamestring)
                
    #            parameter_set = [parLambda, parMu] #, parGrav]
    #            
    #            # Return or Store the action number in a list, or/and 
    #            # alternatively/additionally store the resulting parameter set:
    #            filename = 'state_list.txt'
    #            
    #            if os.path.exists(filename):
    #                append_write = 'a' # append if already exists
    #            else:
    #                append_write = 'w' # make a new file if not
    #            
    #            state_list_file = open(filename,append_write)
    #            #state_list_file.write("ActionNumber in Step " + str(stepnum) + ": " + str(action_number) + '\n')
    #            #state_list_file.write("ParameterSet in Step " + str(stepnum) + ": " + str(parameter_set) + '\n')
    #            state_list_file.close()
                
                # Subprocess Function Calls:
                process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True) # NOTE: probably not needed anymore.
                
                # 1.) Run Simulation-App with np=1 and with newly-defined TestAction-XML-Inputfile:
                cmdForSimulationRunner = "python RL_SimulationRunnerScript.py 1 " + outfilenamestring
                #print("CONTROL OUTPUT: The cmdForSimulationRunnerScript is: %s" % cmdForSimulationRunner)
                process = subprocess.call(cmdForSimulationRunner, shell=True)
                print('\n')
                print colored('SimulationRunner successfully finished.', 'green')
                print colored('======================================= \n', 'green')
                
                # 2.) Run Pvtu2vtu-Converter with obtained TestAction simulation results:
                cmdForPvtu2vtuConverter = 'python RL_Pvtu2vtuConverterAndVMStressCalculator.py RL_TestSimResults/ 140000 50000' 
                # note the lambda and mu parameters are not relevant/effective here, but needed for the function call.
                process = subprocess.call(cmdForPvtu2vtuConverter, shell=True)
                print('\n')
                print colored('Pvtu2vtuConverter successfully finished.', 'green')
                print colored('======================================== \n', 'green')
                
                # 3.) Run RMSE-value-Compute-Script, in order to compute the RMSE-value 
                # for the respective TestAction-deformedCoords obtained from the Pvtu2vtu-Converter, ...
                # Therefore, read the vtk-xml-tree of the deformedCoords and extract the coords list, i.e. "nodes_numpy_array_simdata", 
                # in order to append it to a stored nodes_numpy_array_simdata-list.
                # Then compare the 'simulation results' with the 'real data' and compute the RMSE value, 
                # and return the RMSE-value (and additionally append/store the RMSE-value to a stored RMSE-values-list):
                #cmdForRMSEvalueComputeScript = 'python RL_RMSEvalueComputeScriptOLD.py RL_TestSimResults/ Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu %s' % str(stepnum)
                #process = subprocess.call(cmdForRMSEvalueComputeScript, shell=True)
                #rmse_value_out = subprocess.check_output([sys.executable, cmdForRMSEvalueComputeScript])
                rmse_value_out = RL_RMSEvalueComputeScript.rmsevalue_computer("RL_TestSimResults/", "Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", "TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", str(stepnum), str(action_number))
                print('\n')
                print colored("The RMSE value in Step %s for ActionNumber %s is: %s." % (stepnum, action_number, rmse_value_out), 'yellow') #... return value
                print('\n')
                print colored('RMSEvalueComputeScript successfully finished.', 'green')
                print colored('============================================= \n', 'green')
                
                # Transfer RMSE-value into (the respective component = action_number of) the Q-value-Vector:
                qValueVec[action_number] = rmse_value_out
                
                
        if action_number == 4:
            for param_mu in root.iter('mu'):
                prev_param_mu = float(param_mu.text)
                new_mu = prev_param_mu - epsilon_mu
                
                if new_mu >= 0.0:
                    # positive mu-values are permitted, proceed as above in Action 1:
                    parMu = new_mu
                    param_mu.text = str(new_mu)
                    
                    # Set up the respective TestAction-xml-inputfile for Action 4:
                    outfilenamestring = infilenamestring[:-4] + '_TestAction' + str(action_number) + '.xml'
                    print("The outfilenamestring for Action %s is: %s.\n" % (action_number, outfilenamestring))
                    tree.write(outfilenamestring)
                    
    #            parameter_set = [parLambda, parMu] #, parGrav]
    #            
    #            # Return or Store the action number in a list, or/and 
    #            # alternatively/additionally store the resulting parameter set:
    #            filename = 'state_list.txt'
    #            
    #            if os.path.exists(filename):
    #                append_write = 'a' # append if already exists
    #            else:
    #                append_write = 'w' # make a new file if not
    #            
    #            state_list_file = open(filename,append_write)
    #            #state_list_file.write("ActionNumber in Step " + str(stepnum) + ": " + str(action_number) + '\n')
    #            #state_list_file.write("ParameterSet in Step " + str(stepnum) + ": " + str(parameter_set) + '\n')
    #            state_list_file.close()
                    
                    # Subprocess Function Calls:
                    process = subprocess.Popen('echo %USER:NICOLAI.SCHOCH%', stdout=PIPE, shell=True) # NOTE: probably not needed anymore.
                    
                    # 1.) Run Simulation-App with np=1 and with newly-defined TestAction-XML-Inputfile:
                    cmdForSimulationRunner = "python RL_SimulationRunnerScript.py 1 " + outfilenamestring
                    #print("CONTROL OUTPUT: The cmdForSimulationRunnerScript is: %s" % cmdForSimulationRunner)
                    process = subprocess.call(cmdForSimulationRunner, shell=True)
                    print('\n')
                    print colored('SimulationRunner successfully finished.', 'green')
                    print colored('======================================= \n', 'green')
                    
                    # 2.) Run Pvtu2vtu-Converter with obtained TestAction simulation results:
                    cmdForPvtu2vtuConverter = 'python RL_Pvtu2vtuConverterAndVMStressCalculator.py RL_TestSimResults/ 140000 50000' 
                    # note the lambda and mu parameters are not relevant/effective here, but needed for the function call.
                    process = subprocess.call(cmdForPvtu2vtuConverter, shell=True)
                    print('\n')
                    print colored('Pvtu2vtuConverter successfully finished.', 'green')
                    print colored('======================================== \n', 'green')
                    
                    # 3.) Run RMSE-value-Compute-Script, in order to compute the RMSE-value 
                    # for the respective TestAction-deformedCoords obtained from the Pvtu2vtu-Converter, ...
                    # Therefore, read the vtk-xml-tree of the deformedCoords and extract the coords list, i.e. "nodes_numpy_array_simdata", 
                    # in order to append it to a stored nodes_numpy_array_simdata-list.
                    # Then compare the 'simulation results' with the 'real data' and compute the RMSE value, 
                    # and return the RMSE-value (and additionally append/store the RMSE-value to a stored RMSE-values-list):
                    #cmdForRMSEvalueComputeScript = 'python RL_RMSEvalueComputeScriptOLD.py RL_TestSimResults/ Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu %s' % str(stepnum)
                    #process = subprocess.call(cmdForRMSEvalueComputeScript, shell=True)
                    #rmse_value_out = subprocess.check_output([sys.executable, cmdForRMSEvalueComputeScript])
                    rmse_value_out = RL_RMSEvalueComputeScript.rmsevalue_computer("RL_TestSimResults/", "Beam_REALDATA_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", "TestRL_Beam_solution_np1_RefLvl0_Tstep.0010_outVis.vtu", str(stepnum), str(action_number))
                    print('\n')
                    print colored("The RMSE value in Step %s for ActionNumber %s is: %s." % (stepnum, action_number, rmse_value_out), 'yellow') #... return value
                    print('\n')
                    print colored('RMSEvalueComputeScript successfully finished.', 'green')
                    print colored('============================================= \n', 'green')
                    
                    # Transfer RMSE-value into (the respective component = action_number of) the Q-value-Vector:
                    qValueVec[action_number] = rmse_value_out
                
                elif new_mu < 0.0:
                    # negative mu-values are not permitted, hence reverse the above action, and give it a penalized Q-value.
                    new_mu = new_mu + epsilon_mu
                    parMu = new_mu
                    param_mu.text = str(new_mu)
                    
                    # Penalize the Action and set a very bad Q-value:
                    qValueVec[action_number] = 10000.0
        
        
    # ======================================================
    # For GRAV: if action_number == 5 or action_number == 6:
    #for param_grav in root.iter('gravity'):
    #    prev_param_grav = float(param_grav.text)
    #    parGrav = prev_param_grav
    #    if action_number == 5:
    #        new_grav = prev_param_grav + epsilon_grav
    #        if new_grav > 0.0: # positive gravity is not permitted, hence reverse the above action, and then go to "if action_number == 6:" ...
    #            new_grav = new_grav - epsilon_grav
    #            action_number = 6
    #        parGrav = new_grav
    #        param_grav.text = str(new_grav)
    #    if action_number == 6:
    #        new_grav = prev_param_grav - epsilon_grav
    #        parGrav = new_grav
    #        param_grav.text = str(new_grav)
        
        print("ActionSpace for Step %s further simulated/computed, i.e., Q-value vector further updated." % stepnum)
        print("Q-value Vector (in Step %s):\n ===> [%s,%s,%s,%s,%s]. \n\n" % (stepnum, qValueVec[0],qValueVec[1],qValueVec[2],qValueVec[3],qValueVec[4]))
    
    
    print colored("ActionSpace for Step %s entirely computed/simulated, i.e., Q-value vector fully updated.\n" % stepnum, 'yellow')
    
    
    # Analyze Q-value-vector, choose the best Q-value, and perform the respective action 
    # (i.e., fill the respective newly defined parameter into the xml-inputfile):
    
    # 1.) Analyze Q-value-vector: find the component (action_number) with the smallest RMSE-value:
    q_min_index = 100
    q_min = 100000.0
    for ind,val in enumerate(qValueVec):
        if val < q_min:
            q_min = val
            q_min_index = ind
    print colored("The Q-value Vector has been analyzed, and the best Action was found to be: action_number = %s. \n" % q_min_index, 'yellow')
    if q_min_index == 0:
        print colored("The (locally) best solution, i.e., the best parameter combination for the given first-guess-initialization, has been found. PROGRAM FINISHED. \n", 'red')
        print colored("Please note: It may be reasonable to re-initialize the program with another first guess in order to obtain another (possibly better) local solution. \n\n", 'red')
        # NOTE: break # Program finished.
        # Either break or exit, OR return action_number 0 to calling script and then stop "while"-loop in calling script.
        #raise Exception("End!")
        #sys.exit('End!')
        #exit('END')
        #quit()
    
    
    # 2.) Execute the respectively best action_number, i.e., update the xml-inputfile with the respectively newly defined parameter:
    # Reset parLambda and parMu:
    parLambda = 0.0
    parMu = 0.0
    
    # According to the above selected action-number, conduct an action in the tree below:
    #print("ControlOutput: infilenamestring = %s." % str(infilenamestring))
    tree = ET.parse(infilenamestring)
    root = tree.getroot()
    
    # Recompute them according to the q_min_index:
    if q_min_index == 1 or q_min_index == 2:
        for param_mu in root.iter('mu'):
            parMu = float(param_mu.text)
        for para_lam in root.iter('lambda'):
            prev_para_lam = float(para_lam.text)
            #print("Prev_para_lam = %s." % prev_para_lam)
            #parLambda = prev_para_lam
            if q_min_index == 1:
                new_lam = prev_para_lam + epsilon_lam
                parLambda = new_lam
                para_lam.text = str(new_lam)
            if q_min_index == 2:
                new_lam = prev_para_lam - epsilon_lam
                if new_lam < 0.0:
                    #print("Attention: negative Lambda value.")
                    # negative lambda-values are not permitted, hence reverse the above action #, and then go to "if action_number == 1:" ...
                    new_lam += epsilon_lam
                    #action_number = 1
                    #new_lam += epsilon_lam
                parLambda = new_lam
                para_lam.text = str(new_lam)
            #print("New Para_lam = %s." % para_lam.text)
    
    if q_min_index == 3 or q_min_index == 4:
        for param_lam in root.iter('lambda'):
            parLambda = float(param_lam.text)
        for para_mu in root.iter('mu'):
            prev_para_mu = float(para_mu.text)
            #print("Prev_para_mu = %s." % prev_para_mu)
            #parMu = prev_para_mu
            if q_min_index == 3:
                new_mu = prev_para_mu + epsilon_mu
                parMu = new_mu
                para_mu.text = str(new_mu)
            if q_min_index == 4:
                new_mu = prev_para_mu - epsilon_mu
                if new_mu < 0.0:
                    #print("Attention: negative Mu value.")
                    # negative mu-values are not permitted, hence reverse the above action. #, and then go to "if action_number == 3:" ...
                    new_mu += epsilon_mu
                    #action_number = 3
                    #new_mu += epsilon_mu
                parMu = new_mu
                para_mu.text = str(new_mu)
            #print("New Para_mu = %s." % para_mu.text)
    
    #if q_min_index == 5 or q_min_index == 6:
    #    for param_grav in root.iter('gravity'):
    #        prev_param_grav = float(param_grav.text)
    #        #parGrav = prev_param_grav
    #        if q_min_index == 5:
    #            new_grav = prev_param_grav + epsilon_grav
    #            if new_grav > 0.0: # positive gravity is not permitted, hence reverse the above action, and then go to "if action_number == 6:" ...
    #                new_grav = new_grav - epsilon_grav
    #                action_number = 6
    #            parGrav = new_grav
    #            param_grav.text = str(new_grav)
    #        if q_min_index == 6:
    #            new_grav = prev_param_grav - epsilon_grav
    #            parGrav = new_grav
    #            param_grav.text = str(new_grav)
    
    tree.write(infilenamestring)
    
    # Store parameter-set development and action_number development in a separate list file:
    parameter_set = [parLambda, parMu] #, parGrav]
    
    # Return or Store the action number in a list, or/and 
    # alternatively/additionally store the resulting parameter set:
    filename = 'RL_state_list.txt'
    
    if os.path.exists(filename):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    
    state_list_file = open(filename,append_write)
    state_list_file.write("Chosen ActionNumber in Step " + str(stepnum) + "   :  " + str(q_min_index) + '\n')
    state_list_file.write("Produced ParameterSet in Step " + str(stepnum) + " :  " + str(parameter_set) + '\n')
    state_list_file.close()
    
    print('QvalueComputeScript successfully finished in Step %s.' % stepnum)
    
    # return the action_number (in terms of the q_min_index)
    return q_min_index


if __name__ == '__main__':
    print('\n')
    print colored('QvalueComputeFunction STARTED. \n', 'yellow')
    qvalue_computer(sys.argv[1],sys.argv[2])
    print('\n')
    print colored('QvalueComputeFunction FINISHED. \n', 'yellow')
