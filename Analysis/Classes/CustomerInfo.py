'''
Author: James Parkington
Date:   2023-04-03
Class:  CustomerInfo

This script generates a randomized dataset of customer information. The dataset can
be saved as a CSV file or used directly as a pandas DataFrame.

Schema:
    customer_id (varchar):           A unique identifier for each customer
    customer_name (string):          The customer's name
    phone (varchar):                 The customer's phone number
    address (string):                The customer's address
    city (string):                   The city where the customer resides
    state (string):                  The state where the customer resides
    postal_code (varchar):           The postal code of the customer's location
    sales_rep_employee_id (varchar): The sales representative associated with the customer
    credit_limit (currency):         The customer's credit limit

Data Constraints:
    Postal code, city, and state all make sense geographically.
    The values for `customer_name`, `phone`, and `address` are random and fake.
    There are 10 sales representatives with IDs from 1 to 10.
    The `credit_limit` should allow customers to buy between 1 and 30 orders per month. It's also influenced by their purchase history.
'''

from faker      import Faker
from uszipcode  import SearchEngine
from .Utilities import *
import random   as rn
import numpy    as np

class CustomerInfo:
    def __init__(self, order_history):
        self.order_history = order_history
        self.fake          = Faker()
        self.search        = SearchEngine()
        self.spend_weights = self.order_history.get_spend_weights()

    # Mutators
    def set_customer_id(self):
        return self.order_history.get_customer_ids()

    def set_customer_name(self):
        return self.fake.name()

    def set_phone(self):
        return self.fake.phone_number()

    def set_address(self):
        return self.fake.street_address()

    def set_city_state_zip(self):
        '''
        Generate city, state, and postal_code that are geographically consistent. Sometimes the Faker() will supply an invalid state, so the loop
        will fall back on defaults in the event a new state can't be found after a few tries.
        '''
        excluded_states = ['AK', 'HI', 'DC', 'PR']
        for i in range(5):

            try:
                state = self.fake.state_abbr()
                if state not in excluded_states:

                    choice = rn.choice(self.search.by_state(state))
                    if choice:
                        return choice.major_city, state, choice.zipcode
                    
            except IndexError:
                pass
            
        # If no valid city, state, and zipcode can be generated after 5 tries, return defaults
        return 'Los Angeles', 'CA', '90210'

    def set_sales_rep_employee_id(self):
        return f'SRE{rn.randint(1, 10)}'

    def set_credit_limit(self, customer_id):
        return round(np.random.uniform(1000, 5000) * self.spend_weights.get(customer_id, 1), -2)

    # Prescriptive Methods
    def generate_data(self):
        '''
        Generate a list of dictionaries with randomized customer information to be output as either a CSV file or a pandas DataFrame for immediate use.
        '''
        data = []
        for customer_id in self.set_customer_id():

            city, state, postal_code = self.set_city_state_zip()
            customer_info = {'customer_id'          : customer_id,
                             'customer_name'        : self.set_customer_name(),
                             'phone'                : self.set_phone(),
                             'address'              : self.set_address(),
                             'city'                 : city,
                             'state'                : state,
                             'postal_code'          : postal_code,
                             'sales_rep_employee_id': self.set_sales_rep_employee_id(),
                             'credit_limit'         : self.set_credit_limit(customer_id)}
            
            data.append(customer_info)

        return data

    def __call__(self):
        '''
        Generate a pandas DataFrame of randomized customer information.
        '''
        df = to_dataframe(data      = self.generate_data(),
                          by        = ['customer_id'],
                          add_id    = False,
                          filename  = save_path(True, 'Data', 'customer_info.csv'),
                          sql_table = 'customer_info')

        return df