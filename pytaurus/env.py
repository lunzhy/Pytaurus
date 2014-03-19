__author__ = 'lunzhy'
import platform, os, sys
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
if not path in sys.path:
    sys.path.append(path)
import pytaurus.sentaurus as sen

if platform.system() == 'Linux':
    #the file path of default parameter file
    Default_Param_Path = r'/home/lunzhy/SimCTM/default.param'

    #the directory path for debugging
    Debug_Directory = r'/home/lunzhy/SimCTM/debug'
elif platform.system() == 'Windows':
    pass

# method to convert CRLF with LF in parameter file because it may cause problems when reading them from SimCTM
def convertCRLFtoLF(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    newdata = data.replace(b'\r\n', b'\n')
    if newdata != data:
        print('converted')
        with open(file_path, 'wb') as f:
            f.write(newdata)
    return


def convertParamFile(prj_path):
    if platform.system() == 'Linux':
        default_param_path = Default_Param_Path
        user_param_path = os.path.join(prj_path, sen.User_Param_File)
        # convertCRLFtoLF(default_param_path)
        convertCRLFtoLF(user_param_path)
    return


if __name__ == '__main__':
    convertParamFile('/home/lunzhy/connect')