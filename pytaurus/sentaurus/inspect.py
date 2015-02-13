__author__ = 'lunzhy'
import os, sys, re, shutil
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

Cell_gate_dict = {'cell1': 'gate1', 'cell2': 'gate2', 'cell3': 'gate3'}


class InspectCmdFile():
    def __init__(self, trip_cells, cell='cell2'):
        self.cells = trip_cells
        self.target_gate = Cell_gate_dict[cell]
        self.prj_path = trip_cells.prj_path
        self.params = {}
        file_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 os.pardir, os.pardir, 'resources', sen.Resource_Ins_File))
        self.template_file = file_path
        self.cmd_file = os.path.join(self.prj_path, sen.Folder_Run_Sentaurus, sen.Inspect_Cmd_File)
        self.cmd_lines = []
        return

    def _calc_vth_current(self):
        nm_in_um = 1e-3
        channel_length = self.cells.get_param('tc.gate2.width')
        current = 1.0 / (float(channel_length) * nm_in_um) * 1e-7
        return current

    def _set_parameters(self):
        self.params['plt'] = sen.Plot_File
        self.params['gate'] = self.target_gate
        self.params['vth.current'] = '1e-7'
        return

    def _replace_line(self, line):
        pattern = re.compile(r'%.*%')
        match = pattern.search(line)
        if match is None:
            return line
        else:
            param_name = match.group()[1:-1]
        value = self.params[param_name]
        new_line = re.sub(pattern, value, line)
        return new_line

    def _create_cmd_lines(self):
        f = open(self.template_file)
        for line in f.readlines():
            new_line = self._replace_line(line)
            self.cmd_lines.append(new_line)
        f.close()
        return

    def _write_cmd_file(self):
        cmd_file = self.cmd_file
        f = open(cmd_file, 'w+')
        self._create_cmd_lines()
        f.writelines(self.cmd_lines)
        f.close()
        return

    def build(self):
        self._set_parameters()
        self._write_cmd_file()
        return