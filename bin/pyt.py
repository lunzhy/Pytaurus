#!/usr/bin/python
import os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)

from pytaurus import tools
import pytaurus.env as env
import pytaurus.sentaurus as sen
import pytaurus.sentaurus.sse as sse
import pytaurus.sentaurus.sde as sde
import pytaurus.sentaurus.inspect as inspect
import pytaurus.sentaurus.callsent as callsent
import pytaurus.sentaurus.extract as extr

Effective_argument = ['clean', 'prepare', 'structure', 'solve', 'solvevth']
# the argument list
# pyt clean [project_path]                      | clean the files except the remained in this folder
# pyt prepare [project_path]                    | mkdir all the folders needed by the SimCTM
# pyt structure [project_path]                  | build structure using sentanrus
# pyt solve [prject_path]                       | run the simulation prject in this folder
# pyt solvevth [project_path] [time_list]       | solve vth using sentaurus of the project


def isSolveVthTime(time):
    return tools.isMajorTime(time)


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


def senSolveVth(prj_path, trip_cells):
    files_name = os.listdir(os.path.join(prj_path, sen.Folder_Substrate))
    files_path = [os.path.join(prj_path, sen.Folder_Substrate, file) for file in files_name]
    files_path_sorted = sorted(files_path ,key=lambda x: os.path.getmtime(x))
    for file_path in files_path_sorted:
        if not sen.Charge_File_Prefix in file_path:
            continue
        time = tools.parseSimTime(file_path)
        if isSolveVthTime(time) is False:
            continue
        # copy charge file before call sdevice
        sde.copyChargeFile(prj_path, file_path)
        sde_cmd = sde.SdeCmdFile(trip_cells, solve_vth=True)
        sde_cmd.build()
        callsent.callSdevice(sde_cmd)
        # deal with inspect
        ins_cmd = inspect.InspectCmdFile(trip_cells)
        ins_cmd.build()
        output = callsent.callInspect(ins_cmd)
        voltage = extr.extractVth(output)
        print('\nVth of %.3e : %.3f\n' % (time, voltage))
        ins_cmd.writeVth(time, voltage)
    return


def senSolveVthSingleTime(prj_path, trip_cells, time):
    substrate_folder = os.path.join(prj_path, sen.Folder_Substrate)
    file_path = tools.searchFilePathByTime(substrate_folder, sen.Charge_File_Prefix, time)
    # copy charge file before call sdevice
    sde.copyChargeFile(prj_path, file_path)
    sde_cmd = sde.SdeCmdFile(trip_cells, solve_vth=True)
    sde_cmd.build()
    callsent.callSdevice(sde_cmd)
    # deal with inspect
    ins_cmd = inspect.InspectCmdFile(trip_cells)
    ins_cmd.build()
    output = callsent.callInspect(ins_cmd)
    voltage = extr.extractVth(output)
    print('\nVth of %.3e : %.3f\n' % (time, voltage))
    ins_cmd.writeVth(time, voltage)
    return



def main():
    argc = len(sys.argv)
    if argc == 3:
        mode = sys.argv[1]
        prj_path = sys.argv[2]
        if not os.path.isabs(prj_path):
            # SimCTM sends only the project name
            prj_path = os.path.join(os.path.abspath(os.curdir), prj_path)
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
        elif mode == 'solvevth':
            senSolveVth(prj_path, trip_cells)
        else:
            print('Wrong argument keyword.')
            return
    elif argc >= 4:
        mode = sys.argv[1]
        if not mode == 'solvevth':
            print('Wrong argument keyword')
            return
        prj_path = sys.argv[2]
        if not os.path.isabs(prj_path):
            # SimCTM sends only the project name
            prj_path = os.path.join(os.path.abspath(os.curdir), prj_path)
        trip_cells = buildTrpileCell(prj_path)
        time_list =[float(time) for time in sys.argv[3:]]
        for time in time_list:
            senSolveVthSingleTime(prj_path, trip_cells, time)
    else:
        print('Wrong number of argument.')
    return


if __name__ == '__main__': main()