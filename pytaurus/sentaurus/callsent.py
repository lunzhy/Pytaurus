__author__ = 'lunzhy'
import os, sys, re, subprocess
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.platform as platform
import pytaurus.sentaurus as sen

def chdirToSentrun(prj_path):
    runsent_dir = os.path.join(prj_path, sen.Folder_Run_Sentaurus)
    os.chdir(runsent_dir)
    return


def callSse(sse_cmd):
    prj_path = sse_cmd.prj_path
    log_filepath = os.path.join(prj_path, 'sse_run.log')
    logfile = open(log_filepath, "w+")
    chdirToSentrun(prj_path)
    command = 'sde -e -l %s' % sen.Sse_Cmd_File
    output, error = subprocess.Popen(command.split(' '), stdout=logfile,
                                     stderr=subprocess.PIPE).communicate()
    return


def test():
    callSse(platform.Debug_Directory)


if __name__ == '__main__': test()