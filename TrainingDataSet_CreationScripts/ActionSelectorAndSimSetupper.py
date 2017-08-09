#######################################################################
# Python script for random-selecting an Action (which corresponds to a manipulation of the XML Inputfile parameter value set)
# and for then updating the HiFlow3-XML-Inputfile with the respectively new parameter value set.
# 
# The script needs the following input:
#   .. the previous scenario's xml inputfile:      ...
# 
# Using the data specified above, the script sets up the respectively next HiFlow3 simulation xml-inputfile with randomly manipulated new parameters.
# 
# The output is the following:
#   .. the following scenario's xml-file with the newly specified/manipulated parameters: ...
# 
# To run the script, call:
#   python ActionSelectorAndSimSetupper.py <previous-xml-inputfile>
# 
# Example:
#   python ActionSelectorAndSimSetupper.py elastScen_Beam_ActionSelector_TestInput.xml
# 
# author = {Nicolai Schoch}
# date = {2017-07-31}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-07-31"

import sys
import os
import xml.etree.ElementTree as ET
from random import randint


print('=====================================')
print('ActionSelectorAndSimSetupper started. \n')

infilenamestring = sys.argv[1] # 'elastScen_BeamQuader_DirAndNeumBC.xml'
stepnum = sys.argv[2]
#param_lambda = sys.argv[1]
#param_mu = sys.argv[2]
#step = sys.argv[3]
#prevstep = int(step) - 1

#infilenamestring = 'elastScen_Beam_DLstep' + str(prevstep) + '.xml'
#outfilenamestring = 'elastScen_Beam_DLstep' + step + '.xml'

parLambda = 0.0
parMu = 0.0
parGrav = 0.0

# Set manipulation (epsilon) values:
epsilon_lam = 5000.0
epsilon_mu = 3000.0
epsilon_grav = 0.5

# Random Function to random-select an action-number out of [1,2,3,4,5,6,7]:
action_number = randint(1,7)
print("The action number in Step %s is: %s." % (stepnum, action_number))

# According to the above selected action-number, conduct an action in the tree below:
tree = ET.parse(infilenamestring)
root = tree.getroot()

#if action_number == 1 or action_number == 2:
for param_lam in root.iter('lambda'):
    prev_param_lam = float(param_lam.text)
    parLambda = prev_param_lam
    if action_number == 1:
        new_lam = prev_param_lam + epsilon_lam
        parLambda = new_lam
        param_lam.text = str(new_lam)
    if action_number == 2:
        new_lam = prev_param_lam - epsilon_lam
        if new_lam < 0.0: # negative lambda-values are not permitted, hence reverse the above action, and then go to "if action_number == 1:" ...
            new_lam = new_lam + epsilon_lam
            #action_number = 1
            new_lam += epsilon_lam
        parLambda = new_lam
        param_lam.text = str(new_lam)

#if action_number == 3 or action_number == 4:
for param_mu in root.iter('mu'):
    prev_param_mu = float(param_mu.text)
    parMu = prev_param_mu
    if action_number == 3:
        new_mu = prev_param_mu + epsilon_mu
        parMu = new_mu
        param_mu.text = str(new_mu)
    if action_number == 4:
        new_mu = prev_param_mu - epsilon_mu
        if new_mu < 0.0: # negative mu-values are not permitted, hence reverse the above action, and then go to "if action_number == 3:" ...
            new_mu = new_mu + epsilon_mu
            #action_number = 3
            new_mu += epsilon_mu
        parMu = new_mu
        param_mu.text = str(new_mu)

#if action_number == 5 or action_number == 6:
for param_grav in root.iter('gravity'):
    prev_param_grav = float(param_grav.text)
    parGrav = prev_param_grav
    if action_number == 5:
        new_grav = prev_param_grav + epsilon_grav
        if new_grav > 0.0: # positive gravity is not permitted, hence reverse the above action, and then go to "if action_number == 6:" ...
            new_grav = new_grav - epsilon_grav
            action_number = 6
        parGrav = new_grav
        param_grav.text = str(new_grav)
    if action_number == 6:
        new_grav = prev_param_grav - epsilon_grav
        parGrav = new_grav
        param_grav.text = str(new_grav)

tree.write(infilenamestring)

parameter_set = [parLambda, parMu, parGrav]

# Return or Store the action number in a list, or/and 
# alternatively/additionally store the resulting parameter set:
filename = 'state_list.txt'

if os.path.exists(filename):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not

state_list_file = open(filename,append_write)
state_list_file.write("ActionNumber in Step " + str(stepnum) + ": " + str(action_number) + '\n')
state_list_file.write("ParameterSet in Step " + str(stepnum) + ": " + str(parameter_set) + '\n')
state_list_file.close()

print('ActionSelectorAndSimSetupper successfully finished.')

