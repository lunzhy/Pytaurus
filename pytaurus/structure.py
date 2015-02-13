__author__ = 'Lunzhy'
import os, sys, re, shutil
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.env as platform
import pytaurus.sentaurus as sen


class TripleCells:
    def __init__(self, prj_path):
        self.prj_path = prj_path
        self.current_material = ''
        self.params = {}
        self.mat_params = {}
        self.user_param_path = os.path.join(prj_path, sen.User_Param_File)
        self.channel_points = []
        return

    def _isCommentOrBlank(self, line):
        line = line.lstrip()
        return len(line) == 0 or line[0] == '#'

    def _parseLine(self, line):
        effective_line = re.split(':|#', line)
        param = effective_line[0].strip()
        value = effective_line[1].strip()
        # parse structure parameters
        if 'tc.' in param:
            self.params[param] = value
        # parse other parameters
        if 'subs' in param:
            self.params[param] = value
        # parse material parameters
        if param == 'material':
            self.current_material = value
        if param == 'dielectricConstant':
            self.mat_params[(self.current_material, param)] = value
        return

    def _readParamFile(self, file_path):
        f = open(file_path)
        for line in f.readlines():
            if self._isCommentOrBlank(line):
                continue
            self._parseLine(line)
        f.close()
        return

    def get_param(self, name):
        try:
            par_val = self.params[name]
        except KeyError:
            print('The required parameter [%s] does not exist.' % name)
        if name == 'tc.junction':
            if par_val == 'True':
                par_val = '1'
            elif par_val == 'False':
                par_val = '0'
        return str(par_val)

    def getMatParam(self, name):
        return self.mat_params[name]

    def build(self):
        default_param_path = platform.Default_Param_Path
        self._readParamFile(default_param_path)
        self._readParamFile(self.user_param_path)
        self._setEquiStackThick()
        self._calcChannelPoints()
        self._writeChannelPoints()
        return

    def _setEquiStackThick(self):
        tunnel_thick = self.params['tc.tunnel.thick']
        tunnel_material = self.params['tc.tunnel.material']
        tunnel_dielectric = self.mat_params[(tunnel_material, 'dielectricConstant')]
        trap_thick = self.params['tc.trap.thick']
        trap_material = self.params['tc.trap.material']
        trap_dielectric = self.mat_params[(trap_material, 'dielectricConstant')]
        block_thick = self.params['tc.block.thick']
        block_material = self.params['tc.block.material']
        block_dielectric = self.mat_params[(block_material, 'dielectricConstant')]
        SiO2_dielectric = self.mat_params[('SiO2', 'dielectricConstant')]
        equi_stack_thick = (float(tunnel_thick) / float(tunnel_dielectric) + float(trap_thick) / float(trap_dielectric)
                            + float(block_thick) / float(block_dielectric)) * float(SiO2_dielectric)
        self.params['tc.stack.thick'] = str('%.3f' % equi_stack_thick)  # in nm
        return

    def _calcChannelPoints(self):
        nm_in_um = 1e-3
        y_coord = 0
        offset = 0
        # under iso1
        grid_num = int(self.params['tc.iso1.width.grid'])
        grid_length = float(self.params['tc.iso1.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        # under gate1
        offset += float(self.params['tc.iso1.width'])
        grid_num = int(self.params['tc.gate1.width.grid'])
        grid_length = float(self.params['tc.gate1.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        # under iso2
        offset += float(self.params['tc.gate1.width'])
        grid_num = int(self.params['tc.iso2.width.grid'])
        grid_length = float(self.params['tc.iso2.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        # under gate2
        offset += float(self.params['tc.iso2.width'])
        grid_num = int(self.params['tc.gate2.width.grid'])
        grid_length = float(self.params['tc.gate2.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        # under iso3
        offset += float(self.params['tc.gate2.width'])
        grid_num = int(self.params['tc.iso3.width.grid'])
        grid_length = float(self.params['tc.iso3.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        # under gate3
        offset += float(self.params['tc.iso3.width'])
        grid_num = int(self.params['tc.gate3.width.grid'])
        grid_length = float(self.params['tc.gate3.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        # under iso4
        offset += float(self.params['tc.gate3.width'])
        grid_num = int(self.params['tc.iso4.width.grid'])
        grid_length = float(self.params['tc.iso4.width']) / grid_num
        for grid in range(grid_num+1):
            x_coord = offset + grid * grid_length
            self.channel_points.append((x_coord, y_coord))
        return

    def _writeChannelPoints(self):
        points_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.Points_Location_Subs)
        f = open(points_filepath, 'w+')
        f.write('vertex ID\t\tx coordinate [nm]\t\ty coordinate [nm]\n')
        for vert_id, tup_points in enumerate(self.channel_points):
            line = str(vert_id) + '\t' + str(tup_points[0]) + '\t' + str(tup_points[1]) + '\n'
            f.write(line)
        f.close()
        return

    def refreshGateVoltage(self, vg1=None, vg2=None, vg3=None):
        if vg1 is not None:
            self.params['tc.gate1.voltage'] = vg1
        if vg2 is not None:
            self.params['tc.gate2.voltage'] = vg2
        if vg3 is not None:
            self.params['tc.gate3.voltage'] = vg3
        return