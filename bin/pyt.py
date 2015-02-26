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
import pytaurus.timestep as timestep

Effective_argument = ['clean', 'prepare', 'structure', 'solve', 'solvevth', 'parsevth', 'timestep', 'project',
                      'solvevth-nl', 'solvevth-empty']
# the argument list
# pyt clean [prj_path]                                      | clean the files except the remained in this folder
# pyt prepare [prj_path]                                    | mkdir all the folders needed by the SimCTM
# pyt structure [prj_path]                                  | build structure using sentanrus
# pyt solve [prj_path] [-vg1|vg2|vg3=0]                     | run the simulation prject in this folder, the gate
#                                                             voltage can be assigned
# pyt solvevth [prj_path] [cell('cell2')] [time_list]       | solve vth using sentaurus of the project
# pyt solvevth-nl [prj_path] [cell('cell2')] [time_list]    | solve vth using sentaurus of the project, remove the
# lateral charge of cell2
# pyt solvevth-empty [prj_path] [cell('cell2')] [time_list]    | solve vth using sentaurus of the project,
# remove all the charge
# pyt parsevth [prj_path]                                   | calculate vth through flatband shift of each time step
# pyt timestep [prj_path]                                   | generate time step input file
# pyt project [prj_path]                                    | generate project folders and files


def isSolveVthTime(time):
    return tools.isMajorTime(time)


def buildTripleCell(prj_path):
    env.convertParamFile(prj_path)
    cells = structure.TripleCells(prj_path)
    cells.build()
    return cells


def senStructure(trip_cells):
    sse_cmd = sse.SseCmdFile(trip_cells)
    sse_cmd.build()
    callsent.callSse(sse_cmd)
    return trip_cells


def senPotential(prj_path, trip_cells, vg1=None, vg2=None, vg3=None):
    trip_cells.refreshGateVoltage(vg1, vg2, vg3)
    sde_cmd = sde.SdeCmdFile(trip_cells)
    sde_cmd.build()
    callsent.callSdevice(sde_cmd)
    sde_cmd.move_plot_file()
    extr.parsePlotFile(prj_path)
    return


def senInspect(triple_cells, time, vth_cell):
    # deal with inspect
    ins_cmd = inspect.InspectCmdFile(triple_cells, vth_cell)
    ins_cmd.build()
    output = callsent.callInspect(ins_cmd)
    voltage = extr.extractVth(output)
    print('\nVth of %s at %.6e : %.3f\n' % (vth_cell, time, voltage))
    extr.writeVth(triple_cells.prj_path, time, voltage, vth_cell)
    return


def senSolveAllVth(prj_path, trip_cells, vth_cell, solve_type):
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
        sde_cmd = sde.SdeCmdFile(trip_cells, vth_cell, solve_type=solve_type)
        sde_cmd.build()
        callsent.callSdevice(sde_cmd)
        senInspect(trip_cells, time, vth_cell)
    return


def senSolveVthSingleTime(prj_path, trip_cells, time, vth_cell, solve_type):
    substrate_folder = os.path.join(prj_path, sen.Folder_Substrate)
    file_path = tools.searchFilePathByTime(substrate_folder, sen.Charge_File_Prefix, time)
    # copy charge file before call sdevice
    sde.copyChargeFile(prj_path, file_path)
    sde_cmd = sde.SdeCmdFile(trip_cells, vth_cell, solve_type=solve_type)
    sde_cmd.build()
    callsent.callSdevice(sde_cmd)
    senInspect(trip_cells, time, vth_cell)
    return


def senSolveVth(prj_path, cells, time_list, vth_cell='cell2', solve_type=None):
    if len(time_list) == 0:
        senSolveAllVth(prj_path, cells, vth_cell, solve_type)
    else:
        for time in time_list:
            senSolveVthSingleTime(prj_path, cells, time, vth_cell, solve_type)
    return


def senParseVth(prj_path, trip_cells):
    extr.parseVth(prj_path, trip_cells)
    return


def main():
    curr_arg_list = sys.argv[1:]
    keyword, curr_arg_list = curr_arg_list[0], curr_arg_list[1:]
    if keyword not in Effective_argument:
        print('[Error] Wrong argument keyword: %s' % keyword)
        return
    prj_path, curr_arg_list = curr_arg_list[0], curr_arg_list[1:]
    if keyword == 'project':
        tools.genProject(prj_path)
        return
    # if not os.path.isabs(prj_path):
    #     # SimCTM sends only the project name,
    #     prj_path = os.path.join(os.path.abspath(os.curdir), prj_path)
    if not os.path.isdir(prj_path):
        print('[Error] Wrong project directory: %s' % prj_path)
        return
    trip_cells = buildTripleCell(prj_path)  # triplefull

    if keyword == 'clean':
        tools.cleanProject(prj_path)

    elif keyword == 'prepare':
        tools.prepareProject(prj_path)

    elif keyword == 'structure':
        senStructure(trip_cells)

    elif keyword == 'solve':
        arg_list = curr_arg_list
        vg1, vg2, vg3 = None, None, None
        for vg_arg in arg_list:
            if '-vg1=' in vg_arg:
                vg1 = vg_arg[5:]
            elif '-vg2=' in vg_arg:
                vg2 = vg_arg[5:]
            elif '-vg3=' in vg_arg:
                vg3 = vg_arg[5:]
        senPotential(prj_path, trip_cells, vg1=vg1, vg2=vg2, vg3=vg3)

    elif 'solvevth' in keyword:
        if keyword == 'solvevth-nl':
            solve_type = 'nlateral'
        elif keyword == 'solvevth-empty':
            solve_type = 'empty'
        else:
            solve_type = None

        if len(curr_arg_list) == 0:
            senSolveVth(prj_path, curr_arg_list, trip_cells, solve_type=solve_type)
        else:
            if 'cell' in curr_arg_list[0]:
                target_cell, curr_arg_list = curr_arg_list[0], curr_arg_list[1:]
                time_list = [float(time) for time in curr_arg_list]
                senSolveVth(prj_path, trip_cells, time_list, target_cell, solve_type=solve_type)
            else:
                time_list = [float(time) for time in curr_arg_list]
                senSolveVth(prj_path, trip_cells, time_list, solve_type=solve_type)

    elif keyword == 'parsevth':
        senParseVth(prj_path, trip_cells)

    elif keyword == 'timestep':
        timestep.writeTimestepFile(prj_path)

    elif keyword == 'project':
        tools.genProject(prj_path)
    else:
        print('Wrong argument keyword.')
        return

    return


if __name__ == '__main__':
    main()