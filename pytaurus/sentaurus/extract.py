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
    out_filepath = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Exchange_Data_Subs)
    f = open(out_filepath, 'w+')
    f.write('vertex ID\t\tchannel potential [V]\t\tfermi energy above CB [eV]\n')
    for index, (pot, fermi, cb) in enumerate(zip(potential_list, fermi_energy_list, conduction_band_list)):
        fermi_above = float(fermi) - float(cb) # fermi energy above conduction band
        line = '%s %s %s\n' % (index, pot, fermi_above)
        f.write(line)
    f.close()
    return


def extractVth(output):
    patt = re.compile(r'Vth\s+\d+.\d+')
    match = re.search(patt, output)
    if match is None:
        print('No vth extracted.')
    else:
        voltage = match.group()
    voltage = float(voltage[4:])
    return voltage


def parseVth(prj_path, trip_cells):
    # parse effective points
    points_file = os.path.join(prj_path, sen.Folder_Exchange_Data, sen.Points_Location_Subs)
    channel_main_start = float(trip_cells.getParam('tc.iso1.width')) +\
                         float(trip_cells.getParam('tc.gate1.width')) + float(trip_cells.getParam('tc.iso2.width'))
    channel_main_end = channel_main_start + float(trip_cells.getParam('tc.gate2.width'))
    main_points = []
    with open(points_file) as file:
        info = file.readline()
        for line in file.readlines():
            items = re.split('\s+', line)
            vert_index, xcoord = int(items[0]), float(items[1])
            if xcoord >= channel_main_start and xcoord <= channel_main_end:
                main_points.append(vert_index)
    vfb_dir = os.path.join(prj_path, sen.Folder_Substrate)
    time_vth_list = []
    for file in os.listdir(vfb_dir):
        if sen.Charge_File_Prefix in file:
            file_path = os.path.join(vfb_dir, file)
            sim_time = tools.parseSimTime(file_path)
            with open(file_path) as file:
                info = file.readline()
                voltage_list = []
                for line in file.readlines():
                    items = re.split('\s+', line)
                    vert_left, vert_right, voltage = int(items[0]), int(items[1]), float(items[2])
                    if vert_left in main_points and vert_right in main_points:
                        voltage_list.append(voltage)
            effective_voltage = sum(voltage_list) / len(voltage_list)
            time_vth_list.append((sim_time, effective_voltage))

    # organise time voltage list
    time_vth_list = sorted(time_vth_list, key=lambda x: x[0])
    vth_flatband_file = os.path.join(prj_path, sen.Folder_Miscellaneous, sen.File_Parsed_Vth)
    with open(vth_flatband_file, 'w') as file:
        for time_vth in time_vth_list:
            file.write('%.5e\t\t%s\n' % time_vth)
    return


def test():
    parsePlotFile()
    return

if __name__ == '__main__': test()