import random
import pandas as pd 
import numpy as np
from neo4j import GraphDatabase


#--gather nodes and node ID's
class getPlateDB:
    def __init__(self, node_id, plate_type):
        self.PlateCatalogue = []
        self.node_id = node_id  # Use a private variable to store node_id
        self.plate_type = plate_type  # Use a private variable to store plate_type


    def get_plates_property(self, node_id, uri, username, password):
        query = (
        f"MATCH (node:{node_id}) "
        "RETURN node.Plates AS platesProperty"
        )

        
        plates_property_list = []  # Initialize an empty list to store results

        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                result = session.run(query)

                # Extract the platesProperty from the result and add to the list
                for record in result:
                    plates_property = record["platesProperty"]
                    plates_property_list.extend(plates_property)  # Extend the list


        self.PlateCatalogue = plates_property_list


#--this will generate a random set of numbers and extensions to generate barcodes
class generate_random_numbers_extensions:
    def __init__(self, PlateNumber, extension, PlateCatalogue):
        self.PlateNumber = PlateNumber  # number of plates to generate
        self.extension = extension  # ID extension
        self.PlateCatalogue = PlateCatalogue  # current list of plates

    def generate_random_numbers(self):
        used_numbers = self.PlateCatalogue
        extension = self.extension
        plates_to_generate = self.PlateNumber  # Number of plates to generate
        plates_generated = 0  # Counter for plates generated
        new_plates = []
        while plates_generated < plates_to_generate:
            # Generate a random number
            new_number = random.randint(1, 999999)
            

            # Format the number as 'R' followed by a zero-padded 6-digit numeric value
            formatted_number = f'{extension}{new_number:06d}'
            

            # Check if the number has already been used
            if formatted_number not in used_numbers:
                used_numbers.append(formatted_number)
                new_plates.append(formatted_number)
                plates_generated += 1  # Increment the counter

        return used_numbers, new_plates
    
#--add to nodes in the database
class addPlatesToDB:
    def __init__(self, node_id, plate_type, PlateCatalogue):
        self.node_id = node_id  # Use a private variable to store node_id
        self.plate_type = plate_type  # Use a private variable to store plate_type
        self.PlateCatalogue = PlateCatalogue  # current list of plates
        

    def replace_list_property(self, uri, username, password):
        query = (
            f"MATCH(p:{self.node_id}) "
            f"SET p.{self.plate_type} = {self.PlateCatalogue}"
        )

        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                session.run(query)


class generate_wells:
    def __init__(self, plateType, PlateBarCode, wells):
        self.PlateBarCode = PlateBarCode
        self.wells = wells
        self.plateType = plateType

    def add_wells(self, uri, username, password):
        query = (
            f"MATCH (node:{self.plateType}) WHERE node.PlateBarCode = $PlateBarCode "
            "SET node.Wells = $wells"
        )
        parameters = {"PlateBarCode": self.PlateBarCode, "wells": self.wells}
        
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                session.run(query, parameters)


