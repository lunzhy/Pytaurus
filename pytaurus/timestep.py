__author__ = 'lunzhy'
import math, os, sys
import numpy as np
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen
import pytaurus.env as env

def _genISPP(volStart, volEnd, startTime=1e-8, endTime=1e-4, timeStep=5, volStep=1):
    """

    @param volStart:
    @param volEnd:
    @param startTime:
    @param endTime:
    @param timeStep:
    @param volStep:
    @return: (time, vol_gate1, vol_gate2, vol_gate3)
    """
    # step time 1us, step 1V
    time_list, vg1_list, vg2_list, vg3_list = [], [], [], []
    startTime_exp = int(math.log10(startTime))
    endTime_exp = int(math.log10(endTime))
    time_vth_list = []
    vg1, vg3 = 0, 0
    time_offset = 0
    vg2_internal = np.arange(volStart, volEnd+1, 1)
    for vg2 in vg2_internal:
        time_internal = np.logspace(startTime_exp, endTime_exp, timeStep*(endTime_exp-startTime_exp)+1)
        for timestep in time_internal:
            time_total = time_offset + timestep
            time_vth_list.append((time_total, vg1, vg2, vg3))
        time_offset += math.pow(10, endTime_exp)
    # for index, time_vth in enumerate(time_vth_list):
    #     print('%s\t\t%.8e\t\t%.5f\t\t%.5f\t\t%.5f' % ((index+1,) + time_vth))
    return time_vth_list


def _sidePrgCenterPrg(prgVol=16, passVol=8, prgTime=200e-6):
    time_vth_list = []
    time_offset = 0
    start_time_exp = -8
    steps = (math.log10(prgTime) - start_time_exp) * 6
    time_single = np.logspace(start_time_exp, math.log10(prgTime), steps)
    # side programming
    vg1 = prgVol
    vg2 = passVol
    vg3 = prgVol
    for timestep in time_single:
        time_total = time_offset + timestep
        time_vth_list.append((time_total, vg1, vg2, vg3))
    # center programming
    vg1 = passVol
    vg2 = prgVol
    vg3 = passVol
    time_offset += prgTime
    for timestep in time_single:
        time_total = time_offset + timestep
        time_vth_list.append((time_total, vg1, vg2, vg3))
    return time_vth_list


def _retentionAfterPrg(prgVol=16, prgTime=200e-6, retTime=1e6):
    time_vth_list = _sidePrgCenterPrg(prgVol=prgVol, prgTime=prgTime, passVol=0)
    time_offset = time_vth_list[-1][0]
    # 10-2 -> 1e4
    time_retention = np.logspace(-2, 4, 60)
    for timestep in time_retention:
        time_total = time_offset + timestep
        time_vth_list.append((time_total, 0, 0, 0))
    # 1e4 -> 1e6
    time_offset = time_vth_list[-1][0]
    time_retention = np.linspace(1e4, retTime-1e4, 100)
    for timestep in time_retention:
        time_total = time_offset + timestep
        time_vth_list.append((time_total, 0, 0, 0))
    return time_vth_list


def _sidePrg(prgVol=16, passVol=8, prgTime=0.01):
    time_vth_list = []
    time_offset = 0
    start_time_exp = -8
    steps = (math.log10(prgTime) - start_time_exp) * 6
    time_single = np.logspace(start_time_exp, math.log10(prgTime), steps)
    # side programming
    vg1 = prgVol
    vg2 = passVol
    vg3 = prgVol
    for timestep in time_single:
        time_total = time_offset + timestep
        time_vth_list.append((time_total, vg1, vg2, vg3))
    return time_vth_list
    return


def _readDisturb(readTime=1e6, readVol=6, isSidePrg=True):
    time_vth_list = _sidePrg() if isSidePrg is True else []
    start_time_exp = -2
    steps = (math.log10(readTime) - start_time_exp) * 10
    time_single = np.logspace(start_time_exp, math.log10(readTime), steps)
    time_offset = time_vth_list[-1][0] if not len(time_vth_list) == 0 else 0
    for timestep in time_single:
        time_total = time_offset + timestep
        time_vth_list.append((time_total, readVol, readVol, readVol))
    return time_vth_list


def _genTimestep():
    # time_vth_list = _genISPP(8, 18)
    # time_vth_list = _sidePrgCenterPrg(prgTime=1e-2)
    # time_vth_list = _retentionAfterPrg()
    time_vth_list = _readDisturb(isSidePrg=True, readVol=0)
    return time_vth_list


def writeTimestepFile(prjPath):
    file_path = os.path.join(prjPath, sen.TimeStep_File)
    time_vth_list = _genTimestep()
    with open(file_path, 'w') as timestep_file:
        timestep_file.write('Step\t\tTime [s]\t\tVgate1 [V]\tVgate2 [V]\t\tVgate3 [V]\n')
        for index, time_vth in enumerate(time_vth_list):
            timestep_file.write('%s\t\t%.8e\t\t%.5f\t\t%.5f\t\t%.5f\n' % ((index + 1,) + time_vth))


def _printTimestep():
    time_vth_list = _genTimestep()
    for index, time_vth in enumerate(time_vth_list):
        print(index+1, time_vth)
    return


if __name__ == '__main__':
    _printTimestep()
    # writeTimestepFile(env.Debug_Directory)