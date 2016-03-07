__author__ = 'lunzhy'
import os, sys, re, subprocess
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.env as platform
import pytaurus.sentaurus as sen

def chdirToSentrun(prj_path):
    runsent_dir = os.path.join(prj_path, sen.Folder_Run_Sentaurus)
    os.chdir(runsent_dir)
    return


def callSse(sse_cmd):
    prj_path = sse_cmd.prj_path
    log_filepath = os.path.join(prj_path, sen.Logfile_Sse)
    # logfile = open(log_filepath, 'w+')
    work_dir = os.getcwd()
    chdirToSentrun(prj_path)
    # command = 'sde -e -l %s' % sen.Sse_Cmd_File
    command = 'sde -e -l %s' % os.path.basename(sse_cmd.cmd_filepath)
    subprocess.call(command.split(' '))
    # output = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE).communicate()[0]
    # print(output.decode('utf-8'))
    # subprocess.check_output(command.split(' '))
    # logfile.close()
    os.chdir(work_dir)  # it is important to change back
    return


def callSdevice(sde_cmd):
    prj_path = sde_cmd.prj_path
    log_filepath = os.path.join(prj_path, sen.Logfile_Sdevice)
    # logfile = open(log_filepath, 'w+')
    work_dir = os.getcwd()
    chdirToSentrun(prj_path)
    command = 'sdevice %s' % os.path.basename(sde_cmd.cmd_filepath)
    subprocess.call(command.split(' '))
    # logfile.close()
    os.chdir(work_dir)  # it is important to change back
    return


def callInspect(ins_cmd):
    prj_path = ins_cmd.prj_path
    work_dir = os.getcwd()
    chdirToSentrun(prj_path)
    print('\nExtracting threshold voltage.\n')
    command = 'inspect -batch -f %s' % sen.Inspect_Cmd_File
    output = subprocess.check_output(command.split(' '))
    output_str = output.decode(encoding='UTF-8')
    os.chdir(work_dir)  # it is important to change back
    return output_str

def test():
    callSse(platform.Debug_Directory)
    callSdevice(platform.Debug_Directory)


if __name__ == '__main__': test()