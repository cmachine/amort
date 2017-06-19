from __future__ import division
import flask, datetime
from flask import Flask
from flask import request
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

# calculate payment due per interest period
def pmt_per_int(principal, rate, periods):

    return round(principal * (rate / (1 - (1 + rate) ** (-periods))), 2)


# return list of dates between start and end at given interval
def interval_dates(start, end, interval):
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current = current + interval

    return dates


# return int if string can cast to int
def is_int(s):
    try:
        return int(s)
    except ValueError:
        return False


# return float if string can cast to float
def is_float(s):
    try:
        return float(s)
    except ValueError:
        return False


# return datetime if string can caste to date
def is_date(s):
    try:
        return datetime.datetime.strptime(s, "%m/%d/%Y").date()
    except ValueError:
        return False


# validate input strings in html form
def validate_types(form, validations):

    validated = {}
    errors = []

    for input_name in form:

        # check each input with a validation is proper type
        if input_name in validations:
            input_value = form[input_name]

            if validations[input_name] == "float":
                float = is_float(input_value)
                if float:
                    validated[input_name] = float
                else:
                    errors.append("{0} value is [{1}]. Must be type {2}".format(input_name, input_value, validations[input_name]))

            elif validations[input_name] == "int":
                int = is_int(input_value)
                if int:
                    validated[input_name] = int
                else:
                    errors.append("{0} value is [{1}]. Must be type {2}".format(input_name, input_value, validations[input_name]))

            elif validations[input_name] == "date":
                date = is_date(input_value)
                if date:
                    validated[input_name] = date
                else:
                    errors.append("{0} value is [{1}]. Must be type {2}".format(input_name, input_value, validations[input_name]))

    if errors:
        validated['errors'] = errors

    return validated


# parse and validate input html form
def parse_input(form):

    # required input field types
    field_types = {"apr": "float", "principal": "float", "term": "int", "start_date": "date"}

    parsed = validate_types(request.form, field_types)
    if 'errors' in parsed:
        return parsed

    # non-validated inputs
    parsed['pay_freq'] = request.form['pay_freq']
    parsed['int_freq'] = request.form['int_freq']

    return parsed


# calculate interest and add to principal
def compound(principal, rate):

    interest = round(principal * rate, 2)
    principal += interest

    return principal, interest


# determine payment amounts
def make_payment(principal, unpaid_interest, int_pay, pay_per_int):
    print "make payment {0}, {1}, {2}, {3}".format(principal, unpaid_interest, int_pay, pay_per_int)

    # adjust payment amount to be per pay period instead of interest period
    payment = round(int_pay / pay_per_int, 2)

    # if total payment to be made is less than outstanding interest, payment will be all interset with carryover
    if payment < unpaid_interest:
        unpaid_interest = round(unpaid_interest - payment, 2)
        interest_paid = payment
        principal_paid = 0
    else:
        # if principal is less than normal payment this is the last payment
        if principal < payment:
            principal_paid = principal - unpaid_interest
        else:
            principal_paid = round(payment - unpaid_interest, 2)

        interest_paid = unpaid_interest
        unpaid_interest = 0

    # deduct payment from principal
    principal = round(principal - payment, 2)
    principal = 0 if principal < 0 else principal

    # record installment to track schedule
    installment = {'total': interest_paid + principal_paid,
                   'interest_paid': interest_paid, 'principal_paid': principal_paid, 'remaining': principal,
                   'unpaid_interest': unpaid_interest}

    return installment, principal, unpaid_interest

@app.route("/")
def home():
    return flask.render_template('calc.html')


@app.route("/calculate", methods=['POST'])
def calculate():

    user_params = parse_input(request.form)
    if 'errors' in user_params:
        return flask.render_template('errors.html', errors=user_params['errors'])

    # available terms and corresponding timedelta
    terms = {"monthly": relativedelta(months=1), "semi-monthly": relativedelta(days=15), "weekly": relativedelta(weeks=1),
         "daily": relativedelta(days=1)}

    # unpack user params and calculate other values needed for amortization schedule
    principal = user_params['principal']
    apr = user_params['apr'] / 100
    years = user_params['term']
    start_date = user_params['start_date']
    pay_freq = terms[user_params['pay_freq']]
    int_freq = terms[user_params['int_freq']]
    end_date = start_date + relativedelta(years=years)
    pay_dates = interval_dates(start_date, end_date, pay_freq)
    int_dates = interval_dates(start_date, end_date, int_freq)[:-1]

    rate_per_period = apr * years / len(int_dates)

    # calculate the recurring payment amount
    int_pay = pmt_per_int(principal, rate_per_period, len(int_dates))
    print "payment: " + str(int_pay)

    installments = []
    payment_num = 1
    unpaid_interest = 0
    current_date = start_date
    pay_per_int = (len(pay_dates) - 1) / len(int_dates)

    # for each day in loan term
    while current_date < end_date and principal > 0:

        # if interest is compounded on this day
        if current_date in int_dates:
            principal, unpaid_interest = compound(principal, rate_per_period)

        # if payment is made on this day subtract payment amount from outstanding interest 1st
        if current_date in pay_dates:

            installment, principal, unpaid_interest = make_payment(principal, unpaid_interest, int_pay, pay_per_int)
            print "return {0}, {1}, {2}".format(installment, principal, unpaid_interest)
            installment['number'] = payment_num
            installment['pay_date'] = current_date
            installments.append(installment)
            payment_num += 1

        current_date = current_date + relativedelta(days=1)

    loan_start = start_date - pay_freq
    return flask.render_template('payment_schedule.html', installments=installments, pay_start=start_date, loan_start=loan_start)

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

