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
        
        #--method start time, per_well_action_time
        COMPILED = pd.concat(DATA)[[0, 3, 5, 8, 10, 'log_file']]
        COMPILED.columns = ['echo_well_pick_actionTime', '384_AGAR_PLATE', '384_AGAR_PLATE_WELL', '96_GROWTH_PLATE', 'Sample Name', 'log_file']
        COMPILED['EchoCherryPick_well_pick_actionTime'] = COMPILED['echo_well_pick_actionTime'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M:%S'))
        COMPILED['384_AGAR_PLATE_WELL'] = COMPILED['384_AGAR_PLATE_WELL'].apply(lambda x: self.PLATE384MAP.get_well(int(x)))
        COMPILED['Sample Name'] = COMPILED['Sample Name'].apply(lambda x: self.PLATE96MAP.get_well(int(x)))
        COMPILED['EchoCherryPick_method_start_time'] = COMPILED['log_file'].apply(lambda x: GROWTHINOC.get(x))
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


#--create dilution plates

class DilutionPlateCreator:
    def __init__(self, DIR, DF):
        self.DIR = DIR
        self.DF = DF
    
    def create_dilution_plates(self):
        DilutionPlate = {}
        GROWTHPLATE = {}

        for file in os.listdir(self.DIR):
            if file.endswith(r'.log'):
                PATH = os.path.join(self.DIR, file)
                with open(PATH, 'r') as f:
                    for line in f:
                        FILENAME = file
                        if re.search(r'Unit serial number', line) is not None:
                            serialNumber = line.split(r'=')[1].strip('\n').strip()
                        if re.search('Aspirate', line) and re.search('G[0-9]{1,9}', line) is not None:
                            GROWTHPLATE = re.search('G[0-9]{1,9}', line).group()
                            DILUTIONPLATE = re.search('D[0-9]{1,9}', next(iter(f))).group()
                            DilutionPlate.update({GROWTHPLATE: (DILUTIONPLATE, FILENAME)})

        self.DF['Dilution_Plate'] = self.DF['96_GROWTH_PLATE'].apply(lambda x: DilutionPlate.get(x)[0])
        self.DF['Dilution_Log'] = self.DF['96_GROWTH_PLATE'].apply(lambda x: DilutionPlate.get(x)[1])
        self.DF['Dilution_Autiomation_Serial_Number'] = serialNumber

        return self.DF
    
#--create glycerol stock plates

class GlycerolPlates:
    def __init__(self, DIR, DF):
        self.DIR = DIR 
        self.DF = DF
        self.serialNumber = None  # Initialize serialNumber here

    def convert(self):
        GlycerolPlates = []

        for file in os.listdir(self.DIR):
            if file.endswith(r'.log'):
                PATH = os.path.join(self.DIR, file)
                with open(PATH, 'r') as f:
                    for line in f:
                        FILENAME = file
                        if re.search(r'Unit serial number', line) is not None:
                            self.serialNumber = line.split('=')[1].strip('\n').strip()  # Store the serialNumber

        for file in os.listdir(self.DIR):
            if file.endswith(r'.log'):
                PATH = os.path.join(self.DIR, file)
                F1 = pd.read_csv(PATH, sep=',', skiprows=8, header=None)
                GlycerolPlates.append(F1)

        GP = pd.concat(GlycerolPlates)

        PLATES = GP[4].unique().tolist()
        PLATES.remove('Glycerol')

        GROWTH = []
        GLYCEROL = []

        for i in range(0, len(PLATES)):
            GRWTH = re.search('G[0-9]{1,9}', PLATES[i])
            GLYC = re.search('GLY[0-9]{1,9}', PLATES[i])
            if GRWTH is not None:
                GROWTH.append(GRWTH.group())
            if GLYC is not None:
                GLYCEROL.append(GLYC.group())

        GROWTH_GLYCEROL = dict(zip(GROWTH, GLYCEROL))

        self.DF['Glycerol_Plate'] = self.DF['96_GROWTH_PLATE'].apply(lambda x: GROWTH_GLYCEROL.get(x))
        self.DF['Glycerol_Autiomation_Serial_Number'] = self.serialNumber

        return self.DF
