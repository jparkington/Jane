'''
Author: James Parkington
Date:   2023-03-31
Class:  Students

This script generates a randomized dataset of student profiles. The dataset can
be saved as a CSV file or used directly as a pandas DataFrame.

Schema:
    student_id (varchar):      A unique identifier for each student
    school_id (varchar):       A unique identifier for each school
    grade_level (integer):     The grade level of the student
    gpa (integer):             The student's GPA
    date_of_birth (timestamp): The student's date of birth
    school_district (string):  The school district the student belongs to

Data Constraints:
    The cardinality is determined by student_id.
    The year in each date_of_birth should reasonably correspond to the grade_level each student is in.
    School_district and school_id have a fixed association, as do grade_level and the birth_year in date_of_birth.
'''

from datetime   import date
from .Utilities import *
import random   as rn
import numpy    as np

class Students:
    def __init__(self, school_attendance):
        self.school_attendance = school_attendance

    # Mutators
    def set_student_ids(self):
        '''
        Access the list of student_ids from the SchoolAttendance object.
        
        Considerations:
            Using .get_student_ids() allows for seamless integration with the SchoolAttendance class without duplicating code.
        '''
        return self.school_attendance.get_student_ids()

    def set_school_id_and_district(self):
        '''
        Create a school_id and corresponding school_district for a student.
        
        Considerations:
            school_district_mapping ensures a fixed association between school_id and school_district.
        '''
        school_id = f'SC{rn.randint(1, 6)}'
        school_district_mapping = {
            'SC1' : 'District 1',
            'SC2' : 'District 1',
            'SC3' : 'District 2',
            'SC4' : 'District 2',
            'SC5' : 'District 3',
            'SC6' : 'District 3',
        }
        school_district = school_district_mapping[school_id]
        return school_id, school_district

    def set_grade_level(self):
        return rn.randint(1, 12)

    def set_gpa(self):
        '''
        Approximates realistic GPA values for all students in the dataset.

        Considerations:
            Uses a normal distribution to make values most likely to occur in the 3 to 3.2 range.
        '''
        gpa = round(np.clip(rn.normalvariate(3, 0.2), 1, 4), 2)

        return gpa

    def set_date_of_birth(self, grade_level):
        # Adjust the year based on grade level
        birth_year  = date.today().year - (grade_level + 5)
        birth_month = rn.choice([3] * 12 + [i for i in range(1, 13)] * 5)
        birth_day   = rn.randint(1, 28 if birth_month == 2 else 30 \
                                       if birth_month in {4, 6, 9, 11} else 31)

        return date(birth_year, birth_month, birth_day)

    # Prescriptive Methods
    def generate_data(self):
        '''
        Generate a list of dictionaries with randomized student data to be output as either a CSV file or a pandas DataFrame for immediate use.
        
        Considerations:
            A dictionary is used for each student record because it allows for easy conversion to a pandas DataFrame later.
            The arguments grade_level, school_id, and school_district are defined before student_record to maintain a logical flow of data generation.
        '''
        data = []
        for student_id in self.set_student_ids():

            grade_level         = self.set_grade_level()
            school_id, district = self.set_school_id_and_district()
            student_record      = {'student_id'      : student_id,
                                   'school_id'       : school_id,
                                   'grade_level'     : grade_level,
                                   'gpa'             : self.set_gpa(),
                                   'date_of_birth'   : self.set_date_of_birth(grade_level),
                                   'school_district' : district}
            
            data.append(student_record)

        return data
    
    def __call__(self):
        '''
        Generate a pandas DataFrame of randomized student profiles.

        Considerations:
            The id field is not requires, since the table's cardinality is already fully determined by student_id
        '''
        df = to_dataframe(data      = self.generate_data(), 
                          by        = ['student_id'],
                          add_id    = False,
                          filename  = save_path(True, 'Data', 'students.csv'),
                          sql_table = 'students')
        
        return df