__author__ = 'lunzhy'
import os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.env as env
import pytaurus.sentaurus as sen
import pytaurus.sentaurus.sse as sse
import pytaurus.sentaurus.sde as sde
import pytaurus.sentaurus.callsent as callsent
import pytaurus.sentaurus.extract as extr

def cleanDebugEnv():
    # clean the log file
    logfile_paths = [os.path.join(env.Debug_Directory, sen.Logfile_Sse),
                    os.path.join(env.Debug_Directory, sen.Logfile_Sdevice)]
    for log_file in logfile_paths:
        if os.path.exists(log_file):
            os.remove(log_file)

    #clean sentaurus running folder
    sentrun_path = os.path.join(env.Debug_Directory, sen.Folder_Run_Sentaurus)
    for file in os.listdir(sentrun_path):
        file_path = os.path.join(sentrun_path, file)
        os.remove(file_path)

    #clean data exchage
    exchange_path = os.path.join(env.Debug_Directory, sen.Folder_Exchange_Data)
    for file in os.listdir(exchange_path):
        if not file == sen.Charge_File and not file == sen.Points_Location_Subs:
            file_path = os.path.join(exchange_path, file)
            os.remove(file_path)
    return

def test_debug():
    cleanDebugEnv()
    debug_prj_path = env.Debug_Directory
    env.convertParamFile(debug_prj_path)
    trip_cells = sse.TripleCells(debug_prj_path)
    trip_cells.build()
    sse_cmd = sse.SseCmdFile(trip_cells)
    sse_cmd.build()
    sde_cmd = sde.SdeCmdFile(trip_cells)
    sde_cmd.build()
    callsent.callSse(sse_cmd)
    callsent.callSdevice(sde_cmd)
    sde.movePlotFile(debug_prj_path)
    extr.parsePlotFile(debug_prj_path)
    return


if __name__ == '__main__': test_debug()