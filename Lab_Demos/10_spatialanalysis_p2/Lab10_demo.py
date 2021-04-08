#!/usr/bin/env python3

"""This is a test "module" in python, which demonstrates how to import external
functions into your current python environment.

author: andrewdnolan
date  : 04/07/2021
"""

import datetime

def print_helloworld():
    print('Hello World!')

def print_date():
    currentDT = datetime.datetime.now()
    print('The date is: {}'.format(currentDT.strftime("%Y-%m-%d")))

def print_time():
    currentDT = datetime.datetime.now()
    print('The time is: {}'.format(currentDT.strftime("%I:%M:%S %p")))


def print_date_and_time():
    print_date()
    print_time()

    # This is commented out intentionally to demonstrate how to incorporate changes
    # within this file in the "workspace" that the file is loaded into.
    # currentDT = datetime.datetime.now()
    # print('The date and time is: {}'.format(currentDT.strftime("%Y-%m-%d %I:%M:%S %p")))
