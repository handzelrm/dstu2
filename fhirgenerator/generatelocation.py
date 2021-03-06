import generatebase

import fhirclient.models.address as a
import fhirclient.models.location as l
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))


class GenerateLocation(generatebase.GenerateBase):
    location_status = 'active'
    location_name = 'UPMC Magee Clinic'
    location_line = ["Magee-Women's Hospital of UPMC, Halket Street"]
    location_city = 'Pittsburgh'
    location_postalCode = '15213'
    location_state = 'PA'
    location_longitude = -79.960779
    location_latitude = 40.437123

    def __init__(self):
        """
        Uses fhirclient.models to create and post location resource. Currently, using class variables.

        :returns: GenerateLocation object that has Location object as an attribute.
        """
        Location = l.Location()
        LocationPosition = l.LocationPosition()
        Address = a.Address()
        Location.status = 'active'
        Location.name = self.location_name
        Address.line = self.location_line
        Address.city = self.location_city
        Address.postalCode = self.location_postalCode
        Address.state = self.location_state
        Location.address = Address
        LocationPosition.latitude = self.location_latitude
        LocationPosition.longitude = self.location_longitude
        Location.position = LocationPosition
        # self._validate(Location)
        self.response = self.post_resource(Location)
        Location.id = self._extract_id()
        self.Location = Location
        print(self)

    def __str__(self):
        return f'{self.Location.__class__.__name__}:{self.location_name}; id: {self.Location.id}'

    @staticmethod
    def __repr__():
        return 'GenerateLocation()'

if __name__ == '__main__':
    GenerateLocation()
