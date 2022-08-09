import logging, math
import utils

logger = logging.getLogger(name='utils_48line_olfa')
logger.setLevel(logging.DEBUG)
if logger.hasHandlers():    logger.handlers.clear()     # removes duplicate log messages
console_handler = utils.create_console_handler()
logger.addHandler(console_handler)


# CONNECT TO 48 LINE OLFA
def connect_to_48line_olfa(parent):
    parent.olfactometer.get_ports()

    # find Arduino port
    for item_idx in range(0,parent.olfactometer.port_widget.count()):
        this_item = parent.olfactometer.port_widget.itemText(item_idx)
        if 'Arduino' in this_item:
            break
    # connect to Arduino port
    if item_idx != []:
        logger.debug('setting olfa port widget to arduino port')
        parent.olfactometer.port_widget.setCurrentIndex(item_idx)
        logger.debug('connecting olfactometer')
        parent.olfactometer.connect_btn.toggle()
    else:
        logger.info('no arduinos detected')

# FLOW SENSOR CONVERSIONS
def convertToInt(SCCMval, dictionary):
    SCCMval = float(SCCMval)
    if SCCMval in dictionary:   ardVal = dictionary.get(SCCMval)
    else:
        minVal = min(dictionary)
        maxVal = max(dictionary)
        if SCCMval < minVal:    ardVal = dictionary.get(minVal)
        elif SCCMval > maxVal:  ardVal = dictionary.get(maxVal)
        else:
            if SCCMval.is_integer() == False:
                val1 = math.floor(SCCMval)
            else:
                val1 = SCCMval-1
            flow1 = dictionary.get(val1)
            while flow1 is None:
                val1 = val1-1
                flow1 = dictionary.get(val1)
            if SCCMval.is_integer() == False:
                val2 = math.ceil(SCCMval)
            else:
                val2 = SCCMval+1
            flow2 = dictionary.get(val2)
            while flow2 is None:
                val2 = val2+1
                flow2 = dictionary.get(val2)

            slope = (flow2-flow1)/(val2-val1)
            x1 = SCCMval - val1
            addNum = x1*slope
            ardVal = flow1 + addNum
    
    ardVal = round(ardVal)
    return int(ardVal)


def convertToSCCM(ardVal, dictionary):
    if ardVal in dictionary:    val_SCCM = dictionary.get(ardVal)
    else:
        minVal = min(dictionary)
        maxVal = max(dictionary)
        if ardVal < minVal:     val_SCCM = dictionary.get(minVal)
        elif ardVal > maxVal:   val_SCCM = dictionary.get(maxVal)
        else:
            val1 = ardVal-1
            flow1 = dictionary.get(val1)
            while flow1 is None:
                val1 = val1-1
                flow1 = dictionary.get(val1)
            val2 = ardVal+1
            flow2 = dictionary.get(val2)
            while flow2 is None:
                val2 = val2+1
                flow2 = dictionary.get(val2)
            
            slope = (flow2-flow1)/(val2-val1)
            x1 = ardVal - val1
            addNum = x1*slope
            val_SCCM = flow1 + addNum
            val_SCCM = round(val_SCCM,1)

    return val_SCCM
