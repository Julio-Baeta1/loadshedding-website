from django.test import TestCase

from loadshedding_calc.forms import DaySlotsForm

class DaySlotsFormTest(TestCase):
    """Test Default Form is valid """
    def test_default_day_slot_form_is_valid(self):
        form = DaySlotsForm(data={'selected_day': 1, 'selected_area' : 1, 'selected_stage' : 1})
        self.assertTrue(form.is_valid())


    """Tests for Day Field on form"""
    def test_day_slot_form_day_field_label(self):
        form = DaySlotsForm()
        self.assertTrue(form.fields['selected_day'].label is None or form.fields['selected_day'].label == 'selected day')

    def test_day_slot_form_day_field_help_text(self):
        form = DaySlotsForm()
        self.assertEqual(form.fields['selected_day'].help_text, 'Enter the day of the month')

    def test_day_slot_form_day_under_range(self):
        form = DaySlotsForm(data={'selected_day': 0, 'selected_area' : 1, 'selected_stage' : 1})
        self.assertFalse(form.is_valid())

    def test_day_slot_form_day_over_range(self):
        form = DaySlotsForm(data={'selected_day': 32, 'selected_area' : 1, 'selected_stage' : 1})
        self.assertFalse(form.is_valid())


    """Tests for Area Code Field on form"""
    def test_day_slot_form_area_field_label(self):
        form = DaySlotsForm()
        self.assertTrue(form.fields['selected_area'].label is None or form.fields['selected_area'].label == 'selected area')

    def test_day_slot_form_day_field_help_text(self):
        form = DaySlotsForm()
        self.assertEqual(form.fields['selected_area'].help_text, 'Enter your area code')

    def test_day_slot_form_area_under_range(self):
        form = DaySlotsForm(data={'selected_day': 1, 'selected_area' : 0, 'selected_stage' : 1})
        self.assertFalse(form.is_valid())

    def test_day_slot_form_day_over_range(self):
        form = DaySlotsForm(data={'selected_day': 1, 'selected_area' : 17, 'selected_stage' : 1})
        self.assertFalse(form.is_valid())

    
    """Tests for Day Field on form"""
    def test_day_slot_form_stage_field_label(self):
        form = DaySlotsForm()
        self.assertTrue(form.fields['selected_stage'].label is None or form.fields['selected_stage'].label == 'selected stage')

    def test_day_slot_form_stage_field_help_text(self):
        form = DaySlotsForm()
        self.assertEqual(form.fields['selected_stage'].help_text, 'Enter the loadshedding stage')

    def test_day_slot_form_stage_under_range(self):
        form = DaySlotsForm(data={'selected_day': 1, 'selected_area' : 1, 'selected_stage' : 0})
        self.assertFalse(form.is_valid())

    def test_day_slot_form_stage_over_range(self):
        form = DaySlotsForm(data={'selected_day': 1, 'selected_area' : 1, 'selected_stage' : 9})
        self.assertFalse(form.is_valid())

