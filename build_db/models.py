from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class Structure(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    num_atoms: int = Field(index=True)
    stoichometry: str = Field(index=True)
    q: int = Field(index=True)
    S: int = Field(index=True)
    MND: int = Field(index=True)

    coordinates: List["Coordinates"] = Relationship(back_populates="structure")

class Coordinates(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    structure_id: str = Field(foreign_key="structure.id", index=True)
    xyz: str

    structure: "Structure" = Relationship(back_populates="coordinates")
    properties: List["Property"] = Relationship(back_populates="coordinates")

class Property(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    coordinates_id: str = Field(foreign_key="coordinates.id", index=True)  
    property: str = Field(index=True)  # Name of the property (e.g., "energy", "dipole moment")
    value: float = Field(index=True)   # Value of the propertyclear

    coordinates: "Coordinates" = Relationship(back_populates="properties")
