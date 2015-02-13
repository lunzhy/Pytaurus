__author__ = 'Lunzhy'
import os, sys, re, shutil
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.env as platform
import pytaurus.sentaurus as sen


class SseCmdFile:
    def __init__(self, trip_cell):
        self.pyt_structure = trip_cell.get_param('tc.structure')
        self.triple_cell = trip_cell
        self.prj_path = trip_cell.prj_path
        self.template_cmdfile = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                        os.pardir, os.pardir, 'resources', sen.Resource_Sse_File(self.pyt_structure)))
        self.cmd_filepath = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Sse_Cmd_File(self.pyt_structure))
        self.cmd_lines = []
        return

    def _replace_line(self, line):
        pattern = re.compile(r'%.*%')
        match = pattern.search(line)
        if match == None:
            return line  # return this line if parameter parenthetical symbol (%%) is not found
        else:
            param_name = match.group()[1:-1]  # r'%(?<=%).*(?=%)%'
        value = self.triple_cell.get_param(param_name)
        new_line = re.sub(pattern, value, line)
        return new_line

    def _write_cmd_file(self):
        cmd_filepath = self.cmd_filepath
        f = open(cmd_filepath, 'w+')
        self._create_cmd_lines();
        f.writelines(self.cmd_lines)
        f.close()
        return

    def _copy_cmd_file_to_prj(self):
        dirToCheck = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir,
                                      'out')
        shutil.copy(self.cmd_filepath, dirToCheck)
        return

    def build(self):
        self._write_cmd_file()
        self._copy_cmd_file_to_prj()
        return

    def _put_region_grids(self):
        name_regions = ['iso1', 'gate1', 'iso2', 'gate2', 'iso3', 'gate3', 'iso4']
        leftX_regions = ['lX_i1', 'lX_g1', 'lX_i2', 'lX_g2', 'lX_i3', 'lX_g3', 'lX_i4']
        length_regions = ['Liso1', 'Lgate1', 'Liso2', 'Lgate2', 'Liso3', 'Lgate3', 'Liso4']
        for name, leftX, length in zip(name_regions, leftX_regions, length_regions):
            line = ';create region under %s\n' % name
            self.cmd_lines.append(line)
            line = '(define lX_section %s)\n' % leftX
            self.cmd_lines.append(line)
            param = 'tc.%s.width.grid' % name
            grid_number = int(self.triple_cell.get_param(param))
            line = '(define Lgrid (/ %s %s))\n' % (length, grid_number)
            self.cmd_lines.append(line)
            for grid in range(1, grid_number + 1):
                variable_name = 'rX_r' + str(grid)
                if grid == 1:
                    left = 'lX_section'
                else:
                    left = 'rX_r' + str(grid - 1)
                line = '(define %s (+ %s Lgrid)) ;region %s\n' % (variable_name, left, str(grid))
                self.cmd_lines.append(line)

            if self.pyt_structure == 'DoubleGate':
                # for top gate stack
                for grid in range(1, grid_number + 1):
                    right = 'rX_r' + str(grid)
                    if grid == 1:
                        left = 'lX_section'
                    else:
                        left = 'rX_r' + str(grid - 1)
                    r_name = 'R.%s.gr%s.top' % (name, str(grid))
                    line = '(sdegeo:create-rectangle (position %s bY_stack 0) (position %s tY_stack 0) "SiO2" "%s")\n' \
                           % (left, right, r_name)
                    self.cmd_lines.append(line)
                # for bottom gate stack
                for grid in range(1, grid_number + 1):
                    right = 'rX_r' + str(grid)
                    if grid == 1:
                        left = 'lX_section'
                    else:
                        left = 'rX_r' + str(grid - 1)
                    r_name = 'R.%s.gr%s.bot' % (name, str(grid))
                    line = '(sdegeo:create-rectangle (position %s (+ Yoffset_stack bY_stack) 0)' \
                           ' (position %s (+ Yoffset_stack tY_stack) 0) "SiO2" "%s")\n' \
                           % (left, right, r_name)
                    self.cmd_lines.append(line)

            elif self.pyt_structure == 'Planar':
                # for top gate stack
                for grid in range(1, grid_number + 1):
                    right = 'rX_r' + str(grid)
                    if grid == 1:
                        left = 'lX_section'
                    else:
                        left = 'rX_r' + str(grid - 1)
                    r_name = 'R.%s.gr%s' % (name, str(grid))
                    line = '(sdegeo:create-rectangle (position %s bY_stack 0) (position %s tY_stack 0) "SiO2" "%s")\n' \
                           % (left, right, r_name)
                    self.cmd_lines.append(line)

            self.cmd_lines.append('\n')
        return

    def _create_cmd_lines(self):
        template = open(self.template_cmdfile)
        end_count = 0
        put_flag = False
        for line in template.readlines():
            if '<split>' in line:
                end_count += 1
                continue
            if end_count == 0 or end_count == 3:  # replace lines
                new_line = self._replace_line(line)
                self.cmd_lines.append(new_line)
            elif end_count == 1 or end_count == 4:  # not change
                self.cmd_lines.append(line)
            else:  # end_count == 2, put new lines
                if not put_flag:
                    self._put_region_grids()
                    put_flag = True
        template.close()
        return


def test():
    trip_cells = TripleCells(platform.Debug_Directory)
    trip_cells.build()
    print(trip_cells.channel_points)
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