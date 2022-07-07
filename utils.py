import logging
from datetime import datetime

currentDate = str(datetime.date(datetime.now()))


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


def get_current_time():
    current_time = datetime.time(datetime.now())
    current_time_f = current_time.strftime('%H:%M:%S.%f')
    current_time_str = current_time_f[:-3]

    return current_time_str