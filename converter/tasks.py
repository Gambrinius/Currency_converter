# -*- coding: utf-8 -*-
from converter.models import Currency, FullName
from celery.task import task
import requests


"""
@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def just_print():
    print("Print from celery task")
"""


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def initialize():    # initialize/update rates, currencies to database from https://openexchangerates.org
    app_id = '12f3d77a607040939f8ff9c25207490c'
    rates = requests.get('https://openexchangerates.org/api/latest.json?app_id=%s' % app_id)
    currencies = requests.get('https://openexchangerates.org/api/currencies.json?app_id=%s' % app_id)

    dict_rates = rates.json()
    dict_currencies = currencies.json()
    rates = dict_rates['rates'].items()

    for key, value in rates:
        try:
            currency = Currency.objects.get(rate=key)
        except Currency.DoesNotExist:
            currency = None

        if currency:
            currency.value = float(value)
            currency.save()
        else:
            currency = Currency(base=dict_rates["base"], rate=key, value=float(value))
            currency.save()

    for key, value in dict_currencies.items():
        try:
            fullname = FullName.objects.get(symbols=key)
        except FullName.DoesNotExist:
            fullname = None

        if fullname is None:
            fullname = FullName(symbols=key, name=value)
            fullname.save()

    # update_time = dict_rates['timestamp']
    # context[]
    print("Update currencies is successful")
