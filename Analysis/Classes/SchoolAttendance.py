'''
Author: James Parkington
Date:   2023-03-31
Class:  SchoolAttendance

This script generates a randomized dataset of attendance records for students within a specific date range. The dataset can
be saved as a CSV file or used directly as a pandas DataFrame.

Schema:
    date (timestamp):     The date of the attendance record
    student_id (varchar): A unique identifier for each student
    attendance (boolean): A flag indicating whether the student attended school on the given date (True for attended, False for absent)

Data Constraints:
    Each student_id is represented across all dates and does not show up twice for the same date.
    The final DataFrame is ordered by date (ascending) and student_id (ascending).
    The number of rows is determined by the max_student_id ⋅ time_delta, which ensures all students are accounted for across all days.
'''

from datetime   import timedelta
from .Utilities import *
import random   as rn

class SchoolAttendance:
    def __init__(self, start_date, end_date, max_student_id):
        self.start_date     = start_date
        self.end_date       = end_date
        self.max_student_id = max_student_id

        # Optimized variables for faster mutator performance
        self.attendance_weights = [True] * 4 + [False] # Ensures that True shows up 80% of the time
        self.dates              = self.calculate_dates()

    # Mutators
    def set_student_ids(self):
        return [s for s in range(1, self.max_student_id + 1)]

    def set_date_range(self):
        return rn.choice(self.dates)

    def set_random_attendance(self):
        return rn.choice(self.attendance_weights)
    
    # Accessors
    def get_student_ids(self):
        return self.set_student_ids()

    # Prescriptive Methods
    def generate_data(self):
        '''
        Generate a list of dictionaries with randomized attendance data to be output as either a CSV file or a pandas DataFrame for immediate use.
        
        Considerations:
            Using two loops in this method ensures that we create a record for each student on each date.
            A dictionary is used for each attendance record because it allows for easy conversion to a pandas DataFrame later.
        '''
        data = []
        for date in self.dates:

            for student_id in self.set_student_ids():

                attendance_record = {'date'       : date,
                                     'student_id' : student_id,
                                     'attendance' : self.set_random_attendance()}
                
                data.append(attendance_record)

        return data
    
    def calculate_dates(self):
        '''
        Pre-calculating these dates allows for faster selection.
        '''
        delta  = self.end_date - self.start_date
        dates  = [self.start_date + timedelta(days = d) for d in range(delta.days + 1)]
        return dates
    
    def __call__(self):
        '''
        Generate a pandas DataFrame of attendance records for students within a specific date range.
        '''
        df = to_dataframe(data      = self.generate_data(), 
                          by        = ['student_id', 'date'], 
                          filename  = save_path(True, 'Data', 'school_attendance.csv'),
                          sql_table = 'school_attendance')
        
        return df