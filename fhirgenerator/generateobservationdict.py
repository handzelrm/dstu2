import generatebase
import generatepatient
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))


class GenerateObservationDict(generatebase.GenerateBase):

    def __init__(self, Patient=None):

        if Patient == None:
            self.Patient = generatepatient.GeneratePatient().Patient
        else:
            self.Patient = Patient

        self.smoke_loinc, self.smoke_description = self._get_smoking_loinc()
        self._generate_gravidity_and_parity(self.Patient)
        self.sbp, self.dbp, self.hr = self._generate_vitals()
        self.height, self.weight = self._generate_height_weight(self.Patient.gender)
        self._get_household_income()
        self._get_pregnancy_status()
        self.insurance = self._get_fpar_random_value('Insurance Coverage Type')
        self.payer = self._get_fpar_random_value('Payer for Visit')
        self.preg_reporting_method = self._get_fpar_random_value('Pregnancy Status Reporting Method')
        self.preg_intent = self._get_fpar_random_value('Pregnancy Intention')
        self.ever_had_sex = self._get_fpar_random_value('Ever Had Sex')
        self.sex_3_mo = self._get_fpar_random_value('Sex Last 3 Months')
        self.sex_12_mo = self._get_fpar_random_value('Sex Last 12 Months')
        self.contraceptive_intake = self._get_fpar_random_value('Contraceptive Method at Intake')
        self.contraceptive_exit = self._get_fpar_random_value('Contraceptive Method at Exit')

        self.observation_dict = {
            'sbp': {'system':'http://loinc.org','type':'quantity','code':'8480-6','display':'Systolic Blood Pressure (mmHg)','unit':'mmHg','value':self.sbp},
            'dbp': {'system':'http://loinc.org','type':'quantity','code':'8462-4','display':'Diastolic Blood Pressure (mmHg)','unit':'mmHg','value':self.dbp},
            'hr': {'system':'http://loinc.org','type':'quantity','code':'8867-4','display':'Heart Rate (bpm)','unit':'bpm','value':self.hr},
            'height': {'system':'http://loinc.org','type':'quantity','code':'8302-2','display':'Height (inches)','unit':'inches','value':self.height},
            'weight': {'system':'http://loinc.org','type':'quantity','code':'29463-7','display':'Weight (pounds)','unit':'pounds','value':self.weight},
            'smoke': {'system':'http://snomed.info/sct','type':'quantity','code':self.smoke_loinc,'display':self.smoke_description,'unit':None,'value':None}
            }

if __name__ == '__main__':
    GenerateObservationDict()
