__author__ = 'lunzhy'
import platform, os, sys
path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir))
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

# platform-dependent global variables
if platform.system() == 'Linux':
    Default_Param_Path = r'/home/lunzhy/SimCTM/default.param'  #the file path of default parameter file
    Debug_Directory = r'/home/lunzhy/SimCTM/debug'  # the directory path for debugging
elif platform.system() == 'Windows':
    Default_Param_Path = r'E:\MyCode\SimCTM\SimCTM\default.param'  # the file path of default parameter file
    Debug_Directory = r'E:\PhD Study\SimCTM\SctmTest\SolverPackTest'  # the directory path for debugging


# method to convert CRLF with LF in parameter file because it may cause problems when reading them from SimCTM
def convertCRLFtoLF(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    newdata = data.replace(b'\r\n', b'\n')
    if newdata != data:
        with open(file_path, 'wb') as f:
            f.write(newdata)
    return


def convertParamFile(prj_path):
    if platform.system() == 'Linux':
        default_param_path = Default_Param_Path
        user_param_path = os.path.join(prj_path, sen.User_Param_File)
        convertCRLFtoLF(default_param_path)
        convertCRLFtoLF(user_param_path)
    return


if __name__ == '__main__':
    convertParamFile('/home/lunzhy/connect')