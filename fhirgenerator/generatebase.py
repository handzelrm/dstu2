import fhirclient.models.codeableconcept as cc
import fhirclient.models.coding as c
import fhirclient.models.fhirdate as fd
import fhirclient.models.fhirreference as fr
import fhirclient.models.period as period
import fhirclient.models.quantity as q
from fhirclient import client
from fhirclient import server
from fhirclient import auth

from pytz import timezone
import json
import pandas as pd
import numpy as np
import random
import requests
import re
import datetime
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class GenerateBase():
    """Base class used to share common methods used within other generate classes"""
    @staticmethod
    def _generate_vitals():
        """
        Generates a set of vitals using a normal distribution times 10

        :returns: sbp, dbp, hr
        """
        avg_sbp = 120
        avg_dbp  = 80
        diff = int(np.random.normal(0,1)*10)
        sbp = avg_sbp + diff
        dbp = avg_dbp + diff

        avg_hr = 80
        diff = int(np.random.normal(0,1)*10)
        hr = avg_hr + diff
        return sbp, dbp, hr

    @staticmethod
    def _generate_height_weight(sex):
        """
        Generates height and weight roughly inline with US stats.

        :param sex: sex of person
        :returns: height, weight
        """
        avg_height_male = 69.2
        std_height_male = 4
        avg_height_female = 63.7
        std_height_female = 3.5

        avg_weight_male = 195.7
        std_weight_male = 30
        avg_weight_female = 168.5
        std_weight_female = 25

        if sex =='unknown':
            sex = random.choice(['male','female'])
        if sex == 'male':
            height = np.random.normal(avg_height_male,std_height_male)
            weight = np.random.normal(avg_weight_male,std_weight_male)
        elif sex == 'female':
            height = np.random.normal(avg_height_female,std_height_female)
            weight = np.random.normal(avg_weight_female,std_weight_female)
        else:
            raise ValueError('sex error')
        return height, weight

    @staticmethod
    def _get_smoking_loinc():
        """
        Uses a get request from LOINC to obtain a list of smoking statuses and returns a random one.

        :returns smoke_loinc, smoke_description
        """
        df = pd.read_html('https://s.details.loinc.org/LOINC/72166-2.html?sections=Comprehensive')[5]
        df.columns = df.iloc[3,:]
        df = df.iloc[4:,[3,5]]
        df.columns = ['description','loinc']
        smoke_description = random.choice(df.description.tolist())
        smoke_loinc = df[df.description==smoke_description].loinc.values[0]
        return smoke_loinc, smoke_description

    @staticmethod
    def _create_FHIRReference(resource):
        """
        Used to create a FHIR reference object based on a FHIRClient.models object

        :param resource: FHIRClient.models class object (i.e. Patient())
        :returns: FHIRReference object
        """
        FHIRReference = fr.FHIRReference()
        FHIRReference.reference = f'{resource.resource_name}/{resource.id}'
        return FHIRReference

    @staticmethod
    def _create_FHIRDate(date):
        """
        Creates a FHIRDate object

        :param date: datetime object used to set the date in the FHIRDate object
        :returns: FHIRDate object
        """
        eastern = timezone('US/Eastern')
        FHIRDate = fd.FHIRDate()
        FHIRDate.date = date.astimezone(eastern)
        return FHIRDate

    def _create_FHIRPeriod(self,start=None,end=None):
        """
        Creates a FHIRPeriod object

        :param self: needed to call _create_FHIRDate method
        :param start: start datetime object
        :param end: end datetime object
        :returns: FHIRPeriod object
        """
        Period = period.Period()
        if start is not None:
            Period.start = self._create_FHIRDate(start)
        else:
            Period.start = self._create_FHIRDate(datetime.datetime.now())
        if end is not None:
            Period.end = self._create_FHIRDate(end)
        return Period


    def _extract_id(self):
        """
        Uses regex to parse out the id from the server response to posting. Current logic will not work with bundles.

        :param self:
        :returns: resource id type string
        """
        regex = re.compile(r'[a-z]\/(\d+)\/',re.IGNORECASE)
        id = regex.search(self.response['issue'][0]['diagnostics']).group(1)
        return id

    @staticmethod
    def _create_FHIRCoding(code, system=None, display=None):
        """
        Creates and returns a FHIRCoding object.

        :param code: code from standard System
        :param system: coding System
        :param display: how the resource should be displayed
        :returns: Coding FHIR object
        """
        Coding = c.Coding()
        Coding.code = code
        Coding.system = system
        Coding.display = display
        return Coding

    def _create_FHIRCodeableConcept(self,code, system=None ,display=None):
        """
        Creates and returns a FHIRCodeableConcept object. References self._create_FHIRCoding()

        :param self:
        :param code: code from standard System
        :param system: coding System
        :param display: how the resource should be displayed
        :returns: CodeableConcept FHIR object
        """
        CodeableConcept = cc.CodeableConcept()
        Coding = self._create_FHIRCoding(code,system,display)
        CodeableConcept.coding = [Coding]
        return CodeableConcept

    @staticmethod
    def _validate(resource):
        """
        Posts a request to hardcoded server to validate a resource. Will print errors/issues.

        :param resource: FHIR resource to be validated.
        :returns: None
        """
        returned = requests.post(f'http://hapi.fhir.org/baseDstu2/{resource.resource_name}/$validate?profile=http://fhir.org/guideasdfasdfs/argonaut/StructureDefinition/argo-condition', data=json.dumps(resource.as_json()))
        """
        Other Servers:
            - https://api-v5-dstu2-test.hspconsortium.org/fpar2/open/
            - http://hapi.fhir.org/baseDstu2/
            - https://api-v5-dstu2.hspconsortium.org/fpardstu2/open/
            - http://hapi.fhir.org/baseDstu2
        """
        # print(returned.text)
        # for issue in returned.json()['issue']:
        #     print(issue['diagnostics'])

    @staticmethod
    def post_resource(resource):
        """
        DSTU2 errors with resource.create(). This function is the DSTU2 version of posting resources.

        :param resource: FHIR resource object that is to be validated
        :returns: json response
        """
        response = requests.post(f'https://api-v5-dstu2.hspconsortium.org/opafpardev/open/{resource.resource_name}',data=json.dumps(resource.as_json()))
        """
        Other Servers:
            - https://api-v5-dstu2-test.hspconsortium.org/fpar2/open/
            - http://hapi.fhir.org/baseDstu2/
            - https://api-v5-dstu2.hspconsortium.org/fpardstu2/open/
            - https://api-v5-dstu2.hspconsortium.org/opafpardev/open/
            - https://api-v5-dstu2.hspconsortium.org/FPARPatients/open/
            - https://api-v5-dstu2.hspconsortium.org/fparTEST/open/
            - https://api-v5-dstu2.hspconsortium.org/opafpardev/open/

        """
        return response.json()

    @staticmethod
    def read_json(file):
        """Reads json file and returns json object"""
        with open(file,'r') as f:
            jdata = json.load(f)
        return jdata

    @staticmethod
    def json_request(ResourceType,StructureDefinition):
        """Searches HSPC server v5 to obtain StructuredDefinitions."""
        r = requests.get(f'https://api-v5-stu3.hspconsortium.org/stu3/open/{ResourceType}?_id={StructureDefinition}&_format=json')
        return r.json()

    def hard_valueset(self):
        """Hard coded to all_lab_values.xlsx document."""
        if self.loinc==None:
            return None
        df = pd.read_excel('./fhir/all_lab_values.xlsx')
        valueset_list = df[df.loinc==self.loinc].value.tolist()
        return valueset_list

    def dict_search(self,data=None):
        """Recursive function that works in conjuction with list_search.  Hard coded for looking up LOINC codes."""
        if data == None:
            data = self.jdata
        for k,v in data.items():
            #parsing loinc
            if k=='system' and v=='http://loinc.org':
                try:
                    isinstance(data['concept'],list)
                    for loinc_dict in data['concept']:
                        self.LoincSet.append(loinc_dict['code'])
                except KeyError:
                    self.loinc = data['code']
            elif k=='min' and int(v)==1:
                try:
                    print(f"id:{data['id']}")
                    pass
                except KeyError:
                    print(f"path:{data['path']}")
                    pass
            if isinstance(v,dict):
                self.dict_search(v)
            elif isinstance(v,list):
                self.list_search(v)

    def list_search(self,data):
        """Recursive function that works in conjuction with dict_search."""
        if data == None:
            data = self.jdata
        for i,v in enumerate(data):
            if isinstance(v,dict):
                self.dict_search(v)
            elif isinstance(v,list):
                self.list_search(v)

    @staticmethod
    def _generate_person():
        """
        Generates the attributes for a person FHIR object. Used in both Patient and Practitioner.

        :returns: name_last, [name_first], gender
        """
        name_first_dict = {}
        df = pd.read_excel('../demographic_files/common_name_first.xlsx')
        name_first_dict['male'] = df.men.tolist()
        name_first_dict['female'] = df.women.tolist()

        name_last_list = []
        df = pd.read_excel('../demographic_files/common_name_last.xlsx')
        name_last_list = df.name_last.tolist()

        gender = random.choice(['male','female'])
        name_first = random.choice(name_first_dict[gender])
        name_last = random.choice(name_last_list)

        return name_last, [name_first], gender

    def _add_quantity_value(self,Observation,measurement):
        """
        Adds a quantity value object to Observation.

        :param Observation: fhirclient.models.observation.Observation object
        :param measurement: measurement dictionary
        :returns: Observation object
        """
        Quantity = q.Quantity()
        Quantity.value = self.observation_dict[measurement]['value']
        Quantity.unit = self.observation_dict[measurement]['unit']
        Observation.valueQuantity = Quantity
        return Observation

    def _add_codeable_value(self,Observation,measurement):
        """
        Adds a codeableconcept value object to Observation.

        :param Observation: fhirclient.models.observation.Observation object
        :param measurement: measurement dictionary
        :returns: Observation FHIR object
        """
        CodeableConcept = cc.CodeableConcept()
        Coding = c.Coding()
        Coding.system = 'http://loinc.org'
        Coding.code = self.observation_dict[measurement]['value_loinc']
        Coding.display = self.observation_dict[measurement]['value_display']
        CodeableConcept.coding = [Coding]
        Observation.valueCodeableConcept = CodeableConcept
        return Observation

    def _add_value(self,Observation,measurement):
        """
        Adds values to an Observation FHIR object. Uses 'type' within dictionary to determine logic.

        :param self:
        :param Observation: Observation FHIR object.
        :param measurement: Specific observation measurement. References a dictionary.
        :returns: Observation FHIR object.
        """
        if measurement['type'] == 'quantity':
            Observation.valueCodeableConcept = self._create_FHIRCodeableConcept(code=measurement['code'], system=measurement['system'], display=measurement['display'])
        elif measurement['type'] == 'codeable':
            Quantity = q.Quantity()
            Quantity.value = self.observation_dict[measurement]['value']
            Quantity.unit = self.observation_dict[measurement]['unit']
            Observation.valueQuantity = Quantity
        elif measurement['type'] == 'valuestring':
            Observation.valueString = measurement['value']
        return Observation

    @staticmethod
    def _generate_vitals():
        """
        Generates a set of vitals using a normal distribution times 10

        :returns: sbp, dbp, hr
        """
        avg_sbp = 120
        avg_dbp  = 80
        diff = int(np.random.normal(0,1)*10)
        sbp = avg_sbp + diff
        dbp = avg_dbp + diff

        avg_hr = 80
        diff = int(np.random.normal(0,1)*10)
        hr = avg_hr + diff
        return sbp, dbp, hr

    @staticmethod
    def _generate_height_weight(sex):
        """
        Generates a set of vitals using a normal distribution times 10

        :returns: sbp, dbp, hr
        """
        avg_height_male = 69.2
        std_height_male = 4
        avg_height_female = 63.7
        std_height_female = 3.5

        avg_weight_male = 195.7
        std_weight_male = 30
        avg_weight_female = 168.5
        std_weight_female = 25

        if sex =='unknown':
            sex = random.choice(['male','female'])
        if sex == 'male':
            height = np.random.normal(avg_height_male,std_height_male)
            weight = np.random.normal(avg_weight_male,std_weight_male)
        elif sex == 'female':
            height = np.random.normal(avg_height_female,std_height_female)
            weight = np.random.normal(avg_weight_female,std_weight_female)
        else:
            raise ValueError('sex error')
        return height, weight

    @staticmethod
    def _get_smoking_loinc():
        """
        Uses a get request from LOINC to obtain a list of smoking statuses and returns a random one.

        :returns: smoke_loinc, smoke_description
        """
        df = pd.read_html('http://hl7.org/fhir/us/core/stu1/ValueSet-us-core-observation-ccdasmokingstatus.html')[1]
        headers = df.iloc[0,:2].tolist()
        df = df.iloc[1:,:2]
        df.columns = headers
        smoke_description = random.choice(df.Display.tolist())
        smoke_loinc = df[df.Display==smoke_description].Code.values[0]
        return smoke_loinc, smoke_description

    def _get_household_income(self):
        """Requests values of household income and selects one at random."""
        df = pd.read_html('https://r.details.loinc.org/LOINC/77244-2.html?sections=Comprehensive')[4]
        df = df.iloc[4:,[3,5]]
        df.columns = ['income_range','answer_id']
        self.income_range = random.choice(df.income_range.tolist())
        self.income_loinc = df[df.income_range == self.income_range].answer_id.values[0]

    def _get_pregnancy_status(self):
        """Currently hardcoded to give Not Pregnant"""
        df = pd.read_html('https://s.details.loinc.org/LOINC/82810-3.html')[5]
        df = df.iloc[4:,[3,5]]
        df.columns = ['pregnancy_display','pregnancy_id']
        df.iloc[2,0] = 'Unknown'
        self.pregnancy_display = df[df.pregnancy_display == 'Not pregnant'].pregnancy_display.values[0]
        self.pregnancy_loinc = df[df.pregnancy_display == self.pregnancy_display].pregnancy_id.values[0]

    def _generate_gravidity_and_parity(self,patient):
        """Generates a gravidity and parity between 0 and 6"""
        if patient.gender == 'male':
            self.gravidity = 0
        else:
            self.gravidity = random.choice(range(7))
        if self.gravidity == 0:
            self.parity = 0
        else:
            self.parity = self.gravidity - random.choice(range(self.gravidity))

    @staticmethod
    def _get_fpar_random_value(item_name):
        """
        Used in generating fpar observations. Hardcoded to look at valuesets within file and picks at random.

        :param item_name: Observation name which is determined by listing in hardcoded file.
        :returns: random value from valueset
        """
        df = pd.read_excel('../demographic_files/valueset.xlsx',sheet_name='Sheet1')
        df = df.fillna('N/A')
        item_value = df[df.item == item_name].valueset.tolist()
        return random.choice(item_value)
