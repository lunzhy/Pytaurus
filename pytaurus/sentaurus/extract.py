__author__ = 'Lunzhy'
import os, sys, re
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen


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


def test():
    parsePlotFile()
    return

if __name__ == '__main__': test()