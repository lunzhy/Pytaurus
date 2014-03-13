__author__ = 'lunzhy'
import os, sys
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.platform as platform
import pytaurus.sentaurus.sse as sse
import pytaurus.sentaurus.sde as sde
import pytaurus.sentaurus.callsent as callsent


def test_debug():
    trip_cells = sse.TripleCells(platform.Debug_Directory)
    trip_cells.build()
    #sse_cmd = sse.SseCmdFile(trip_cells)
    #sse_cmd.build()
    sde_cmd = sde.SdeCmdFile(trip_cells)
    sde_cmd.build()
    #callsent.callSse(sse_cmd)
    return


if __name__ == '__main__': test_debug()