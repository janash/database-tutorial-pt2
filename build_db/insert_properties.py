import csv
from sqlmodel import Session, select, create_engine
from models import Property, Coordinates

# Function to insert property data from CSV into the database
def insert_properties_from_csv(db_url: str, csv_file_path: str):
    # Create the database engine
    engine = create_engine(db_url)

    # Omit create_all() since the tables are already created

    # Read the CSV file
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        with Session(engine) as session:
            for row in reader:
                # Extract CSD_code and property values
                csd_code = row['CSD_code']
                properties = {
                    'Electronic_E': float(row['Electronic_E']),
                    'Dispersion_E': float(row['Dispersion_E']),
                    'Dipole_M': float(row['Dipole_M']),
                    'Metal_q': float(row['Metal_q']),
                    'HL_Gap': float(row['HL_Gap']),
                    'HOMO_Energy': float(row['HOMO_Energy']),
                    'LUMO_Energy': float(row['LUMO_Energy']),
                    'Polarizability': float(row['Polarizability'])
                }

                # Query the Coordinates table to get the coordinates_id for the given structure_id (csd_code)
                coordinates = session.exec(select(Coordinates).where(Coordinates.structure_id == csd_code)).first()

                if coordinates is None:
                    print(f"No coordinates found for structure {csd_code}, skipping.")
                    continue

                # Insert each property into the Property table using coordinates_id
                for prop, value in properties.items():
                    property_instance = Property(
                        coordinates_id=coordinates.id,  # Use coordinates_id instead of structure_id
                        property=prop,
                        value=value
                    )
                    session.add(property_instance)

            # Commit the session to save all changes
            session.commit()
    print("Property data inserted successfully from CSV.")

# Example usage
db_url = "sqlite:///tmqm_4.db"  # Path to your existing SQLite database
csv_file_path = "tmQM_y.csv"  # Replace with the actual path to your CSV file
insert_properties_from_csv(db_url, csv_file_path)
