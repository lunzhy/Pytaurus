__author__ = 'Lunzhy'
import os, sys, re, shutil
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import collections
import pytaurus.sentaurus as sen


def movePlotFile(prj_path):
    origin_path = os.path.join(prj_path, sen.Folder_Run_Sentaurus, sen.Plot_File_Sentaurus)
    if not os.path.exists(origin_path):
        origin_path = os.path.join(prj_path, sen.Folder_Run_Sentaurus, sen.Plot_File_Init_Sentaurus)
    dst_path = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Plot_Subs_File)
    shutil.copy(origin_path, dst_path)
    return


def copyChargeFile(prj_path, charge_file):
    dst_path = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Charge_File)
    shutil.copy(charge_file, dst_path)
    return


class SdeCmdFile():
    def __init__(self, triple_cell, solve_vth=False):
        self.solve_vth = solve_vth
        self.params = {}
        self.channel_points = {}
        self.structure = triple_cell
        self.prj_path = triple_cell.prj_path
        if self.solve_vth is False:
            file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                     os.pardir, os.pardir, 'resources', sen.Resource_Sde_File))
        else:
            file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                     os.pardir, os.pardir, 'resources', sen.Resource_Sde_File_Vth))
        self.template_filepath = file_path
        self.cmd_lines = []
        self.lines_charge = ''
        self.cmd_filepath = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Sde_Cmd_File)
        return

    def build(self):
        self.readChannelVerts()
        self.readInterfaceCharge()
        self.setParameters()
        self.writeCmdFile()
        self.copyCmdFileToPrj()
        return

    def readChannelVerts(self):
        nm_in_um = 1e-3
        verts_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.Points_Location_Subs)
        f = open(verts_filepath)
        for line in f.readlines()[1:]:
            values = re.split('\s+', line)
            id = int(values[0])
            # xCoord = float(values[1]) * nm_in_um
            # yCoord = float(values[2]) * nm_in_um
            xCoord = float('%se-3' % values[1])
            yCoord = float('%se-3' % values[2])
            self.channel_points[id] = (xCoord, yCoord)
        sorted_list = sorted(self.channel_points.items(), key=lambda x: x[0])
        self.channel_points = collections.OrderedDict(sorted_list)
        f.close()
        return

    def setParameters(self):
        # tdr file
        self.params['grid.tdr'] = sen.Tdr_File

        # parameters from structure
        params_from_structure = ['tc.gate1.workfunction', 'tc.gate2.workfunction', 'tc.gate3.workfunction',
                                 'tc.gate1.voltage', 'tc.gate2.voltage', 'tc.gate3.voltage', 'tc.drain.voltage']
        for param in params_from_structure:
            self.params[param] = self.structure.getParam(param)

        # set the points
        points = ''
        for key, coord_tup in self.channel_points.items():
            points += ('\t\t%s\n' % (coord_tup,))
        self.params['points'] = points

        # interface charge concentration
        self.params['charge'] = self.lines_charge

        # deal with solve_vth condition
        if self.solve_vth:
            params_for_solvevth = ['tc.gate.voltage.pass', 'tc.gate.voltage.read', 'tc.drain.voltage.read']
            for param in params_for_solvevth:
                self.params[param] = self.structure.getParam(param)
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

    def readInterfaceCharge(self):
        interface_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.Charge_File)
        file = open(interface_filepath)
        infoline = file.readline() #read the information line
        regions_name = ['gate1', 'iso2', 'gate2', 'iso3', 'gate3']
        regions_grid = [int(self.structure.getParam('tc.gate1.width.grid')),
                        int(self.structure.getParam('tc.iso2.width.grid')),
                        int(self.structure.getParam('tc.gate2.width.grid')),
                        int(self.structure.getParam('tc.iso3.width.grid')),
                        int(self.structure.getParam('tc.gate3.width.grid'))]
        for region, grid_num in zip(regions_name, regions_grid):
            for grid_index in range(1, grid_num+1):
                file_line = file.readline()
                voltage_shift = float(re.split('\s+', file_line)[2]) # the third is voltage shift
                charge_conc = self.calculateChargeConc(voltage_shift)
                region_grid_name = 'R.%s.gr%s' % (region, grid_index)
                line_phys = 'Physics (RegionInterface = "R.subs/%s")\n' % region_grid_name
                self.lines_charge += line_phys
                line_left_brace = '{\n'
                self.lines_charge += line_left_brace
                # note that it is negative charge
                line_trap = 'Traps (FixedCharge Conc=-%.3e)\n' % charge_conc
                self.lines_charge += line_trap
                line_rigth_brace = '}\n\n'
                self.lines_charge += line_rigth_brace

        return

    def calculateChargeConc(self, voltage_shift):
        nm_in_cm = 1e-7
        epsilon_sio2 = float(self.structure.getMatParam(('SiO2', 'dielectricConstant')))
        stack_thick_in_cm = float(self.structure.getParam('tc.stack.thick')) * nm_in_cm
        charge_conc = voltage_shift * (sen.eps0 * epsilon_sio2) / stack_thick_in_cm / sen.q_charge
        return charge_conc


def test():
    return

if __name__ == '__main__': test()