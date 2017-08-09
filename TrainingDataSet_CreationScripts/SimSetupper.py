#######################################################################
# Python script for setting up a HiFlow3-based linear-elastic or corotation-based elasticity simulation
# using the beam bending scenario:
# 
# The script needs the following input:
#   .. parameter lambda:      ...
#   .. parameter mu: ...
#   .. parameter f_scale: ...
#   .. step-iteration-value: ...
# 
# Using the data specified above, the script sets up the respective HiFlow3 simulation input xml file.
# 
# The output is the following:
#   .. xml-file with specified parameters: ...
# 
# To run the script, call:
#   python SimSetupper.py <lambda-value> <mu-value> <step-iter-value>
# 
# Example:
#   python SimSetupper.py <lambda-value> <mu-value> <step-iter-value> 
# 
# authors = {Nicolai Schoch}
# dates = {2017-07-31}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-07-17"

import xml.etree.ElementTree as ET

#import numpy as np
#from numpy import linalg as LA

import sys
#import os

#import vtk

'''
Call SimSetupper by:
$ python SimSetupper.py <lambda-value> <mu-value> <step-iter-value>
'''

print('SimSetupper started.')

#infilenamestring = 'elastScen_BeamQuader_DirAndNeumBC.xml'

param_lambda = sys.argv[1]
param_mu = sys.argv[2]
step = sys.argv[3]
prevstep = int(step) - 1

#print('Prev step: ', prevstep)

infilenamestring = 'elastScen_Beam_DLstep' + str(prevstep) + '.xml'
outfilenamestring = 'elastScen_Beam_DLstep' + step + '.xml'

tree = ET.parse(infilenamestring)
root = tree.getroot()

for path in root.iter('OutputPathAndPrefix'):
    newpath = 'SimResults/' + outfilenamestring
    path.text = newpath

for param_lam in root.iter('lambda'):
    newlam = str(param_lambda)
    param_lam.text = newlam

for param_m in root.iter('mu'):
    newmu = str(param_mu)
    param_m.text = newmu

tree.write(outfilenamestring)



#def sim_setupper(param_lambda, param_mu, outfilename='elastSimScen'):
#    '''
#    Open xml-Simulation-Inputfile named filenamestring.
#    Manipulate in the xml tree the following parameters
#    : lambda : 
#    : mu :
#    and write the manipulated xml tree into a new file named outfilenamestring.
#    '''
#    
#    tree = ET.parse(infilenamestring)
#    root = tree.getroot()
#    
#    for path in root.iter('OutputPathAndPrefix'):
#        newpath = 'SimResults/' + outfilename
#        path.text = newpath
#    
#    for param_lam in root.iter('lambda'):
#        newlam = str(param_lambda)
#        param_lam.text = newlam
#    
#    for param_m in root.iter('mu'):
#        newmu = str(param_mu)
#        param_m.text = newmu
#    
#    tree.write(outfilenamestring)
#
#
## Call sim_setupper function with respective parameters:
#sim_setupper(1234, 5678, 'elasticitySimulationScenario')

print('SimSetupper successfully finished.')
