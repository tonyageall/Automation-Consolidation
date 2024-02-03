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

    def getInsolPlates(self):
        self.Dplates = self.Input.Dilution_Plate.unique()
        for file in os.listdir(self.Dir):
            if file.endswith('.log'):
                PATH = os.path.join(self.Dir, file)
                f1 = open(PATH, 'r').readlines()
                DILUTIONPLATE = [item for item in f1 if re.search(r'D[0-9]{1,9}', item)]
                for item in DILUTIONPLATE:
                    INSOL = re.search(r'I[0-9]{1,9}', item)
                    DILUTION = re.search(r'D[0-9]{1,9}', item)
                    
                    if INSOL and DILUTION is not None:
                        INSOL = INSOL.group()
                        DILUTION = DILUTION.group()
                        self.insol.update({DILUTION: INSOL})
                    else:
                        INSOL = 'No INSOL Found'
                        DILUTION = DILUTION.group()
                        self.sol.update({DILUTION: INSOL})

                    

    def getSolPlates(self):
        self.Dplates = self.Input.Dilution_Plate.unique()
        for file in os.listdir(self.Dir):
            if file.endswith('.log'):
                PATH = os.path.join(self.Dir, file)
                f1 = open(PATH, 'r').readlines()
                DILUTIONPLATE = [item for item in f1 if re.search(r'D[0-9]{1,9}', item)]
                for item in DILUTIONPLATE:
                    SOL = re.search(r'S[0-9]{1,9}', item)
                    DILUTION = re.search(r'D[0-9]{1,9}', item)
                    
                    if SOL and DILUTION is not None:
                        SOL = SOL.group()
                        DILUTION = DILUTION.group()
                        self.sol.update({DILUTION: SOL})
                    else:
                        SOL = 'No SOL Found'
                        DILUTION = DILUTION.group()
                        self.sol.update({DILUTION: SOL})
                    
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




