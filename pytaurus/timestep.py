__author__ = 'lunzhy'
import math, os, sys
import numpy as np
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen
import pytaurus.env as env

def _genISPP(volStart, volEnd, startTime=1e-8, endTime=1e-4, timeStep=5, volStep=1):
    # step time 1us, step 1V
    time_list, vg1_list, vg2_list, vg3_list = [], [], [], []
    startTime_exp = int(math.log10(startTime))
    endTime_exp = int(math.log10(endTime))
    time_vth_list = []
    vg1, vg3 = 0, 0
    time_offset = 0
    vg2_internal = np.arange(volStart, volEnd+1, 1)
    for vg2 in vg2_internal:
        time_internal = np.logspace(startTime_exp, endTime_exp, timeStep*(endTime_exp-startTime_exp))
        for timestep in time_internal:
            time_total = time_offset + timestep
            time_vth_list.append((time_total, vg1, vg2, vg3))
        time_offset += math.pow(10, endTime_exp)
    # for index, time_vth in enumerate(time_vth_list):
    #     print('%s\t\t%.8e\t\t%.5f\t\t%.5f\t\t%.5f' % ((index+1,) + time_vth))
    return time_vth_list


def _genTimestep():
    time_vth_list = _genISPP(8, 18)
    return time_vth_list


def writeTimestepFile(prjPath):
    file_path = os.path.join(prjPath, sen.TimeStep_File)
    time_vth_list = _genTimestep()
    with open(file_path, 'w') as timestep_file:
        timestep_file.write('Step\t\tTime [s]\t\tVgate1 [V]\tVgate2 [V]\t\tVgate3 [V]\n')
        for index, time_vth in enumerate(time_vth_list):
            timestep_file.write('%s\t\t%.8e\t\t%.5f\t\t%.5f\t\t%.5f\n' % ((index + 1,) + time_vth))


if __name__ == '__main__':
    writeTimestepFile(env.Debug_Directory)