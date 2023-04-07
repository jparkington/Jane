'''
Author: James Parkington
Date:   2023-04-03
Class:  OrderHistory

This script generates a randomized dataset of order history information. The dataset can
be saved as a CSV file or used directly as a pandas DataFrame.

Schema:
    order_id (varchar):       A unique identifier for each order
    order_date (timestamp):   The date when the order was placed
    shipped_date (timestamp): The date when the order was shipped
    status (string):          The status of the order (abandoned, canceled, or completed)
    comments (string):        Optional comments about the order
    order_amount (currency):  The total dollar amount of the user's cart
    customer_id (varchar):    The customer who placed the order
    store_id (varchar):       The store where the order was placed

Considerations:
    `shipped_date` should generally be 1 to 2 business days after order_date.
    `order_amount` is the total dollar amount of a user's cart (online basket).
    Status gives insight into whether or not the order was abandoned, canceled, or completed.
    The values in `order_amount` should emulate the average expected for an iheartjane.com purchase.
    The values for `customer_id` are predicated upon a user averaging 4 orders over a 6-month period
'''

from datetime    import date, timedelta
from collections import defaultdict
from .Utilities  import *
import random    as rn
import numpy     as np
import holidays  as hd

class OrderHistory:
    def __init__(self, revenue, aov, start_date, end_date):
        self.num_orders = revenue // aov
        self.revenue    = revenue
        self.aov        = aov
        self.start_date = start_date
        self.end_date   = end_date

        # Optimized variables for faster mutator performance
        self.peak_days     = [date(2022,  4, 20), # Obviously
                              date(2022, 11, 20), # Black Friday
                              date(2022, 11, 21),
                              date(2022, 11, 22),
                              date(2022, 11, 23), # Cyber Monday
                              date(2022, 12, 19), # Christmas Eve
                              date(2022, 12, 20), # Christmas
                              date(2022, 12, 26), # New Year's Eve
                              date(2022, 12, 27)] # New Year's Day
        self.dates         = self.calculate_dates()
        self.customer_pool = self.set_customer_pool()

    # Mutators
    def set_order_id(self):
        return f'O{rn.randint(1000000, 9999999)}'

    def set_order_date(self):
        return rn.choice(self.dates)

    def set_shipped_date(self, order_date):
        shipped_date = order_date + timedelta(days=rn.randint(1, 2))
        holidays_2022 = hd.US(years=2022)

        # Add one day to shipped_date until it is not a weekend or holiday
        shipped_date += timedelta(days = sum([1 for _ in range(3) \
                                             if shipped_date.weekday() >= 5 or shipped_date in holidays_2022]))

        return shipped_date

    def set_status(self):
        return rn.choices(['completed', 'abandoned', 'canceled'], [0.87, 0.1, 0.03])[0]

    def set_comments(self, order_date):
        return 'Holiday Promotion' if order_date in hd.US(years = 2022) else ''

    def set_order_amount(self, order_date):
        '''
        The order amount is determined by a normal distribution around the average order value (AOV),
        with a standard deviation of 15. It incorporates random spikes of 2x to 4x higher than the AOV
        for 1 in every 30 calls. 
        
        Additionally, a holiday multiplier is applied for peak holiday dates, scaling the AOV upward 
        until it reaches 3x on the holiday date and then scales back down.
    '''
        spike_multiplier = np.random.choice([1] * 29 + [np.random.uniform(2, 4)], 1)[0]
        
        peak_multiplier = 1
        for day in self.peak_days:

            days_diff = (day - order_date).days
            if -10 <= days_diff <= 0:

                peak_multiplier = 1 + 0.2 * abs(days_diff)
                break

        return round(np.random.normal(self.aov * spike_multiplier * peak_multiplier, 15), 2)

    def set_customer_id(self):
        return rn.choice(self.customer_pool)


    def set_store_id(self):
        return f'S{rn.randint(1, 500)}'
    
    # Accessors
    def get_customer_ids(self):
        return set(self.customer_pool)
    
    def get_spend_weights(self):
        '''
        Calculate weights for each customer based on their total order amounts.
        
        The weights are calculated as a ratio of each customer's total order amount compared
        to the maximum total order amount across all customers. The weights range from 1 to 3.
        
        Returns:
            dict: A dictionary with customer IDs as keys and their corresponding weights as values.
        '''
        order_totals = defaultdict(float)
        for order in self.generate_data():
            order_totals[order['customer_id']] += order['order_amount']

        max_total = max(order_totals.values())
        return {k: 1 + 2 * (v / max_total) for k, v in order_totals.items()}

    # Prescriptive Methods
    def generate_data(self):
        '''
        Generate a list of dictionaries with randomized order history data.
        '''
        data = []
        for _ in range(self.num_orders):

            order_date = self.set_order_date()
            order_record = {'order_id'     : self.set_order_id(),
                            'order_date'   : order_date,
                            'shipped_date' : self.set_shipped_date(order_date),
                            'status'       : self.set_status(),
                            'comments'     : self.set_comments(order_date),
                            'order_amount' : self.set_order_amount(order_date),
                            'customer_id'  : self.set_customer_id(),
                            'store_id'     : self.set_store_id()}
            
            data.append(order_record)

        return data
    
    def calculate_dates(self):
        '''
        Pre-calculating these dates for faster selection when generating the data.
        '''
        delta  = self.end_date - self.start_date
        dates  = [self.start_date + timedelta(days = d) for d in range(delta.days + 1)]
        dates += self.peak_days * 4
        return dates
    
    def set_customer_pool(self):
        """
        Generate a pool of customer IDs with the desired distribution:
        - 5% of users to get 20 order records
        - 35% of users to get 4 order records
        - 60% of users to get only 1 order record
        """
        percentages = [0.05, 0.35, 0.60]
        orders_list = [20, 4, 1]

        pool = [
            customer_id
            for percentage, num_orders in zip(percentages, orders_list)
            for _ in range(int(percentage * self.num_orders // 4))
            for customer_id in [rn.randint(1000000, 9999999)] * num_orders
        ]

        return pool
    
    def __call__(self):
        '''
        Generate a pandas DataFrame of randomized order history information.
        '''
        df = to_dataframe(data      = self.generate_data(),
                          by        = ['order_id'],
                          add_id    = False,
                          filename  = save_path(True, 'Data', 'order_history.csv'),
                          sql_table = 'order_history')

        return df