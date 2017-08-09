#######################################################################
# Python script for running the HiFlow3-based elasticity simulation application
# using the respective xml-Input-File:
# 
# The script needs the following input:
#   .. number of parallel processes: ...
#   .. path to xml input filename: ...
# 
# Using the data specified above, the script runs the respective HiFlow3 simulation application.
# 
# The output is the following:
#   .. simulation results in respective simulation output folder: ...
# 
# To run the script, call:
#   python SimulationRunner.py <num-para-proc> <path-to-xml-input-filename>
# 
# Example:
#    python SimulationRunner.py 2 elastScen_BeamQuader_DirAndNeumBC.xml 
# 
# author = {Nicolai Schoch}
# date = {2017-07-31}
#######################################################################


__author__ = 'schoch'
__date__ = "2017-07-31"

import os
import sys

print('=========================')
print('SimulationRunner started. \n')

try:
    os.makedirs("TestSimResults")
except:
    pass

numproc = sys.argv[1]
print('NumProc: %s.' % int(numproc))

xmlinputfile = sys.argv[2]

if int(numproc) == 1: # Run sequentially:
    HIFLOW_EXECUTABLE = './elasticity'
    cmd = "%s %s" % (HIFLOW_EXECUTABLE, xmlinputfile)
    print("Starting Execution of HiFlow3 Elasticity App in sequential mode: %s" % cmd)
    os.system(cmd)

if int(numproc) > 1: # Run HiFlow3-Elasticity-Simulation in parallel with np X:
    HIFLOW_EXECUTABLE = 'elasticity' # possibly add PATH; t.b. imported
    cmd = "%s %s %s %s" % ('mpirun -np', numproc, HIFLOW_EXECUTABLE, xmlinputfile)
    print("Starting Execution of HiFlow3 Elasticity App in parallel mode: %s" % cmd)
    os.system(cmd)

print('SimulationRunner successfully finished.')

#    def execute(self):
#        """Execute `run HiFlow3 Elasticity`
#
#        """
#        import msml.envconfig
#        import os
#
#        try:
#            os.makedirs("SimResults")
#        except:
#            pass
#
#        for scenefile in self.scenes:
#            
#            # get string 'numproc' from MSML-file:
#            numproc = self._msml_file.env.solver.numParallelProcessesOnCPU
#            
#            if numproc == "0": # Do not execute HiFlow3-Elasticity-Simulation.
#                cmd = "%s %s %s" % ('mpirun -np X', msml.envconfig.HIFLOW_EXECUTABLE, scenefile)
#                log.info("NOT executing HiFlow3 now, but providing command for execution: %s" % cmd)
#                
#                # write command to bashscript/textfile, in order to allow for later execution e.g. on HPC cluster.
#                with open("Hf3Esim_Command_for_Exec.sh", 'w') as f:
#                    # write bash script contents into file:
#                    f.write("#!/bin/bash \n %s" % (cmd))
#                
#                debug("Command for execution of HiFlow3-Elasticity-Simulation written into file 'Hf3Esim_Command_for_Exec.sh'.")
#                
#            elif numproc == "1": # Run HiFlow3-Elasticity-Simulation sequentially:
#                cmd = "%s %s" % (msml.envconfig.HIFLOW_EXECUTABLE, scenefile)
#                log.info("Executing HiFlow3 sequentially: %s" % cmd)
#                os.system(cmd)
#                
#            else: # if numproc > 1: # Run HiFlow3-Elasticity-Simulation in parallel with np X:
#                cmd = "%s %s %s %s" % ('mpirun -np', numproc, msml.envconfig.HIFLOW_EXECUTABLE, scenefile) # '/home/nschoch/Workspace/MSML/msml/examples/MitralValveExample/mvTest_20160118_vexec/' + scenefile)
#                log.info("Executing HiFlow3 in parallel: %s" % cmd)
#                os.system(cmd)
