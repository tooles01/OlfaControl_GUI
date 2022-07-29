import logging, os, glob
from datetime import datetime


# TIME
currentDate = str(datetime.date(datetime.now()))

def get_current_time():
    current_time = datetime.time(datetime.now())
    current_time_f = current_time.strftime('%H:%M:%S.%f')
    current_time_str = current_time_f[:-3]

    return current_time_str


# LOGGING
def create_file_handler(log_dir):    # TODO: add file_name to variables it takes
    file_name = 'logfile_{}.txt'.format(currentDate)
    logFilePath = log_dir + '\\' + file_name
    
    file_handler_level = logging.INFO
    file_handler_formatter = logging.Formatter('%(asctime)s.%(msecs)03d : %(name)-14s :%(levelname)-8s: %(message)s',datefmt='%H:%M:%S')
    file_handler = logging.FileHandler(logFilePath,mode='a')
    file_handler.setLevel(file_handler_level)
    file_handler.setFormatter(file_handler_formatter)

    return file_handler

def create_console_handler():   # TODO: user sends log level to this function
    console_handler_level = logging.DEBUG
    console_handler_formatter = logging.Formatter('%(name)-14s: %(levelname)-8s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_handler_level)
    console_handler.setFormatter(console_handler_formatter)

    return console_handler



# FIND DIRECTORIES
def find_olfaControl_directory():
    str_to_find = '/**/*OlfaControl_GUI*'
    
    # search C:\\GIT for OlfaControl_GUI
    c_drive_path = os.path.expanduser('C:\\GIT\\')
    path_list = glob.glob(c_drive_path + '/**/*' + str_to_find,recursive=True)
    if not path_list:
        # search in Dropbox
        c_drive_path = os.path.expanduser('~\\Dropbox')
        path_list = glob.glob(c_drive_path + '/**/*' + str_to_find,recursive=True)
        if not path_list:
            # search in Dropbox again
            c_drive_path = os.path.expanduser('~\\Dropbox (NYU Langone Health)')
            path_list = glob.glob(c_drive_path + str_to_find,recursive=True)
    
    # if you can't find it anywhere
    if not path_list:
        gui_directory = []
        logger.warning('can\'t find OlfaControl_GUI folder :/')
    else:
        gui_directory = path_list[0]
    
    return gui_directory

def find_datafile_directory():
    folder_to_save_to = 'result_files'
    
    olfaControl_dir = find_olfaControl_directory()
    if not olfaControl_dir:
        # yolo
        c_drive_path = os.path.expanduser('C:\\')
        save_files_to = c_drive_path + '\\' + folder_to_save_to
        #if not os.path.exists(save_files_to): os.mkdir(save_files_to)
    else:
        save_files_to = olfaControl_dir + '\\' + folder_to_save_to
    #save_files_to = c_drive_path + '\\' + folder_to_save_to
    if not os.path.exists(save_files_to): os.mkdir(save_files_to)

    #logger.debug('saving result files to %s',save_files_to)
    
    return save_files_to




############################################
logger = logging.getLogger(name='utils')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = create_console_handler()
logger.addHandler(console_handler)