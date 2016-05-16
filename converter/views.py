from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from converter.models import Currency, FullName, LastUpdateTable
from django.core.cache import cache

import datetime
import requests
# from datetime import datetime

# Create your views here.
# PosgreSQL "psql -U gambrinius currencydb" in virtualenv in project directory


def make_key(key, key_prefix):
    return ':'.join([str(key_prefix), str(key)])


# def initialize(request):
#     context = dict()
#     if request.method == 'GET':
#         context['update_time'] = LastUpdateTable.objects.get(table_name=Currency._meta.db_table).datatime
#     return render(request, 'main.html', context)


def convert(request):
    errors = []
    context = dict()
    context['currencies'] = FullName.objects.all().order_by('symbols')
    context['update_time'] = LastUpdateTable.objects.get(table_name=Currency._meta.db_table).datatime

    if request.method == 'POST':
        context['base'] = request.POST.get('base')
        context['rate'] = request.POST.get('rate')
        context['base_value'] = request.POST.get('base_value')
        base_value = 0

        # check for errors
        try:
            base_value = float(context['base_value'])
        except ValueError:
            errors.append('You enter uncorrected amount.Try again.')
        if context['base'] == context['rate']:
            errors.append('Base rate and second rate are equal.')
        context['errors'] = errors

        if not errors:
            context['base_name'] = FullName.objects.get(symbols=context['base']).name   # full names of rates
            context['rate_name'] = FullName.objects.get(symbols=context['rate']).name
            full_key = make_key(context['rate'], context['base'])  # full_key = key_prefix:key for value in cache

            if full_key in cache:
                if context['base'] == "USD":  # rate based on USD
                    rate_value = cache.get(full_key)    # get(key)
                    context['result_value'] = round(base_value * rate_value, 4)

                else:   # cross rate
                    cross_rate = cache.get(full_key)    # get(key)
                    context['cross_rate'] = cross_rate
                    context['result_value'] = round(base_value * cross_rate, 4)
            else:
                if context['base'] == "USD":  # rate based on USD
                    rate_value = Currency.objects.get(base=context['base'], rate=context['rate']).value
                    context['result_value'] = round(base_value * rate_value, 4)
                    cache.set(full_key, rate_value, 1800)   # set(key, value, timeout)
                else:   # cross rate
                    base_rate = Currency.objects.get(base="USD", rate=context['base']).value
                    second_rate = Currency.objects.get(base="USD", rate=context['rate']).value
                    cross_rate = float(second_rate / base_rate)
                    context['cross_rate'] = cross_rate
                    context['result_value'] = round(base_value * cross_rate, 4)
                    cache.set(full_key, cross_rate, 1800)   # set(key, value, timeout)

        return render(request, 'main.html', context)

    return render(request, 'main.html', context)

# /50.50/USD/to/EUR/in/json/


def request_convert(request, amount, currency_code_1, currency_code_2, response_format):
    context = dict()
    errors = []
    converted_amount = float()

    if request.method == 'GET':
        # check for errors
        try:
            amount = float(amount)
        except ValueError:
            errors.append('Entered incorrect amount.')

        if currency_code_1 == currency_code_2:
            errors.append('Base rate and second rate are equal.'
                          'Change some rate.')

        try:
            FullName.objects.get(symbols=currency_code_1)
            FullName.objects.get(symbols=currency_code_2)
        except ObjectDoesNotExist:
            errors.append('Entered incorrect currency/currencies.'
                          'Please, try again.')
        context['errors'] = errors

        if not errors:

            full_key = make_key(currency_code_2, currency_code_1)  # full_key = key_prefix:key for value in cache

            if full_key in cache:
                if currency_code_1 == "USD":
                    rate_value = cache.get(full_key)    # get(key)
                    converted_amount = round(amount * rate_value, 4)
                else:
                    cross_rate = cache.get(full_key)    # get(key)
                    converted_amount = round(amount * cross_rate, 4)
            else:
                # convert amount
                rate_value = Currency.objects.get(base="USD", rate=currency_code_2).value

                if currency_code_1 == "USD":  # rate based on USD
                    converted_amount = round(amount * rate_value, 4)
                    cache.set(full_key, rate_value, 1800)   # set(key, value, timeout)

                else:   # cross rate
                    base_value = FullName.objects.get(base="USD", rate=currency_code_1).value
                    cross_rate = float(rate_value / base_value)
                    converted_amount = round(amount * cross_rate, 4)
                    cache.set(full_key, cross_rate, 1800)    # set(key, value, timeout)

        if response_format == "text":  # response in text format
            if errors:
                content = errors
            else:
                amount = round(amount, 2)
                content = "The amount %.2f %s converted into %.4f %s" % (amount, currency_code_1,
                                                                         converted_amount, currency_code_2)
            return HttpResponse(content=content, content_type='text/plain')

        elif response_format == "json":  # response in json format
            json_dict = dict()
            if errors:
                json_dict['error'] = errors
                json_dict['success'] = False
            else:
                json_dict['result'] = converted_amount
                json_dict['success'] = True
            return JsonResponse(json_dict)

        elif response_format == "html":  # response in html format
            if errors:
                context['errors'] = errors
            else:
                context['result_value'] = "The amount %.2f %s converted into %.4f %s" % (amount, currency_code_1,
                                                                                         converted_amount, currency_code_2)
            return render(request, 'response.html', context)

        else:  # report an error request format
            context['fail_format'] = 'You entered unsupported or incorrect response format. Please, try again.'
            return render(request, 'response.html', context)


def update(request):
    context = dict()
    errors = []

    if request.method == "GET":
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

        last_currency_update = LastUpdateTable.objects.get(table_name=Currency._meta.db_table)
        last_currency_update.datatime = datetime.datetime.now()  # change date and time of currency update
        last_currency_update.save()
        # update_time = dict_rates['timestamp']
        # context[]
        context['result_value'] = "Update currencies is successful"
        return render(request, 'response.html', context)
