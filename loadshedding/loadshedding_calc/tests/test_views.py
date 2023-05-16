import datetime

from django.test import TestCase
from django.urls import reverse

from loadshedding_calc.models import CapeTownSlots

# Must research session and unmanaged table testing 
"""
class DaySlotViewTest(TestCase):

    def test_day_slots_view_url_location(self):
        response = self.client.get('/loadshedding_calc/day/')
        self.assertEqual(response.status_code, 200)

    def test_day_slots_view_url_accessible_by_name(self):
        response = self.client.get(reverse('day-slots'))
        self.assertEqual(response.status_code, 200)

    def test_day_slots_view_uses_correct_template(self):
        response = self.client.get(reverse('day-slots'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loadshedding_calc/day.html')

    def test_day_slots_view_session(self):
        # Issue a GET request.
        self.client.get('/loadshedding_calc/day/')
        session = self.client.session
        session['c_day'] = 1
        session['c_area'] = 1
        session['c_stage'] = 1
        response = self.client.get(reverse('day-slots'))
        self.assertEqual(response.status_code, 200)
"""


##################################################################################################

