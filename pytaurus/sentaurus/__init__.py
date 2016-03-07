__author__ = 'Lunzhy'


def get_file_name(template, pyt_structure):
    if pyt_structure == 'DoubleGate':
        file_name = template % 'triplefull'   # for historical reason
    elif pyt_structure == 'Planar':
        file_name = template % 'planar'
    try:
        return file_name
    except UnboundLocalError:
        print('Wrong tc.structure name. Error occurs in function get_file_name.', pyt_structure)


# parameter file name
User_Param_File = r'user.param'
TimeStep_File = 'timestep.in'
Trapped_In_File = 'trapped.in'


# the template filename in resource
def Resource_Sse_File(pyt_structure):
    return get_file_name(r'%s_sse.template', pyt_structure)


Resource_Sde_File = 'sde.template'


def Resource_Sde_File_Vth(pyt_structure):
    return get_file_name(r'%s_sde.template', pyt_structure)


# the folder to run sentaurus under project folder
Folder_Run_Sentaurus = r'sentrun'
Folder_Exchange_Data = r'exchange'


# the generated command name for sse dan sdevice
def Sse_Cmd_File(pyt_structure):
    return get_file_name(r'sse_%s.cmd', pyt_structure)


def Sde_Cmd_File(pyt_structure):
    return get_file_name(r'sde_%s.cmd', pyt_structure)


Resource_Ins_File = r'inspect.template'
Inspect_Cmd_File = r'ins.cmd'

# names of file for data exchange
# from SimCTM
Points_Location_Subs = r'subs_points.in'
File_Interface_Vfb = r'charge.in'
# from Pytaurus
Subs_Data_File = r'substrate.in'
Plot_Subs_File = r'potential_fermi.out'


def Sde_Out_File(pyt_structure):
    return get_file_name(r'%s', pyt_structure)


def Tdr_File(pyt_structure):
    return get_file_name(r'%s_msh.tdr', pyt_structure)


def Plot_File(pyt_structure):
    return get_file_name(r'extract_%s_des.plt', pyt_structure)


def Plot_File_Init(pyt_structure):
    return get_file_name(r'init_%s_des.plt', pyt_structure)

Param_File = 'iso.par'

# the folder and file name for solving vth
Folder_Substrate = r'Substrate'
Charge_File_Prefix = r'VfbInterface'
Folder_Miscellaneous = r'Miscellaneous'
File_Vth = r'Vth.txt'
File_Parsed_Vth = r'Vth_flatband.txt'

# names of file for log
Logfile_Sse = r'sse_run.log'
Logfile_Sdevice = r'sde_run.log'

# physics constant
eps0 = 8.854187817e-14 # [F/cm]
q_charge = 1.602176487e-19 # [C]