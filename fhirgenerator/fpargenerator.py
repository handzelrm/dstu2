import generatepatient
import generatelocation
import generatecondition
import generatepractitioner
import generateobservation
import generateobservationdict
import generatefparlabs
import generateorganization
import argparse

class FparGenerator:

    def __init__(self):
        """Used to create all of the FPAR resources available with US Core."""
        self.Organization = generateorganization.GenerateOrganization().Organization
        self.Patient = generatepatient.GeneratePatient(Organization=self.Organization).Patient
        self.Practitioner = generatepractitioner.GeneratePractitioner(Organization=self.Organization).Practitioner
        self.Condition = generatecondition.GenerateCondition(Patient=self.Patient).Condition
        vitals_dict = generateobservationdict.GenerateObservationDict(Patient=self.Patient)
        generateobservation.GenerateObservation(observation_dict=vitals_dict.observation_dict, Patient=self.Patient, Practitioner=self.Practitioner)
        labs_dict = generatefparlabs.GenerateFparLabs()
        generateobservation.GenerateObservation(observation_dict=labs_dict.lab_dict, Patient=self.Patient, Practitioner=self.Practitioner)

def main():
    """argsparse function that addes the ability to create -n sets of fpar resources"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-n','--number', help='Number of fpar patients to create.', type=int, default=1)
    args = parser.parse_args()
    for i in range(int(args.number)):
        FparGenerator()


if __name__ == '__main__':
    main()
