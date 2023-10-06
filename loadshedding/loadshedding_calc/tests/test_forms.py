from django.test import TestCase
from django.db import connection
from django import forms

from datetime import datetime, time

from loadshedding_calc.models import CapeTownPastStages
from loadshedding_calc.forms import DaySlotsForm, DaySlotsFormLoggedIn, DatePickerInput

class DaySlotsFormTest(TestCase):

    def setUp(self):
        super().setUp()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CapeTownPastStages)

            if (
                CapeTownPastStages._meta.db_table
                not in connection.introspection.table_names()
            ):
                raise ValueError(
                    "Table `{table_name}` is missing in test database.".format(
                        table_name=CapeTownPastStages._meta.db_table
                    )
                )
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=1,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=1,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,3),stage=1,start_time=time(0,0),end_time=time(23,59))

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CapeTownPastStages)

    def testStandardDaySlotFormIsValid(self):
        form = DaySlotsForm(data={"selected_date": "2023-01-01","selected_area": "1",})
        self.assertTrue(form.is_valid())

    def testDaySlotFormDateFieldCorrectlyFormat(self):
        form_date = DaySlotsForm().fields['selected_date']
        self.assertTrue(form_date.required)
        self.assertTrue(isinstance(form_date.widget, DatePickerInput))

    def testDaySlotFormDateEarlierThanDBDates(self):
        form = DaySlotsForm(data={"selected_date": "2022-12-31","selected_area": "1",})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_date'][0], 'No load-shedding stage information avaliable for selected date')

    def testDaySlotFormDateLaterThanDBDates(self):
        form = DaySlotsForm(data={"selected_date": "2023-01-04","selected_area": "1",})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_date'][0], 'No load-shedding stage information avaliable for selected date')

    def testDaySlotFormAreaCodeFieldCorrectlyFormat(self):
        form_date = DaySlotsForm().fields['selected_area']
        self.assertTrue(form_date.required)
        self.assertEqual(form_date.label,"Enter your area code")
        self.assertTrue(isinstance(form_date.widget, forms.NumberInput))

    def testDaySlotFormAreaCodeIntBelowAcceptable(self):
        form = DaySlotsForm(data={"selected_date": "2023-01-01","selected_area": "0",})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_area'][0], 'Not a valid area code')

    def testDaySlotFormAreaCodeIntAboveAcceptable(self):
        form = DaySlotsForm(data={"selected_date": "2023-01-01","selected_area": "17",})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_area'][0], 'Not a valid area code')

    def testDaySlotFormAllInvalid(self):
        form = DaySlotsForm(data={"selected_date": "2023-02-01","selected_area": "17",})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_date'][0], 'No load-shedding stage information avaliable for selected date')
        self.assertEqual(form.errors['selected_area'][0], 'Not a valid area code')
        self.assertEqual(len(form.errors), 2)

###################################################################################################################################

class DaySlotsFormLoggedInTest(TestCase):

    def setUp(self):
        super().setUp()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CapeTownPastStages)

            if (
                CapeTownPastStages._meta.db_table
                not in connection.introspection.table_names()
            ):
                raise ValueError(
                    "Table `{table_name}` is missing in test database.".format(
                        table_name=CapeTownPastStages._meta.db_table
                    )
                )
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=1,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=1,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,3),stage=1,start_time=time(0,0),end_time=time(23,59))

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CapeTownPastStages)

    def testStandardDaySlotFormLoggedInIsValid(self):
        form = DaySlotsFormLoggedIn(data={"selected_date": "2023-01-01"})
        self.assertTrue(form.is_valid())

    def testDaySlotFormLoggedInDateFieldCorrectlyFormat(self):
        form_date = DaySlotsFormLoggedIn().fields['selected_date']
        self.assertTrue(form_date.required)
        self.assertTrue(isinstance(form_date.widget, DatePickerInput))

    def testDaySlotFormLoggedInDateEarlierThanDBDates(self):
        form = DaySlotsFormLoggedIn(data={"selected_date": "2022-12-31"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_date'][0], 'No load-shedding stage information avaliable for selected date')

    def testDaySlotFormLoggedInDateLaterThanDBDates(self):
        form = DaySlotsFormLoggedIn(data={"selected_date": "2023-01-04"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['selected_date'][0], 'No load-shedding stage information avaliable for selected date')