"""Represent models for near-Earth objects and their close approaches.

The `NearEarthObject` class represents a near-Earth object. Each has a unique
primary designation, an optional unique name, an optional diameter, and a flag
for whether the object is potentially hazardous.

The `CloseApproach` class represents a close approach to Earth by an NEO. Each
has an approach datetime, a nominal approach distance, and a relative approach
velocity.

A `NearEarthObject` maintains a collection of its close approaches, and a
`CloseApproach` maintains a reference to its NEO.

The functions that construct these objects use information extracted from the
data files from NASA, so these objects should be able to handle all of the
quirks of the data set, such as missing names and unknown diameters.

"""
from helpers import cd_to_datetime, datetime_to_str


class NearEarthObject:
    """A near-Earth object (NEO).

    An NEO encapsulates semantic and physical parameters about the object, such
    as its primary designation (required, unique), IAU name (optional), diameter
    in kilometers (optional - sometimes unknown), and whether it's marked as
    potentially hazardous to Earth.

    A `NearEarthObject` also maintains a collection of its close approaches -
    initialized to an empty collection, but eventually populated in the
    `NEODatabase` constructor.
    """

    def __init__(self, **info):
        """Create a new `NearEarthObject`.

        :param info: A dictionary of excess keyword arguments supplied to the constructor.
        """
        self.designation = info['designation']
        self.name = None
        if info['name'] != '' and info['name'] is not None:
            self.name = info['name']
        self.diameter = float('nan')
        if info['diameter'] != '' and float(info['diameter']) != float('nan'):
            self.diameter = float(info['diameter'])
        self.hazardous = info['hazardous'] == "Y"
        self.approaches = []

    @property
    def fullname(self):
        """Return a representation of the full name of this NEO."""
        if self.name is None:
            return f"{self.designation}"
        else:
            return f"{self.designation} {self.name}"

    @property
    def finaldiameter(self):
        """Return a representation of the diameter of this NEO."""
        if self.diameter == float('nan'):
            return "unknown"
        else:
            return f"{self.diameter:.3f}"

    def __str__(self):
        """Return `str(self)`."""
        hazardousphrase = ''
        if self.hazardous:
            hazardousphrase = 'is potentially hazardous'
        else:
            hazardousphrase = 'is not potentially hazardous'
        return f"A NearEarthObject {self.fullname} has a diameter of {self.finaldiameter} km and {hazardousphrase}."

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation of this object."""
        return f"NearEarthObject(designation={self.designation!r}, name={self.name!r}, " \
               f"diameter={self.diameter:.3f}, hazardous={self.hazardous!r})"


class CloseApproach:
    """A close approach to Earth by an NEO.

    A `CloseApproach` encapsulates information about the NEO's close approach to
    Earth, such as the date and time (in UTC) of closest approach, the nominal
    approach distance in astronomical units, and the relative approach velocity
    in kilometers per second.

    A `CloseApproach` also maintains a reference to its `NearEarthObject` -
    initially, this information (the NEO's primary designation) is saved in a
    private attribute, but the referenced NEO is eventually replaced in the
    `NEODatabase` constructor.
    """

    def __init__(self, **info):
        """Create a new `CloseApproach`.

        :param info: A dictionary of excess keyword arguments supplied to the constructor.
        """
        self._designation = str(info['designation'])
        self.time = None
        if info['time'] is not None:
            self.time = cd_to_datetime(info['time'])
        self.distance = float(info['distance'])
        self.velocity = float(info['velocity'])

        # Create an attribute for the referenced NEO, originally None.
        self.neo = None

    @property
    def time_str(self):
        """Return a formatted representation of this `CloseApproach`'s approach time.

        The value in `self.time` should be a Python `datetime` object. While a
        `datetime` object has a string representation, the default representation
        includes seconds - significant figures that don't exist in our input
        data set.

        The `datetime_to_str` method converts a `datetime` object to a
        formatted string that can be used in human-readable representations and
        in serialization to CSV and JSON files.
        """
        return datetime_to_str(self.time)

    def serialize(self):
        """Return a dictionary that maps the CloseApproach objects.

        attribute name to its values.
        """
        serialized = {
            'datetime_utc': datetime_to_str(self.time),
            'distance_au': self.distance,
            'velocity_km_s': self.velocity,
            'neo': {
                'designation': self.neo.designation,
                'name': self.neo.name,
                'diameter_km': self.neo.diameter,
                'potentially_hazardous': self.neo.hazardous
              },
            }
        return serialized

    def __str__(self):
        """Return `str(self)`."""
        if self.neo:
            return f"At {self.time_str}, '{self.neo.fullname}' approaches "\
                   f" Earth at a distance of {self.distance:.2f} au and a "\
                   f"velocity of {self.velocity:.2f} km/s."
        else:
            return f"At {self.time_str}, '{self._designation}' approaches "\
                    f"Earth at a distance of {self.distance:.2f} au and a "\
                    f"velocity of {self.velocity:.2f} km/s."

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation of.

        this object.
        """
        return (f"CloseApproach(time={self.time_str!r}, "
                f"distance={self.distance:.2f}, velocity={self.velocity:.2f}, "
                f"neo={self.neo!r})")
