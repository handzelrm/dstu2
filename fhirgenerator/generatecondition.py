import generatebase
import generatepatient

import fhirclient.models.codeableconcept as cc
import fhirclient.models.coding as c
import fhirclient.models.condition as cond

import random
import pandas as pd
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))


class GenerateCondition(generatebase.GenerateBase):
    def __init__(self, Patient=None):
        """
        Uses fhirclient.models to create, validate, and post a Condition FHIR resource.

        :returns: GenerateCondition object which has Condition object as an attribute.
        """

        if Patient == None:
            self.Patient = generatepatient.GeneratePatient().Patient
        else:
            self.Patient = Patient

        self._generate_icd_code()

        Condition = cond.Condition()
        Condition.clinicalStatus = 'active'
        Condition.verificationStatus = 'confirmed'
        # Condition.verificationStatus = 'active'
        Condition.category = self._create_FHIRCodeableConcept(code='problem', system='urn:oid:2.16.840.1.113883.4.642.3.153', display='Problem List Item')

        Condition.code = self._create_FHIRCodeableConcept(code=self.icd_code,system='urn:oid:2.16.840.1.113883.6.3',display=self.icd_description)
        Condition.patient = self._create_FHIRReference(self.Patient)

        self._validate(Condition)
        self.response = self.post_resource(Condition)
        Condition.id = self._extract_id()
        self.Condition = Condition
        self.Condition.Patient = self.Patient
        print(self)

    def __str__(self):
        return f'{self.Condition.__class__.__name__}:{self.icd_description}; id: {self.Condition.id}'

    @staticmethod
    def __repr__():
        return 'GenerateCondition()'

    def _generate_icd_code(self):
        """Generates an icd code at random from a hardcoded file."""
        df = pd.read_excel('../demographic_files/common_obgyn_visits_parsed.xlsx',sheet_name='for OPA')
        icd_list = []
        for row in df.iterrows():
            icd_list += row[1][0]*[row[1][1]]
        self.icd_code = random.choice(icd_list)
        self.icd_description = df[df.code==self.icd_code].description.values[0]

if __name__ == '__main__':
	GenerateCondition()
