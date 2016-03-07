__author__ = 'Lunzhy'
import os, sys, re, shutil, time
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import collections
import pytaurus.sentaurus as sen


def copyChargeFile(prj_path, charge_file):
    dst_path = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.File_Interface_Vfb)
    shutil.copy(charge_file, dst_path)
    return


class SdeCmdFile:
    def __init__(self, triple_cell, solve_vth_cell=None, solve_type=None):
        """
        @solve_vth_cell: None for not solving vth, cell1 | cell2 | cell3 for specified cell
        """
        self.vth_cell = solve_vth_cell
        self.params = {}
        self.channel_points = {}
        self.triple_cells = triple_cell
        self.pyt_structure = triple_cell.get_param('tc.structure')
        self.prj_path = triple_cell.prj_path
        self.template_filepath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 os.pardir, os.pardir, 'resources',
                                                 sen.Resource_Sde_File))
        self.cmd_lines = []
        self.lines_charge = ''
        self.cmd_filepath = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Sde_Cmd_File(self.pyt_structure))
        self.par_file = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Param_File)
        self.solve_type = solve_type
        return

    def _copy_cmd_file_to_prj(self):
        dirToCheck = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir,
                                  'out')
        shutil.copy(self.cmd_filepath, dirToCheck)
        return

    def move_plot_file(self):
        origin_path = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Plot_File(self.pyt_structure))
        if not os.path.exists(origin_path):
            origin_path = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Plot_File_Init(self.pyt_structure))
        dst_path = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.Plot_Subs_File)
        shutil.copy(origin_path, dst_path)
        time.sleep(1)
        os.remove(origin_path)
        return

    def build(self):
        self._read_channel_verts()
        self._read_interface_charge()
        self._set_parameters()
        self._write_cmd_file()
        self._write_par_file()
        self._copy_cmd_file_to_prj()
        return

    def _replace_line(self, line):
        pattern = re.compile(r'%.*%')
        match = pattern.search(line)
        if match == None:
            return line
        else:
            param_name = match.group()[1:-1]
        value = self.params[param_name]
        new_line = re.sub(pattern, value, line)
        return new_line

    def _create_cmd_lines(self):
        f = open(self.template_filepath)
        for line in f.readlines():
            new_line = self._replace_line(line)
            self.cmd_lines.append(new_line)
        f.close()
        return

    def _write_cmd_file(self):
        cmd_filepath = self.cmd_filepath
        f = open(cmd_filepath, 'w+')
        self._create_cmd_lines()
        f.writelines(self.cmd_lines)
        f.close()
        return

    def _read_channel_verts(self):
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

    def _read_interface_charge(self):
        interface_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.File_Interface_Vfb)
        if not os.path.exists(interface_filepath):
            print('[Warning] No slice vfb shift for Pytaurus.')
            exit(0)
            return
        file = open(interface_filepath)
        infoline = file.readline()  #read the information line
        regions_name = ['iso1', 'gate1', 'iso2', 'gate2', 'iso3', 'gate3', 'iso4']
        regions_grid = [int(self.triple_cells.get_param('tc.iso1.width.grid')),
                        int(self.triple_cells.get_param('tc.gate1.width.grid')),
                        int(self.triple_cells.get_param('tc.iso2.width.grid')),
                        int(self.triple_cells.get_param('tc.gate2.width.grid')),
                        int(self.triple_cells.get_param('tc.iso3.width.grid')),
                        int(self.triple_cells.get_param('tc.gate3.width.grid')),
                        int(self.triple_cells.get_param('tc.iso4.width.grid'))]
        line_slice_count = 0
        for region, grid_num in zip(regions_name, regions_grid):
            for grid_index in range(1, grid_num + 1):
                file_line = file.readline()
                if file_line is '':
                    continue
                line_slice_count += 1
                voltage_shift = float(re.split('\s+', file_line)[2])  # the third is voltage shift

                # consider the case when lateral charge is removed
                if self.solve_type == 'empty':
                    charge_conc = 0
                elif self.solve_type == 'nlateral' and (region == 'iso2' or region == 'iso3'):
                    charge_conc = self._calculate_charge_density(voltage_shift)
                    if charge_conc < 0:
                        charge_conc = 0
                else:
                    charge_conc = self._calculate_charge_density(voltage_shift)

                if self.pyt_structure == 'DoubleGate':
                    for side in ['top', 'bot']:
                        region_grid_name = 'R.%s.gr%s.%s' % (region, grid_index, side)
                        line_phys = 'Physics (RegionInterface = "R.ch/%s")\n' % region_grid_name
                        self.lines_charge += line_phys
                        line_left_brace = '{\n'
                        self.lines_charge += line_left_brace
                        line_trap = '\tTraps (FixedCharge Conc=%.3e)\n' % charge_conc
                        self.lines_charge += line_trap
                        line_rigth_brace = '}\n\n'
                        self.lines_charge += line_rigth_brace
                elif self.pyt_structure == 'Planar':
                    region_grid_name = 'R.%s.gr%s' % (region, grid_index)
                    line_phys = 'Physics (RegionInterface = "R.subs/%s")\n' % region_grid_name
                    self.lines_charge += line_phys
                    line_left_brace = '{\n'
                    self.lines_charge += line_left_brace
                    line_trap = '\tTraps (FixedCharge Conc=%.3e)\n' % charge_conc
                    self.lines_charge += line_trap
                    line_rigth_brace = '}\n\n'
                    self.lines_charge += line_rigth_brace

        if (not line_slice_count == sum(regions_grid)) or (not file.readline() == ''):
            print('[Error] number of vfb shift does not equal to total grid nunmber.')
        return

    def _set_parameters(self):
        # tdr file
        self.params['grid.tdr'] = sen.Tdr_File(self.pyt_structure)
        self.params['plot'] = sen.Sde_Out_File(self.pyt_structure)
        self.params['current'] = sen.Sde_Out_File(self.pyt_structure)
        self.params['output'] = sen.Sde_Out_File(self.pyt_structure)

        self.params['substrate.line'] = '' if self.pyt_structure == 'DoubleGate' else r'{Name="substrate" Voltage=0}'
        # in else, pyt_structure is 'Planar'

        # parameters from structure
        params_from_structure = ['tc.gate1.workfunction', 'tc.gate2.workfunction', 'tc.gate3.workfunction']
        for param in params_from_structure:
            self.params[param] = self.triple_cells.get_param(param)

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
            self.params['tc.gate.voltage.first'] = self.triple_cells.get_param('tc.gate1.voltage')
            self.params['tc.gate.voltage.second'] = self.triple_cells.get_param('tc.gate3.voltage')
            self.params['tc.gate.voltage.third'] = self.triple_cells.get_param('tc.gate2.voltage')
            self.params['tc.drain.voltage'] = self.triple_cells.get_param('tc.drain.voltage')
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
            self.params['tc.gate.voltage.first'] = self.triple_cells.get_param('tc.gate.voltage.pass')
            self.params['tc.gate.voltage.second'] = self.triple_cells.get_param('tc.gate.voltage.pass')
            self.params['tc.gate.voltage.third'] = self.triple_cells.get_param('tc.gate.voltage.read')
            self.params['tc.drain.voltage'] = self.triple_cells.get_param('tc.drain.voltage.read')

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
                self.params['area.factor'] = 'AreaFactor=%se-3' % self.triple_cells.get_param('tc.gate1.width')
            elif self.vth_cell == 'cell2':
                self.params['area.factor'] = 'AreaFactor=%se-3' % self.triple_cells.get_param('tc.gate2.width')
            elif self.vth_cell == 'cell3':
                self.params['area.factor'] = 'AreaFactor=%se-3' % self.triple_cells.get_param('tc.gate3.width')

        # Last solve
        if self.vth_cell is None:
            self.params['solve.last'] = 'Poisson'
        else:
            self.params['solve.last'] = 'Poisson Electron'
        return

    def _calculate_charge_density(self, voltage_shift):
        nm_in_cm = 1e-7
        epsilon_sio2 = float(self.triple_cells.get_mat_param(('SiO2', 'dielectricConstant')))
        stack_thick_in_cm = float(self.triple_cells.get_param('tc.stack.thick')) * nm_in_cm
        charge_conc = voltage_shift * (sen.eps0 * epsilon_sio2) / stack_thick_in_cm / sen.q_charge
        # positive voltage shift is caused by negative charge
        return -charge_conc

    def _write_par_file(self):
        material_iso = self.triple_cells.get_param('tc.iso.material')
        epsilon_iso = self.triple_cells.get_mat_param((material_iso, 'dielectricConstant'))
        with open(self.par_file, 'w') as f:
            f.write('Material = "%s"\n' % material_iso)
            f.write('{\n')
            f.write('\tEpsilon\n')
            f.write('\t{\n')
            f.write('\t\t\tepsilon = %s\n' % epsilon_iso)
            f.write('\t}\n')
            f.write('}\n')
        return None


def test():
    return

if __name__ == '__main__': test()