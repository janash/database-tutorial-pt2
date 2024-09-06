import os
from typing import Optional, List
from sqlmodel import Field, SQLModel, Session, create_engine, select
from sqlalchemy.exc import IntegrityError

from models import *

# Function to read XYZ file (from the previous script)
def read_xyz_file(file_path):
    molecules = []  # List to store all molecules

    with open(file_path, 'r') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        # Read the number of atoms
        num_atoms = int(lines[i].strip())

        # Read the comment line
        comment_line = lines[i + 1].strip()

        # Read the molecule's atom coordinates
        atom_coordinates = []
        for j in range(num_atoms):
            atom_coordinates.append(lines[i + 2 + j].strip())

        # Construct the XYZ format string
        constructed_xyz = f"{num_atoms}\n{comment_line}\n"
        constructed_xyz += "\n".join(atom_coordinates)
        
        # Store the molecule data as a dictionary
        molecule_data = {
            'num_atoms': num_atoms,
            'comment': comment_line,
            'coordinates': constructed_xyz
        }
        molecules.append(molecule_data)

        # Move to the next molecule block
        i += num_atoms + 3

    return molecules

# Function to populate the database
def populate_database(db_url: str, xyz_file_path: str):
    # Create the database engine
    engine = create_engine(db_url)

    # Create tables if they do not exist
    SQLModel.metadata.create_all(engine)

    # Read molecules from the XYZ file
    molecules = read_xyz_file(xyz_file_path)

    with Session(engine) as session:
        for mol in molecules:
            comment_parts = mol['comment'].split("|")
            comment_dict = {}

            # Parse the comment line into a dictionary
            for part in comment_parts:
                key, value = part.split("=")
                comment_dict[key.strip()] = value.strip()

            # Create a unique ID for each structure
            structure_id = comment_dict.get('CSD_code', None)

            # Create a Structure instance
            structure = Structure(
                id=structure_id,
                stoichometry=comment_dict["Stoichiometry"],
                num_atoms=mol['num_atoms'],
                q=int(comment_dict["q"]),
                S=int(comment_dict["S"]),
                MND=int(comment_dict["MND"])
            )

            # Add structure to the session
            try:
                session.add(structure)
                session.commit()
            except IntegrityError:
                session.rollback()
                print(f"Structure with ID {structure_id} already exists.")

            # Create a Coordinates instance
            coordinates = Coordinates(
                id=f"{structure_id}_coords",
                structure_id=structure_id,
                xyz=mol['coordinates']
            )

            # Add coordinates to the session
            session.add(coordinates)
            session.commit()
    
    print("Database population complete.")

# Example usage
db_url = "sqlite:///tmqm_4.db"
xyz_file_path = "tmQM_X.xyz"
populate_database(db_url, xyz_file_path)
