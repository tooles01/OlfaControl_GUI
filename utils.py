import logging, os, glob
from datetime import datetime
import config_main


#################################
# TIME
currentDate = str(datetime.date(datetime.now()))

def get_current_time():
    current_time = datetime.time(datetime.now())
    current_time_f = current_time.strftime('%H:%M:%S.%f')
    current_time_str = current_time_f[:-3]

    return current_time_str



#################################
# LOGGING
def create_file_handler(log_dir):
    '''
    Returns file handler for logger: 'logfile_<today's date>.txt'
        Level set to 'INFO'
        Path is log_dir
    '''

    file_name = 'logfile_{}.txt'.format(currentDate)
    logFilePath = log_dir + '\\' + file_name
    
    file_handler_level = logging.INFO
    file_handler_formatter = logging.Formatter('%(asctime)s.%(msecs)03d : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    file_handler = logging.FileHandler(logFilePath,mode='a')
    file_handler.setLevel(file_handler_level)
    file_handler.setFormatter(file_handler_formatter)
    
    return file_handler

def create_console_handler():   # TODO: user sends log level to this function
    '''
    Returns console handler for logger
        Set level to 'DEBUG'
    '''
    
    console_handler_level = logging.DEBUG
    console_handler_formatter = logging.Formatter('%(asctime)s : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_handler_level)
    console_handler.setFormatter(console_handler_formatter)
    
    return console_handler



#################################
# FIND DIRECTORIES
def find_olfaControl_directory():
    str_to_find = '/**/*OlfaControl_GUI*'
    
    # Search C:\\GIT for paths containing OlfaControl_GUI
    c_drive_git_path = os.path.expanduser('C:\\GIT\\')
    path_list = glob.glob(c_drive_git_path + '/**/*' + str_to_find,recursive=True)
    
    # If not found: search Dropbox
    if not path_list:
        c_drive_git_path = os.path.expanduser('~\\Dropbox')
        path_list = glob.glob(c_drive_git_path + '/**/*' + str_to_find,recursive=True)
    
    # If not found: search Dropbox (NYU Langone Health)
    if not path_list:
        c_drive_git_path = os.path.expanduser('~\\Dropbox (NYU Langone Health)')
        path_list = glob.glob(c_drive_git_path + str_to_find, recursive=True)
    
    # If not found: print warning
    if not path_list:
        gui_directory = []
        #logger.debug('can\'t find OlfaControl_GUI folder :/')
    
    # If found: use the first path listed
    else:
        # If multiple paths found: print (for user)
        if len(path_list) > 1:
            logger.debug('Multiple OlfaControl_GUI paths found:')
            # TODO ignore the .code-workspace files
            for i in path_list:
                logger.debug('\t' + i)
        
        gui_directory = path_list[0]
        logger.debug('OlfaControl_GUI directory found at:\t' + gui_directory)
    
    return gui_directory    # type is list

def find_log_directory():
    # Check for OlfaControl_GUI directory
    olfacontrolgui_directory = find_olfaControl_directory()

    # If not found: use the directory we are currently in
    if not olfacontrolgui_directory:
        directory_to_save_to = os.getcwd()
    else:
        directory_to_save_to = olfacontrolgui_directory
    
    # check if there is a folder called result files
    result_file_directory = directory_to_save_to + '\\' + config_main.result_file_folder_name
    
    # If folder does not exist, create it
    if not os.path.exists(result_file_directory):
        logger.info('creating result file directory at %s', result_file_directory)
        os.mkdir(result_file_directory)
    
    return result_file_directory

def find_calibration_table_directory():
    # check for OlfaControl_GUI directory
    olfacontrolgui_directory = find_olfaControl_directory()

    # if not found, use whatever directory we are currently in
    if not olfacontrolgui_directory:
        directory_to_search = os.getcwd()
    else:
        directory_to_search = olfacontrolgui_directory

    # check if there is a folder called calibration tables
    calibration_table_directory = directory_to_search + '\\' + config_main.calibration_file_dir_name

    return calibration_table_directory



#################################
logger = logging.getLogger(name='utils')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = create_console_handler()
logger.addHandler(console_handler)