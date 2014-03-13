__author__ = 'lunzhy'
import os, sys
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.platform as platform
import pytaurus.sentaurus as sen
import pytaurus.sentaurus.sse as sse
import pytaurus.sentaurus.sde as sde
import pytaurus.sentaurus.callsent as callsent

def cleanDebugEnv():
    logfile_path = os.path.join(platform.Debug_Directory, sen.Logfile_Sse)
    if os.path.exists(logfile_path):
        os.remove(logfile_path)
    sentrun_path = os.path.join(platform.Debug_Directory, sen.Folder_Run_Sentaurus)
    for file in os.listdir(sentrun_path):
        file_path = os.path.join(sentrun_path, file)
        os.remove(file_path)
    return

def test_debug():
    cleanDebugEnv()
    trip_cells = sse.TripleCells(platform.Debug_Directory)
    trip_cells.build()
    sse_cmd = sse.SseCmdFile(trip_cells)
    sse_cmd.build()
    sde_cmd = sde.SdeCmdFile(trip_cells)
    sde_cmd.build()
    callsent.callSse(sse_cmd)
    callsent.callSdevice(sde_cmd)
    return


if __name__ == '__main__': test_debug()