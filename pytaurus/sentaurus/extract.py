__author__ = 'Lunzhy'
import os, sys, re
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen
import pytaurus.tools as tools


def parsePlotFile(prj_path):
    potential_list = []
    fermi_energy_list = []
    conduction_band_list = []
    file_path = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Plot_Subs_File)
    f = open(file_path)
    content = f.read()
    f.close()

    pat_data = re.compile(r'Data.*\{.*\}', re.DOTALL)
    match = re.search(pat_data, content)
    data_branket = match.group()
    pat_value = re.compile(r'(?<=\{).*(?=\})', re.DOTALL)
    match = re.search(pat_value, data_branket)
    data_str = match.group()
    pat = re.compile(r'\s+')
    data_list = re.split(pat, data_str.strip())
    #data_list = [float(x) for x in data_list]
    #up to here, data_list is set

    #deal with the data name
    pat_dataset = re.compile(r'datasets.+?\]', re.DOTALL)
    match = re.search(pat_dataset, content)
    if not match == None:
        datasets = match.group()
    pat_dataname=re.compile(r'".+?"')
    data_names = re.findall(pat_dataname, datasets)
    effective_index = []
    for name, value in zip(data_names, data_list):
        if not 'Pos' in name:
            continue
        if 'ElectrostaticPotential' in name:
            potential_list.append(value)
        elif 'eQuasiFermiEnergy' in name:
            fermi_energy_list.append(value)
        elif 'ConductionBandEnergy' in name:
            conduction_band_list.append(value)

    #put file
    out_filepath = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Subs_Data_File)
    f = open(out_filepath, 'w+')
    f.write('vertex ID\t\tchannel potential [V]\t\tfermi energy above CB [eV]\n')
    for index, (pot, fermi, cb) in enumerate(zip(potential_list, fermi_energy_list, conduction_band_list)):
        fermi_above = float(fermi) - float(cb) # fermi energy above conduction band
        line = '%s %s %s\n' % (index, pot, fermi_above)
        f.write(line)
    f.close()
    return


def extractVth(output):
    patt = re.compile(r'Vth\s+(-\d+|\d+).\d+')
    match = re.search(patt, output)
    if match is None:
        print('No vth extracted.')
    else:
        voltage = match.group()
    voltage = float(voltage[3:])  # remove Vth string
    return voltage


def parseVth(prj_path, trip_cells):
    gate1_start = float(trip_cells.get_param('tc.iso1.width'))
    gate1_end = gate1_start + float(trip_cells.get_param('tc.gate1.width'))
    gate2_start = gate1_end + float(trip_cells.get_param('tc.iso2.width'))
    gate2_end = gate2_start + float(trip_cells.get_param('tc.gate2.width'))
    gate3_start = gate2_end + float(trip_cells.get_param('tc.iso3.width'))
    gate3_end = gate3_start + float(trip_cells.get_param('tc.gate3.width'))

    time, vth_gate1 = _calcVfbShift(prj_path, gate1_start, gate1_end, ret_time=True)
    vth_gate2 = _calcVfbShift(prj_path, gate2_start, gate2_end)
    vth_gate3 = _calcVfbShift(prj_path, gate3_start, gate3_end)
    time_vth_list = tuple(zip(time, vth_gate1, vth_gate2, vth_gate3))
    vth_flatband_file = os.path.join(prj_path, sen.Folder_Miscellaneous, sen.File_Parsed_Vth)
    with open(vth_flatband_file, 'w') as file:
        file.write('Time [s]\t\tCell1 [V]\tCell2 [V]\tCell3 [V]\n')
        for time_vth in time_vth_list:
            file.write('%.5e\t\t%.5f\t\t%.5f\t\t%.5f\n' % time_vth)
    return


def _calcVfbShift(prj_path, xcoord_start, xcoord_end, ret_time=False):
    # parse effective points
    points_file = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Points_Location_Subs)
    eff_points = []
    with open(points_file) as file:
        info = file.readline()
        for line in file.readlines():
            items = re.split('\s+', line)
            vert_index, xcoord = int(items[0]), float(items[1])
            if xcoord >= xcoord_start and xcoord <= xcoord_end:
                eff_points.append(vert_index)

    vfb_dir = os.path.join(prj_path, sen.Folder_Substrate)
    time_vth_list = []
    for file in os.listdir(vfb_dir):
        if sen.Charge_File_Prefix in file:
            file_path = os.path.join(vfb_dir, file)
            sim_time = tools.parseSimTime(file_path)
            with open(file_path, 'r') as file:
                info = file.readline()
                voltage_list = []
                for line in file.readlines():
                    items = re.split('\s+', line)
                    vert_left, vert_right, voltage = int(items[0]), int(items[1]), float(items[2])
                    if vert_left in eff_points and vert_right in eff_points:
                        voltage_list.append(voltage)
            effective_voltage = sum(voltage_list) / len(voltage_list)  # all grids have same length
            time_vth_list.append((sim_time, effective_voltage))
    # organise time voltage list
    time_vth_list = sorted(time_vth_list, key=lambda x: x[0])
    time_list = [ tup[0] for tup in time_vth_list]
    vth_list = [ tup[1] for tup in time_vth_list]
    if ret_time is True:
        return time_list, vth_list
    else:
        return vth_list
    return None


def writeVth(prj_path, time, voltage, cell):
    vth_cell1 = str(voltage) if cell == 'cell1' else 'N/A'
    vth_cell2 = str(voltage) if cell == 'cell2' else 'N/A'
    vth_cell3 = str(voltage) if cell == 'cell3' else 'N/A'
    vth_file = os.path.join(prj_path, sen.Folder_Miscellaneous, sen.File_Vth)
    if not os.path.exists(vth_file):
        with open(vth_file, 'w+') as file:
            file.write('Time [s]\t\tCell1 [V]\tCell2 [V]\tCell3 [V]\n')
    with open(vth_file, 'a+') as file:
        file.write('%.5e\t\t\t%s\t\t%s\t\t%s\n' % (time, vth_cell1, vth_cell2, vth_cell3))
    return


def test():
    parsePlotFile()
    return

if __name__ == '__main__': test()