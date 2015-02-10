__author__ = 'Lunzhy'
import os, sys, re, shutil, time
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import collections
import pytaurus.sentaurus as sen


def movePlotFile(prj_path):
    origin_path = os.path.join(prj_path, sen.Folder_Run_Sentaurus, sen.Plot_File)
    if not os.path.exists(origin_path):
        origin_path = os.path.join(prj_path, sen.Folder_Run_Sentaurus, sen.Plot_File_Init)
    dst_path = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Plot_Subs_File)
    shutil.copy(origin_path, dst_path)
    time.sleep(1)
    os.remove(origin_path)
    return


def copyChargeFile(prj_path, charge_file):
    dst_path = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.File_Interface_Vfb)
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
        interface_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.File_Interface_Vfb)
        print(interface_filepath)
        exit(0)
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


class SdeCmdFileTripleFull(SdeCmdFile):
    def __init__(self, triple_cell, solve_vth_cell=None):
        """
        @solve_vth_cell: None for not solving vth, cell1 | cell2 | cell3 for specified cell
        """
        self.vth_cell = solve_vth_cell
        self.params = {}
        self.channel_points = {}
        self.structure = triple_cell
        self.prj_path = triple_cell.prj_path
        file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 os.pardir, os.pardir, 'resources', sen.Resource_Sde_File))
        self.template_filepath = file_path
        self.cmd_lines = []
        self.lines_charge = ''
        self.cmd_filepath = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Sde_Cmd_File)
        return

    def readInterfaceCharge(self):
        interface_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.File_Interface_Vfb)
        if not os.path.exists(interface_filepath):
            print('[Warning] No slice vfb shift for Pytaurus.')
            return
        file = open(interface_filepath)
        infoline = file.readline()  #read the information line
        regions_name = ['iso1', 'gate1', 'iso2', 'gate2', 'iso3', 'gate3', 'iso4']
        regions_grid = [int(self.structure.getParam('tc.iso1.width.grid')),
                        int(self.structure.getParam('tc.gate1.width.grid')),
                        int(self.structure.getParam('tc.iso2.width.grid')),
                        int(self.structure.getParam('tc.gate2.width.grid')),
                        int(self.structure.getParam('tc.iso3.width.grid')),
                        int(self.structure.getParam('tc.gate3.width.grid')),
                        int(self.structure.getParam('tc.iso4.width.grid'))]
        line_slice_count = 0
        for region, grid_num in zip(regions_name, regions_grid):
            for grid_index in range(1, grid_num + 1):
                file_line = file.readline()
                if file_line is '':
                    continue
                line_slice_count += 1
                voltage_shift = float(re.split('\s+', file_line)[2])  # the third is voltage shift
                charge_conc = self.calculateChargeConc(voltage_shift)
                for side in ['top', 'bot']:
                    region_grid_name = 'R.%s.gr%s.%s' % (region, grid_index, side)
                    line_phys = 'Physics (RegionInterface = "R.ch/%s")\n' % region_grid_name
                    self.lines_charge += line_phys
                    line_left_brace = '{\n'
                    self.lines_charge += line_left_brace
                    # note that it is negative charge
                    line_trap = '\tTraps (FixedCharge Conc=-%.3e)\n' % charge_conc
                    self.lines_charge += line_trap
                    line_rigth_brace = '}\n\n'
                    self.lines_charge += line_rigth_brace

        if (not line_slice_count == sum(regions_grid)) or (not file.readline() == ''):
            print('[Error] number of vfb shift does not equal to total grid nunmber.')
        return

    def setParameters(self):
        # tdr file
        self.params['grid.tdr'] = sen.Tdr_File

        # parameters from structure
        params_from_structure = ['tc.gate1.workfunction', 'tc.gate2.workfunction', 'tc.gate3.workfunction']
        for param in params_from_structure:
            self.params[param] = self.structure.getParam(param)

        # set the points
        if self.vth_cell is None:
            points = ''
            for key, coord_tup in self.channel_points.items():
                points += ('\t\t%s\n' % (coord_tup,))
            self.params['points'] = points
        else:
            self.params['points'] = '(0, 0)'  # in CurrentPlot section, empty points is invalid

        # interface charge concentration
        self.params['charge'] = self.lines_charge

        # deal with gate voltage, in consideration of the solve_vth condition
        if self.vth_cell is None:  # solve potential situation
            self.params['gate.first.ramp'] = 'gate1'
            self.params['gate.second.ramp'] = 'gate3'
            self.params['gate.third.ramp'] = 'gate2'
            self.params['tc.gate.voltage.first'] = self.structure.getParam('tc.gate1.voltage')
            self.params['tc.gate.voltage.second'] = self.structure.getParam('tc.gate3.voltage')
            self.params['tc.gate.voltage.third'] = self.structure.getParam('tc.gate2.voltage')
            self.params['tc.drain.voltage'] = self.structure.getParam('tc.drain.voltage')
        else:  # solve_vth situation
            if self.vth_cell == 'cell1':
                self.params['gate.first.ramp'] = 'gate2'
                self.params['gate.second.ramp'] = 'gate3'
                self.params['gate.third.ramp'] = 'gate1'
            elif self.vth_cell == 'cell2':
                self.params['gate.first.ramp'] = 'gate1'
                self.params['gate.second.ramp'] = 'gate3'
                self.params['gate.third.ramp'] = 'gate2'
            elif  self.vth_cell == 'cell3':
                self.params['gate.first.ramp'] = 'gate1'
                self.params['gate.second.ramp'] = 'gate2'
                self.params['gate.third.ramp'] = 'gate3'
            self.params['tc.gate.voltage.first'] = self.structure.getParam('tc.gate.voltage.pass')
            self.params['tc.gate.voltage.second'] = self.structure.getParam('tc.gate.voltage.pass')
            self.params['tc.gate.voltage.third'] = self.structure.getParam('tc.gate.voltage.read')
            self.params['tc.drain.voltage'] = self.structure.getParam('tc.drain.voltage.read')

        # CurrentPlot
        if self.vth_cell is None:  # solve initial value mode
            self.params['plot.time.gate.first'] = 'Time=(-1)'
            self.params['plot.time.gate.second'] = 'Time=(-1)'
            self.params['plot.time.drain'] = 'Time=(-1)'
            self.params['plot.last'] = 'CurrentPlot ( Time=(1) )'
            if float(self.params['tc.gate.voltage.third']) == 0:
                if float(self.params['tc.drain.voltage']) == 0:
                    if float(self.params['tc.gate.voltage.second']) == 0:
                        self.params['plot.time.gate.first'] = 'Time=(1)'
                    else:
                        self.params['plot.time.gate.second'] = 'Time=(1)'
                else:
                    self.params['plot.time.drain'] = 'Time=(1)'

        else:  # solve vth mode
            self.params['plot.time.gate.first'] = 'Time=(-1)'
            self.params['plot.time.gate.second'] = 'Time=(-1)'
            self.params['plot.time.drain'] = 'Time=(-1)'
            self.params['plot.last'] = ''

        # AreaFactor
        if self.vth_cell is None:
            self.params['area.factor'] = ''
        else:
            if self.vth_cell == 'cell1':
                self.params['area.factor'] = 'AreaFactor=%se-3' % self.structure.getParam('tc.gate1.width')
            elif self.vth_cell == 'cell2':
                self.params['area.factor'] = 'AreaFactor=%se-3' % self.structure.getParam('tc.gate2.width')
            elif self.vth_cell == 'cell3':
                self.params['area.factor'] = 'AreaFactor=%se-3' % self.structure.getParam('tc.gate3.width')

        # Last solve
        if self.vth_cell is None:
            self.params['solve.last'] = 'Poisson'
        else:
            self.params['solve.last'] = 'Poisson Electron'
        return

def test():
    return

if __name__ == '__main__': test()