import datetime

from django.test import TestCase
from django.urls import reverse

from loadshedding_calc.models import CapeTownSlots

class HomePageViewTest(TestCase):

    def testHomeViewUrlByPath(self):
        response = self.client.get('/', {}, True)
        self.assertEqual(response.status_code, 200)

    def testHomeViewUrlByName(self):
        response = self.client.get(reverse('index'), {}, True)
        self.assertEqual(response.status_code, 200)

    def testHomeUsesCorrectTemplate(self):
        response = self.client.get(reverse('index'), {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTemplateUsed(response, 'base_generic.html')

##################################################################################################



