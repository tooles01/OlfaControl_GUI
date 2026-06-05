import logging, os
from datetime import datetime
import config_main

currentDate = str(datetime.date(datetime.now()))
calibration_file_dir_name = 'calibration_tables'



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
    file_handler_formatter = logging.Formatter('%(asctime)s.%(msecs)03d : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    file_handler = logging.FileHandler(logFilePath,mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_handler_formatter)
    
    return file_handler

def create_console_handler():
    '''
    Returns console handler for logger
        Set level to 'DEBUG'
    '''

    console_handler_formatter = logging.Formatter('%(asctime)s : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_handler_formatter)
    
    return console_handler



#################################
# FIND DIRECTORIES
def find_olfaControl_directory():
    """Find "OlfaControl_GUI" directory"""
    
    str_to_find = 'OlfaControl_GUI'
    path_list = []

    # Check if we are already in the folder
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    for root, dirs, files in os.walk(parent_dir):
         if str_to_find in dirs:
            path_list.append(os.path.join(root, str_to_find))
            break
    
    # If still not found: search C:\\GIT
    if not path_list:
        dir_to_search = 'C:\\GIT\\'
        for root, dirs, files in os.walk(dir_to_search):
            if str_to_find in dirs: path_list.append(os.path.join(root, str_to_find))
            
    # If still not found: search Dropbox
    if not path_list:
        dir_to_search = os.path.expanduser('~\\Dropbox*')    # idk if this will work
        for root, dirs, files in os.walk(dir_to_search):
            if str_to_find in dirs: path_list.append(os.path.join(root, str_to_find))
    
    # If still not found: print warning
    if not path_list:
        gui_directory = []
        #logger.debug('can\'t find OlfaControl_GUI folder :/')
    
    # If found: use the first path listed
    else:
        # Ignore .code-workspace files
        str_to_exclude = ".code-workspace"
        path_list = [item for item in path_list if str_to_exclude not in item]
        
        # If multiple paths found: print (for user)
        if len(path_list) > 1:
            logger.debug('Multiple OlfaControl_GUI paths found:')
            for i in path_list:
                logger.debug('\t' + i)
        
        gui_directory = path_list[0]
        logger.debug('OlfaControl_GUI directory found at:\t' + gui_directory)
    
    return gui_directory    # type is string

def find_log_directory():
    '''
    Returns directory where log file will be stored
        result_file_directory = directory_to_save_to + "\\result_files"
            directory_to_save_to = either OlfaControl_GUI or current directory
    '''
    
    # Get directory where result files will be stored
    # If "..\OlfaControl_GUI" not found, use current working director
    olfacontrolgui_directory = find_olfaControl_directory()
    if not olfacontrolgui_directory:
        directory_to_save_to = os.getcwd()
    else:
        directory_to_save_to = olfacontrolgui_directory
    
    # Get/create result_file_directory
    result_file_directory = directory_to_save_to + '\\' + config_main.result_file_folder_name
    if not os.path.exists(result_file_directory):   # If folder does not exist, create it
        logger.info('creating result file directory at %s', result_file_directory)
        os.mkdir(result_file_directory)
    
    return result_file_directory


#################################
logger = logging.getLogger(name='utils')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = create_console_handler()
logger.addHandler(console_handler)