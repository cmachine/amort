import unittest, amort, datetime

# unit tests for amort.py
class TestAmort(unittest.TestCase):

    def test_pmt_per_int(self):
        self.assertEqual(amort.pmt_per_int(5000,0.0125,36), 173.33)

    def test_is_int(self):
        self.assertEqual(amort.is_int("7"), 7)

    def test_is_float(self):
        self.assertEqual(amort.is_float("7.77"), 7.77)

    def test_is_date(self):
        str_date = "06/17/2017"
        date = datetime.date(year=2017, month=06, day=17)
        self.assertEqual(amort.is_date(str_date), date)

    def test_validate_types(self):
        validations = {"int_field": "int", "float_field": "float", "date_field": "date"}

        int = "5"
        float = "5.55"
        date = "05/05/2015"

        form = {"int_field": int, "float_field": float, "date_field": date}
        validated = amort.validate_types(form, validations)

        self.assertTrue('errors' not in validated)

    def test_compound(self):
        self.assertEqual(amort.compound(5000, 0.05), (5250, 250))

    def test_make_payment(self):
        installment, principal, unpaid_int = amort.make_payment(5062.5, 62.5, 173.33, 4.33333333333)

        self.assertTrue(principal == 5022.5 and unpaid_int == 22.5)

if __name__ == '__main__':
    unittest.main()