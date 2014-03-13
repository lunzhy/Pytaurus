__author__ = 'Lunzhy'
import os, sys, re, shutil
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
if not path in sys.path:
    sys.path.append(path)
import collections
import pytaurus.sentaurus as sen


class SdeCmdFile():
    def __init__(self, triple_cell):
        self.params = {}
        self.points = {}
        self.triple_cell = triple_cell
        self.prj_path = triple_cell.prj_path
        file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 os.pardir, os.pardir, 'resources', sen.Resource_Sde_File))
        self.template_filepath = file_path
        self.cmd_lines = []
        self.cmd_filepath = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Sde_Cmd_File)
        return

    def build(self):
        self.readChannelVerts()
        self.setParameters()
        self.writeCmdFile()
        self.copyCmdFileToPrj()
        return

    def readChannelVerts(self):
        nm_in_um = 1e-3
        verts_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.ExDataFile_Channel)
        f = open(verts_filepath)
        for line in f.readlines()[1:]:
            values = re.split('\s+', line)
            id = int(values[0])
            # xCoord = float(values[1]) * nm_in_um
            # yCoord = float(values[2]) * nm_in_um
            xCoord = float('%se-3' % values[1])
            yCoord = float('%se-3' % values[2])
            self.points[id] = (xCoord, yCoord)
        sorted_list = sorted(self.points.items(), key=lambda x: x[0])
        self.points = collections.OrderedDict(sorted_list)
        f.close()
        return

    def setParameters(self):
        self.params['grid.tdr'] = sen.Tdr_File
        params_from_structure = ['tc.gate1.workfunction', 'tc.gate2.workfunction', 'tc.gate3.workfunction',
                                 'tc.gate1.voltage', 'tc.gate2.voltage', 'tc.gate3.voltage', 'tc.drain.voltage']
        for param in params_from_structure:
            self.params[param] = self.triple_cell.getParam(param)

        # set the points
        points = ''
        for key, coord_tup in self.points.items():
            points += ('\t\t%s\n' % (coord_tup,))
        self.params['points'] = points
        return

    def replaceLine(self, line):
        pattern = re.compile(r'%.*%')
        match = pattern.search(line)
        if match == None:
            return line
        else:
            param_name = match.group()[1:-1]
        value = self.params[param_name]
        new_line = re.sub(pattern, value, line)
        return new_line

    def createCmdLines(self):
        f = open(self.template_filepath)
        for line in f.readlines():
            new_line = self.replaceLine(line)
            self.cmd_lines.append(new_line)
        f.close()
        return

    def writeCmdFile(self):
        cmd_filepath = self.cmd_filepath
        f = open(cmd_filepath, 'w+')
        self.createCmdLines()
        f.writelines(self.cmd_lines)
        f.close()
        return

    def copyCmdFileToPrj(self):
        dirToCheck = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir,
                                  'out')

        shutil.copy(self.cmd_filepath, dirToCheck)
        return


def test():
    return

if __name__ == '__main__': test()