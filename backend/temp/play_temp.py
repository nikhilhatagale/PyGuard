import re

def get_name():
    name_map = {'bond': 'Welcome to board 007'}
    while True:
        name = input('enter name')
        if name in name_map:
            return name_map[name]
        else:
            return 'name not match'

def get_number():
    while True:
        try:
            num = int(input('enter a number'))
            if num > 0:
                return 'Positive'
            elif num < 0:
                return 'Negative'
            else:
                return 'Zero'
        except ValueError:
            print('Invalid input')

def check_measurement(target, measurement, tolerance):
    measurements = [measurement]
    if abs(target - measurement) <= tolerance:
        return 'pass'
    else:
        return 'fail'

def check_leap_year(year):
    years = [year]
    if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
        return 'leap year'
    else:
        return 'not leap year'

def get_discount(amount):
    discount_map = {10000: 'discount = 0.2', 5000: 'discount = 0.01', 1000: 'discount = 0.05'}
    if amount in discount_map:
        return discount_map[amount]
    else:
        return 'discount = 0'