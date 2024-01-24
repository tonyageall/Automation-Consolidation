import pandas as pd
import numpy as np 
from datetime import datetime
import os
import re

#--turned into object 384 map
class Plate384Map:
    def __init__(self):
        self.ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        self.WELLS = {}
        self.generate_wells()

    def generate_wells(self):
        j = 1
        for row in self.ROWS:
            for i in range(1, 25):
                WELL = row + str(i)
                self.WELLS[j] = WELL
                j = j + 1

    def get_well(self, WELLNUMBER):
        return self.WELLS.get(WELLNUMBER)


#--turned into object 96 map
class Plate96Map:
    def __init__(self):
        self.ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.WELLS = {}
        self.generate_wells()

    def generate_wells(self):
        j = 1
        for row in self.ROWS:
            for i in range(1, 13):
                WELL = row + str(i)
                self.WELLS[j] = WELL
                j = j + 1

    def get_well(self, WELLNUMBER):
        return self.WELLS.get(WELLNUMBER)
    
#--scrape intial log files for well to well matching and datetime addition

class PlateConverter:
    def __init__(self, DIRS):
        self.DIRS = DIRS
        self.PLATE384MAP = Plate384Map()
        self.PLATE96MAP = Plate96Map()

    def convert(self):
        DATA = []
        GROWTHINOC = {}
        SERIALNUM = {}

        for file in os.listdir(self.DIRS):
            if file.endswith(r'.log'):
                PATH = os.path.join(self.DIRS, file)
                f1 = open(PATH, 'r').readlines()[10:]
                D1 = np.loadtxt(f1, dtype=object, delimiter=',')
                data = pd.DataFrame(D1)
                data['log_file'] = file
                DATA.append(data)

                with open(PATH, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:9]:
                        if line.startswith(r'Started'):
                            TIME = re.search(r'[0-9]{0,2}/[0-9]{0,2}/[0-9]{0,4} [0-9]{2}:[0-9]{2}:[0-9]{2}', line)
                            datetime_object = datetime.strptime(TIME.group(), '%m/%d/%Y %H:%M:%S')
                            GROWTHINOC[file] = datetime_object
                        if line.startswith(r'Unit'):
                            SERIAL = line.strip('\n').split(r'=')[1]
                            SERIALNUM[file] = SERIAL

        COMPILED = pd.concat(DATA)[[3, 5, 8, 10, 'log_file']]
        COMPILED.columns = ['384_AGAR_PLATE', '384_AGAR_PLATE_WELL', '96_GROWTH_PLATE', 'Sample Name', 'log_file']
        COMPILED['384_AGAR_PLATE_WELL'] = COMPILED['384_AGAR_PLATE_WELL'].apply(lambda x: self.PLATE384MAP.get_well(int(x)))
        COMPILED['Sample Name'] = COMPILED['Sample Name'].apply(lambda x: self.PLATE96MAP.get_well(int(x)))
        COMPILED['Growth_Inoculation_Time'] = COMPILED['log_file'].apply(lambda x: GROWTHINOC.get(x))
        COMPILED['Autiomation_SerialNum'] = COMPILED['log_file'].apply(lambda x: SERIALNUM.get(x))

        result = None  # Define result before merging

        for file in os.listdir(self.DIRS):
            if file.endswith(r'.csv'):
                df = os.path.join(self.DIRS, file)
                data = pd.read_csv(df, skiprows=10, usecols=['Source Plate Name', 'Source Plate Barcode', 'Source Well', 'Destination Plate Barcode']).fillna('None')
                data_cieve = data[data['Destination Plate Barcode'] != 'None']
                data_cieve.columns = ['ECHO_Source Plate Name', 'ECHO_Source Plate Barcode', 'ECHO_Source Well', '384_AGAR_PLATE']

                if result is None:
                    result = data_cieve
                else:
                    result = result.merge(data_cieve, on='384_AGAR_PLATE')

        return result.merge(COMPILED, on='384_AGAR_PLATE')


