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
import pytaurus.structure as structure

Effective_argument = ['clean', 'prepare', 'structure', 'solve', 'solvevth', 'parsevth']
# the argument list
# pyt clean [prj_path]                                      | clean the files except the remained in this folder
# pyt prepare [prj_path]                                    | mkdir all the folders needed by the SimCTM
# pyt structure [prj_path]                                  | build structure using sentanrus
# pyt solve [prj_path] [-vg1|vg2|vg3=0]                     | run the simulation prject in this folder, the gate
#                                                             voltage can be assigned
# pyt solvevth [prj_path] [cell('cell2')] [time_list]       | solve vth using sentaurus of the project
# pyt parsevth [prj_path]                                   | calculate vth through flatband shift of each time step


def isSolveVthTime(time):
    return tools.isMajorTime(time)


def buildTripleCell(prj_path, cell_structure='triple'):
    env.convertParamFile(prj_path)
    cells = structure.TripleCells(prj_path, cell_structure)
    cells.build()
    return cells


def senStructure(trip_cells):
    sse_cmd = sse.SseCmdFile(trip_cells)
    sse_cmd.build()
    callsent.callSse(sse_cmd)
    return trip_cells


def senPotential(prj_path, trip_cells, vg1=None, vg2=None, vg3=None):
    trip_cells.refreshGateVoltage(vg1, vg2, vg3)
    if sen.Cell_Structure == 'triple':
        sde_cmd = sde.SdeCmdFile(trip_cells)
    elif sen.Cell_Structure == 'triplefull':
        sde_cmd = sde.SdeCmdFileTripleFull(trip_cells)
    sde_cmd.build()
    callsent.callSdevice(sde_cmd)
    sde.movePlotFile(prj_path)
    extr.parsePlotFile(prj_path)
    return


def senSolveAllVth(prj_path, trip_cells, vth_cell):
    files_name = os.listdir(os.path.join(prj_path, sen.Folder_Substrate))
    files_path = [os.path.join(prj_path, sen.Folder_Substrate, file) for file in files_name]
    files_path_sorted = sorted(files_path, key=lambda x: os.path.getmtime(x))
    for file_path in files_path_sorted:
        if not sen.Charge_File_Prefix in file_path:
            continue
        time = tools.parseSimTime(file_path)
        if isSolveVthTime(time) is False:
            continue
        # copy charge file before call sdevice
        sde.copyChargeFile(prj_path, file_path)
        if sen.Cell_Structure == 'triple':
            sde_cmd = sde.SdeCmdFile(trip_cells, solve_vth=True)
        elif sen.Cell_Structure == 'triplefull':
            sde_cmd = sde.SdeCmdFileTripleFull(trip_cells, vth_cell)
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


def senSolveVthSingleTime(prj_path, trip_cells, time, vth_cell):
    substrate_folder = os.path.join(prj_path, sen.Folder_Substrate)
    file_path = tools.searchFilePathByTime(substrate_folder, sen.Charge_File_Prefix, time)
    # copy charge file before call sdevice
    sde.copyChargeFile(prj_path, file_path)
    if sen.Cell_Structure == 'triple':
        sde_cmd = sde.SdeCmdFile(trip_cells, solve_vth=True)
    elif sen.Cell_Structure == 'triplefull':
        sde_cmd = sde.SdeCmdFileTripleFull(trip_cells, vth_cell, vth_cell)
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


def senSolveVth(prj_path, cells, time_list, vth_cell='cell2'):
    if len(time_list) == 0:
        senSolveAllVth(prj_path, cells, vth_cell)
    else:
        for time in time_list:
            senSolveVthSingleTime(prj_path, cells, time, vth_cell)
    return


def senParseVth(prj_path, trip_cells):
    extr.parseVth(prj_path, trip_cells)
    return


def main():
    keyword = sys.argv[1]
    if not keyword in Effective_argument:
        print('[Error] Wrong argument keyword: %s' % keyword)
        return
    prj_path = sys.argv[2]
    # if not os.path.isabs(prj_path):
    #     # SimCTM sends only the project name,
    #     prj_path = os.path.join(os.path.abspath(os.curdir), prj_path)
    if not os.path.isdir(prj_path):
        print('[Error] Wrong project directory: %s' % prj_path)
        return
    trip_cells = buildTripleCell(prj_path, cell_structure=sen.Cell_Structure)
    if keyword == 'clean':
        tools.cleanProject(prj_path)
    elif keyword == 'prepare':
        tools.prepareProject(prj_path)
    elif keyword == 'structure':
        senStructure(trip_cells)
    elif keyword == 'solve':
        arg_list = sys.argv[3:]
        vg1, vg2, vg3 = None, None, None
        for vg_arg in arg_list:
            if '-vg1=' in vg_arg:
                vg1 = vg_arg[5:]
            elif '-vg2=' in vg_arg:
                vg2 = vg_arg[5:]
            elif '-vg3=' in vg_arg:
                vg3 = vg_arg[5:]
        senPotential(prj_path, trip_cells, vg1=vg1, vg2=vg2, vg3=vg3)
    elif keyword == 'solvevth':
        if len(sys.argv) == 3:
            senSolveVth(prj_path, [], trip_cells)
        else:
            if 'cell' in sys.argv[3]:
                target_cell = sys.argv[3]
                time_list = [float(time) for time in sys.argv[4:]]
                senSolveVth(prj_path, trip_cells, time_list, target_cell)
            else:
                time_list = [float(time) for time in sys.argv[3:]]
                senSolveVth(prj_path, trip_cells, time_list)

    elif keyword == 'parsevth':
        senParseVth(prj_path, trip_cells)
    else:
        print('Wrong argument keyword.')
        return

    return


if __name__ == '__main__': main()