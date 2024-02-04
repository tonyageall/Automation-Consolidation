import pandas as pd
import numpy as np 
from datetime import datetime
import os
import re

#--takes in the previous meta data and directory to log files
class GetDilutionPlates:
    def __init__(self, Input, Dir):
        self.Dplates = []
        self.Input = Input
        self.Dir = Dir
        self.sol = {}
        self.insol = {}

    def getDplates(self):
        self.Dplates = self.Input.Dilution_Plate.unique()

    
    def getCGEPlates(self):

        SOL = []
        INSOL = []
        SOLPLATES = {}
        INSOLPLATES = {}

        for file in os.listdir(self.Dir):
                    if file.endswith('.log'):
                        PATH = os.path.join(self.Dir, file)
                        f1 = open(PATH, 'r').readlines()
                        DILUTIONPLATE = [item for item in f1 if re.search(r'D[0-9]{1,9}', item)]
                        for item in DILUTIONPLATE:
                                META = item.split(',')
                                DIL = META[5]
                                PLA = META[4]
                                TIME = datetime.strptime(META[0], '%m/%d/%Y %H:%M:%S')
                                if PLA not in (SOL and INSOL):
                                    if re.search(r'S', PLA) != None:
                                            SOL.append(PLA)
                                            try:
                                                if SOLPLATES.get(DIL) != PLA:
                                                    SOLPLATES.update({DIL:PLA})
                                                else:
                                                    continue
                                            except:
                                                SOLPLATES.update({DIL:PLA})
                                    
                                    if re.search(r'I', PLA) != None:
                                            INSOL.append(PLA)
                                            try:
                                                if INSOLPLATES.get(DIL) != PLA:
                                                    INSOLPLATES.update({DIL:PLA})
                                                else:
                                                    continue
                                            except:
                                                INSOLPLATES.update({DIL:PLA})
                                else:
                                    continue
        self.sol = SOLPLATES
        self.insol = INSOLPLATES
                        
#-- not sure if these methods should be called like this but this seems useful and a little more modular

    def Analyzed_Plates_Sol(self, Input):
        if self.sol.get(Input) is None:
            return 'Not Analyzed'
        else:
            return self.sol.get(Input)

    def Analyzed_Plates_ISol(self, Input):
        if self.insol.get(Input) is None:
            return 'Not Analyzed'
        else:
            return self.insol.get(Input)
        
#-- create a class to convert Sol and Insol plates to associated reduced/non-reduced plates
class ReducedNonReducedPlateConverter:
    def __init__(self, DIR):
        self.SOL_REDUCED_PLATES = {}
        self.INSOL_REDUCED_PLATES = {}
        self.PLATES = []
        self.DIR = DIR

    def collectPlates(self):
        self.PLATES = []
        for file in os.listdir(self.DIR):
            if file.endswith('.log'):
                PATH = os.path.join(self.DIR, file)
                F1 = pd.read_csv(PATH, sep=',', skiprows=8, header=None)
                self.PLATES.append(F1)

        SOL_INSOL = pd.concat(self.PLATES)[4].unique().tolist()
        self.PLATES = SOL_INSOL

    def collectReducedPlates(self):
        for i in range(0, len(self.PLATES)):
            try:
                if re.search(r'S[0-9]{1,9}', self.PLATES[i]) is not None:
                    sol = re.search(r'S[0-9]{1,9}', self.PLATES[i]).group()
                    red = re.search('RED[0-9]{1,9}', self.PLATES[i+1]).group()
                    self.SOL_REDUCED_PLATES.update({sol: red})
                if re.search(r'I[0-9]{1,9}', self.PLATES[i]) is not None:
                    isol = re.search(r'I[0-9]{1,9}', self.PLATES[i]).group()
                    red = re.search('RED[0-9]{1,9}', self.PLATES[i+1]).group()
                    self.INSOL_REDUCED_PLATES.update({isol: red})
            except IndexError:
                break

    def Analyzed_CGEPlates_Sol(self, Input):
        if self.SOL_REDUCED_PLATES.get(Input) is None:
            return 'Not Analyzed'
        else:
            return self.SOL_REDUCED_PLATES.get(Input)
    
    def Analyzed_CGEPlates_ISol(self, Input):
        if self.INSOL_REDUCED_PLATES.get(Input) is None:
            return 'Not Analyzed'
        else:
            return self.INSOL_REDUCED_PLATES.get(Input)




