#!/usr/bin/python
import os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)

from pytaurus import tools
import pytaurus.env as env
import pytaurus.sentaurus.sse as sse
import pytaurus.sentaurus.sde as sde
import pytaurus.sentaurus.callsent as callsent
import pytaurus.sentaurus.extract as extr

Effective_argument = ['clean', 'prepare', 'structure', 'solve', 'solvevth']
# the argument list
# pyt clean [project_path]              | clean the files except the remained in this folder
# pyt prepare [project_path]            | mkdir all the folders needed by the SimCTM
# pyt structure [project_path]          | build structure using sentanrus
# pyt solve [prject_path]               | run the simulation prject in this folder
# pyt solvevth [project_path]           | solve vth using sentaurus of the project


def buildTrpileCell(prj_path):
    env.convertParamFile(prj_path)
    trip_cells = sse.TripleCells(prj_path)
    trip_cells.build()
    return trip_cells


def senStructure(prj_path, trip_cells):
    sse_cmd = sse.SseCmdFile(trip_cells)
    sse_cmd.build()
    callsent.callSse(sse_cmd)
    return trip_cells


def senPotential(prj_path, trip_cells):
    sde_cmd = sde.SdeCmdFile(trip_cells)
    sde_cmd.build()
    callsent.callSdevice(sde_cmd)
    sde.movePlotFile(prj_path)
    extr.parsePlotFile(prj_path)
    return


def main():
    argc = len(sys.argv)
    if argc == 3:
        mode = sys.argv[1]
        prj_path = sys.argv[2]
        if mode in Effective_argument:
            trip_cells = buildTrpileCell(prj_path)
        if mode == 'clean':
            tools.cleanProject(prj_path)
        elif mode == 'prepare':
            tools.prepareProject(prj_path)
        elif mode == 'structure':
            senStructure(prj_path, trip_cells)
        elif mode == 'solve':
            senPotential(prj_path, trip_cells)
        else:
            print('Wrong argument keyword.')
    else:
        print('Wrong number of argument.')
    return


if __name__ == '__main__': main()