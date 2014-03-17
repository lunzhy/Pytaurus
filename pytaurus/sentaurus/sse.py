__author__ = 'Lunzhy'
import os, sys, re, shutil
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.platform as platform
import pytaurus.sentaurus as sen


class TripleCells:
    def __init__(self, prj_path):
        self.prj_path = prj_path
        self.current_material = ''
        self.params = {}
        self.mat_params = {}
        self.user_param_path = os.path.join(prj_path, sen.User_Param_File)
        self.points = []
        return

    def isCommentOrBlank(self, line):
        line = line.lstrip()
        return len(line) == 0 or line[0] == '#'

    def parseLine(self, line):
        effective_line = re.split(':|#', line)
        param = effective_line[0].strip()
        value = effective_line[1].strip()
        # parse structure parameters
        if 'tc.' in param:
            self.params[param] = value
        # parse material parameters
        if param == 'material':
            self.current_material = value
        if param == 'dielectricConstant':
            self.mat_params[(self.current_material, param)] = value
        return

    def readParamFile(self, file_path):
        f = open(file_path)
        for line in f.readlines():
            if self.isCommentOrBlank(line):
                continue
            self.parseLine(line)
        f.close()
        return

    def getParam(self, name):
        return self.params[name]

    def getMatParam(self, name):
        return self.mat_params[name]

    def build(self):
        default_param_path = platform.Default_Param_Path
        self.readParamFile(default_param_path)
        self.readParamFile(self.user_param_path)
        self.setNonOccur()
        self.setEquiStackThick()
        self.calcChannelPoints()
        self.writeChannelPoints()
        return

    def setEquiStackThick(self):
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
        self.params['tc.stack.thick'] = str('%.3f' % equi_stack_thick) # in nm
        return

    def setNonOccur(self):
        self.params['tc.iso1.width'] = self.params['tc.iso2.width']
        self.params['tc.iso4.width'] = self.params['tc.iso3.width']
        return

    def calcChannelPoints(self):
        nm_in_um = 1e-3
        y_coord = 0
        # under gate1
        offset = float(self.params['tc.iso1.width'])
        grid_num = int(self.params['tc.gate1.width.grid'])
        grid_length = float(self.params['tc.gate1.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.points.append((x_coord, y_coord))
        # under iso2
        offset += float(self.params['tc.gate1.width'])
        grid_num = int(self.params['tc.iso2.width.grid'])
        grid_length = float(self.params['tc.iso2.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.points.append((x_coord, y_coord))
        # under gate2
        offset += float(self.params['tc.iso2.width'])
        grid_num = int(self.params['tc.gate2.width.grid'])
        grid_length = float(self.params['tc.gate2.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.points.append((x_coord, y_coord))
        # under iso3
        offset += float(self.params['tc.gate2.width'])
        grid_num = int(self.params['tc.iso3.width.grid'])
        grid_length = float(self.params['tc.iso3.width']) / grid_num
        for grid in range(grid_num):
            x_coord = offset + grid * grid_length
            self.points.append((x_coord, y_coord))
        # under gate3
        offset += float(self.params['tc.iso3.width'])
        grid_num = int(self.params['tc.gate3.width.grid'])
        grid_length = float(self.params['tc.gate3.width']) / grid_num
        for grid in range(grid_num+1): # the last is different from previous
            x_coord = offset + grid * grid_length
            self.points.append((x_coord, y_coord))
        return

    def writeChannelPoints(self):
        points_filepath = os.path.join(self.prj_path, sen.Folder_Exchange_Data, sen.ExPoints_Subs)
        f = open(points_filepath, 'w+')
        f.write('vertex ID\t\tx coordinate [nm]\t\ty coordinate [nm]\n')
        for id, tup_points in enumerate(self.points):
            line = str(id) + '\t' + str(tup_points[0]) + '\t' + str(tup_points[1]) + '\n'
            f.write(line)
        f.close()
        return


class SseCmdFile:
    def __init__(self, trip_cell):
        self.triple_cell = trip_cell
        self.prj_path = trip_cell.prj_path
        file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 os.pardir, os.pardir, 'resources', sen.Resource_Sse_File))
        self.template_cmdfile = file_path
        self.cmd_lines = []
        self.cmd_filepath = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Sse_Cmd_File)
        return

    def replaceLine(self, line):
        pattern = re.compile(r'%.*%')
        match = pattern.search(line)
        if match == None:
            return line
        else:
            param_name = match.group()[1:-1]  # r'%(?<=%).*(?=%)%'
        value = self.triple_cell.getParam(param_name)
        new_line = re.sub(pattern, value, line)
        return new_line

    def putRegionGrids(self):
        name_regions = ['gate1','iso2','gate2','iso3','gate3']
        leftX_regions = ['rX_i1', 'rX_g1', 'rX_i2', 'rX_g2', 'rX_i3']
        length_regions = ['Lgate1', 'Liso2', 'Lgate2', 'Liso3', 'Lgate3']
        for name, leftX, length in zip(name_regions, leftX_regions, length_regions):
            line = ';create region under %s\n' % name
            self.cmd_lines.append(line)
            line = '(define lX_section %s)\n' % leftX
            self.cmd_lines.append(line)
            param = 'tc.%s.width.grid' % name
            grid_number = int(self.triple_cell.getParam(param))
            line = '(define Lgrid (/ %s %s))\n' % (length, grid_number)
            self.cmd_lines.append(line)
            for grid in range(1, grid_number+1):
                variable_name = 'rX_r' + str(grid)
                if grid == 1:
                    left = 'lX_section'
                else:
                    left = 'rX_r' + str(grid-1)
                line = '(define %s (+ %s Lgrid)) ;region %s\n' % (variable_name, left, str(grid))
                self.cmd_lines.append(line)

            for grid in range(1, grid_number+1):
                right = 'rX_r' + str(grid)
                if grid == 1:
                    left = 'lX_section'
                else:
                    left = 'rX_r' + str(grid - 1)
                r_name = 'R.%s.gr%s' % (name, str(grid))
                line = '(sdegeo:create-rectangle (position %s bY_stack 0) (position %s tY_stack 0) "SiO2" "%s")\n' \
                       % (left, right, r_name)
                self.cmd_lines.append(line)
        return

    def creatCmdLines(self):
        template = open(self.template_cmdfile)
        end_count = 0
        put_flag = False
        for line in template.readlines():
            if '<split>' in line:
                end_count += 1
                continue
            if end_count == 0:
                new_line = self.replaceLine(line)
                self.cmd_lines.append(new_line)
            elif end_count == 1 or end_count == 3:
                self.cmd_lines.append(line)
            else: # end_count == 2
                if not put_flag:
                    self.putRegionGrids()
                    put_flag = True
        template.close()
        return

    def writeCmdFile(self):
        cmd_filepath = self.cmd_filepath
        f = open(cmd_filepath, 'w+')
        self.creatCmdLines()
        f.writelines(self.cmd_lines)
        f.close()
        return

    def copyCmdFileToPrj(self):
        dirToCheck = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir,
                                      'out')
        shutil.copy(self.cmd_filepath, dirToCheck)
        return

    def build(self):
        self.writeCmdFile()
        self.copyCmdFileToPrj()
        return


def test():
    trip_cells = TripleCells(platform.Debug_Directory)
    trip_cells.build()
    print(trip_cells.points)
    print(trip_cells.params)
    #print(trip_cells.getParam('tc.stack.thick'))
    #print(trip_cells.getMatParam(('SiO2', 'dielectricConstant')))
    sse = SseCmdFile(trip_cells)
    #new = sse.replaceLine('(define ThicknessGate tc.iso.thick%)    ;(defineThicknessGate 10)')
    #sse.writeCmdFile('a.txt')
    #print(os.path.dirname(__file__))
    sse.build()
    return

if __name__ == '__main__': test()