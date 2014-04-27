__author__ = 'lunzhy'
import os, sys, re, shutil
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

class InspectCmdFile():
    def __init__(self, trip_cells):
        self.structure = trip_cells
        self.prj_path = trip_cells.prj_path
        self.params = {}
        file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 os.pardir, os.pardir, 'resources', sen.Resource_Ins_File))

        self.template_file = file_path
        self.cmd_file = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Inspect_Cmd_File)
        self.cmd_lines = []
        return

    def calcVthCurrent(self):
        nm_in_um = 1e-3
        channel_length = self.structure.getParam('tc.gate2.width')
        current = 1.0 / (float(channel_length) * nm_in_um) * 1e-7
        return current

    def setParameters(self):
        self.params['plt'] = sen.Plot_File
        self.params['vth.current'] = '%.3e' % self.calcVthCurrent()
        return

    def replaceLine(self, line):
        pattern = re.compile(r'%.*%')
        match = pattern.search(line)
        if match is None:
            return line
        else:
            param_name = match.group()[1:-1]
        value = self.params[param_name]
        new_line = re.sub(pattern, value, line)
        return new_line

    def createCmdLines(self):
        f = open(self.template_file)
        for line in f.readlines():
            new_line = self.replaceLine(line)
            self.cmd_lines.append(new_line)
        f.close()
        return

    def writeCmdFile(self):
        cmd_file = self.cmd_file
        f = open(cmd_file, 'w+')
        self.createCmdLines()
        f.writelines(self.cmd_lines)
        f.close()
        return

    def build(self):
        self.setParameters()
        self.writeCmdFile()
        return

    def writeVth(self, time, voltage):
        vth_file = os.path.join(self.prj_path, sen.Folder_Miscellaneous, sen.File_Vth)
        with open(vth_file, 'a+') as file:
            file.write('%e\t%s\n' % (time, voltage))
        return