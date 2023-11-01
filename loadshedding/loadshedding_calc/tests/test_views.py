from django.test import TestCase
from django.urls import reverse
from django.db import connection

from datetime import datetime, time

from loadshedding_calc.models import CapeTownPastStages, CapeTownSlots, User, CapeTownAreas

class HomePageViewTest(TestCase):

    def testHomeViewUrlByPath(self):
        response = self.client.get('/', {}, True)
        self.assertEqual(response.status_code, 200)

    def testHomeViewUrlByName(self):
        response = self.client.get(reverse('home'), {}, True)
        self.assertEqual(response.status_code, 200)

    def testHomeViewUsesCorrectTemplate(self):
        response = self.client.get(reverse('home'), {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'base_generic.html')

##################################################################################################

class SlotsForDaySelectionViewTest(TestCase):

    def testSlotsForDaySelectionViewUrlByPath(self):
        response = self.client.get('/loadshedding_calc/one/', {}, True)
        self.assertEqual(response.status_code, 200)

    def testSlotsForDaySelectionViewUrlByName(self):
        response = self.client.get(reverse('one-slots'), {}, True)
        self.assertEqual(response.status_code, 200)

    def testSlotsForDaySelectionViewUsesCorrectTemplate(self):
        response = self.client.get(reverse('one-slots'), {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loadshedding_calc/selection.html')
        self.assertTemplateUsed(response, 'base_generic.html')


class SlotsForDaySelectionViewFormsAndRedirectTest(TestCase):

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(username='testuser', password='12345')
        area_code = CapeTownAreas.objects.create(area_name="A",area_code=1)

        testuser_profile = self.user.profile      
        testuser_profile.user_area= area_code
        testuser_profile.user_hour_cost=100
        testuser_profile.user_time_start="08:00"
        testuser_profile.user_time_end="16:00"
        testuser_profile.save()

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
            
            schema_editor.create_model(CapeTownSlots)

            if (
                CapeTownSlots._meta.db_table
                not in connection.introspection.table_names()
            ):
                raise ValueError(
                    "Table `{table_name}` is missing in test database.".format(
                        table_name=CapeTownPastStages._meta.db_table
                    )
                )
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=6,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=5,start_time=time(0,0),end_time=time(23,59))

        t_day = 1
        t1 = 0
        t2 = 2  
        t_stages = [2,10,14,6,3,11,15,7]

        for x in range(11):
            CapeTownSlots.objects.create(day=t_day,start_time=time(t1,0),end_time=time(t2,0),stage1=t_stages[0], stage2=t_stages[1], stage3=t_stages[2], stage4=t_stages[3],stage5=t_stages[4], stage6=t_stages[5], stage7=t_stages[6], stage8=t_stages[7])
            t_stages = [x%16+1 for x in t_stages]
            t1 += 2
            t2 += 2

        CapeTownSlots.objects.create(day=t_day,start_time=time(22,0),end_time=time(23,59),stage1=t_stages[0], stage2=t_stages[1], stage3=t_stages[2], stage4=t_stages[3],stage5=t_stages[4], stage6=t_stages[5], stage7=t_stages[6], stage8=t_stages[7])
            

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CapeTownPastStages)
            schema_editor.delete_model(CapeTownSlots)

    #####Anon User
    def testSlotsForDaySelectionViewAnonUserFormCorrect(self):

        response = self.client.get(reverse('one-slots'), {}, True)
        self.assertContains(response,"selected_date")
        self.assertContains(response, "selected_area")
        self.assertEqual(response.status_code, 200)

    def testSlotsForDaySelectionViewAnonUserSubmitFormSuccessRedirects(self):

        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2023-01-01",
            "selected_area": "1",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/loadshedding_calc/one-day/?area_code=1&date=01-01-2023')

    def testSlotsForDaySelectionViewAnonUserFutureDateNoData(self):

        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2023-11-01",
            "selected_area": "1",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'selected_date', 'No load-shedding stage information avaliable for selected date')

    def testSlotsForDaySelectionViewAnonUserPastDateNoData(self):

        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2022-01-01",
            "selected_area": "1",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'selected_date', 'No load-shedding stage information avaliable for selected date')


    def testSlotsForDaySelectionViewAnonUserTooLowAreaCode(self):

        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2023-01-01",
            "selected_area": "0",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'selected_area', 'Not a valid area code')

    def testSlotsForDaySelectionViewAnonUserTooHighAreaCode(self):

        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2023-01-01",
            "selected_area": "21",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'selected_area', 'Not a valid area code')

    ####Logged in User
    def testSlotsForDaySelectionViewLoggedInUserFormCorrect(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('one-slots'), {}, True)
        self.assertContains(response,"selected_date")
        self.assertNotContains(response, "selected_area")
        self.assertEqual(response.status_code, 200)

    def testSlotsForDaySelectionViewLoggedInUserSubmitFormSuccessRedirects(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2023-01-01",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/loadshedding_calc/testuser/one-day/?date=01-01-2023')

    def testSlotsForDaySelectionViewLoggedInUserFutureDateNoData(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2023-11-01",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'selected_date', 'No load-shedding stage information avaliable for selected date')

    def testSlotsForDaySelectionViewLoggedInUserPastDateNoData(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('one-slots'), {}, True)
        data = {
            "selected_date": "2022-01-01",
        }
        response = self.client.post('/loadshedding_calc/one/',data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'selected_date', 'No load-shedding stage information avaliable for selected date')



###################################################################################################################################

class SlotsForDayViewTest(TestCase):

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
            
            schema_editor.create_model(CapeTownSlots)

            if (
                CapeTownSlots._meta.db_table
                not in connection.introspection.table_names()
            ):
                raise ValueError(
                    "Table `{table_name}` is missing in test database.".format(
                        table_name=CapeTownPastStages._meta.db_table
                    )
                )
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=6,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=5,start_time=time(0,0),end_time=time(23,59))

        t_day = 1
        t1 = 0
        t2 = 2  
        t_stages = [2,10,14,6,3,11,15,7]

        for x in range(11):
            CapeTownSlots.objects.create(day=t_day,start_time=time(t1,0),end_time=time(t2,0),stage1=t_stages[0], stage2=t_stages[1], stage3=t_stages[2], stage4=t_stages[3],stage5=t_stages[4], stage6=t_stages[5], stage7=t_stages[6], stage8=t_stages[7])
            t_stages = [x%16+1 for x in t_stages]
            t1 += 2
            t2 += 2

        CapeTownSlots.objects.create(day=t_day,start_time=time(22,0),end_time=time(23,59),stage1=t_stages[0], stage2=t_stages[1], stage3=t_stages[2], stage4=t_stages[3],stage5=t_stages[4], stage6=t_stages[5], stage7=t_stages[6], stage8=t_stages[7])
            

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CapeTownPastStages)
            schema_editor.delete_model(CapeTownSlots)


    def testSlotsForDayViewWithCorrectUrlParams(self):

        #response = self.client.get('/loadshedding_calc/one-day/?area_code=1&date=01-01-2023', {}, True)
        response = self.client.get('/loadshedding_calc/one-day/', {"area_code": 1, "date": "01-01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/day.html')
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithNoUrlAreaCodeParam(self):

        response = self.client.get('/loadshedding_calc/one-day/', {"date": "01-01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithNoUrlDateParam(self):

        response = self.client.get('/loadshedding_calc/one-day/', {"area_code": 1}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithNoUrlParams(self):

        response = self.client.get('/loadshedding_calc/one-day/', {}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithIncorrectFormatUrlAreaCodeParam(self):

        response = self.client.get('/loadshedding_calc/one-day/', {"area_code": 'a', "date": "01-01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithInvalidUrlAreaCodeParam(self):

        response = self.client.get('/loadshedding_calc/one-day/', {"area_code": 0, "date": "01-01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithIncorrectFormatUrlDateParam(self):

        response = self.client.get('/loadshedding_calc/one-day/', {"area_code": 1, "date": "01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithInvalidUrlDateParam(self):

        response = self.client.get('/loadshedding_calc/one-day/', {"area_code": 1, "date": "01-13-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

###################################################################################################################################
class SlotsForLoggedInDayViewTest(TestCase):

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(username='testuser', password='12345')
        area_code = CapeTownAreas.objects.create(area_name="A",area_code=1)

        testuser_profile = self.user.profile      
        testuser_profile.user_area= area_code
        testuser_profile.user_hour_cost=100
        testuser_profile.user_time_start="08:00"
        testuser_profile.user_time_end="16:00"
        testuser_profile.save()

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
            
            schema_editor.create_model(CapeTownSlots)

            if (
                CapeTownSlots._meta.db_table
                not in connection.introspection.table_names()
            ):
                raise ValueError(
                    "Table `{table_name}` is missing in test database.".format(
                        table_name=CapeTownPastStages._meta.db_table
                    )
                )
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=6,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=5,start_time=time(0,0),end_time=time(23,59))

        t_day = 1
        t1 = 0
        t2 = 2  
        t_stages = [2,10,14,6,3,11,15,7]

        for x in range(11):
            CapeTownSlots.objects.create(day=t_day,start_time=time(t1,0),end_time=time(t2,0),stage1=t_stages[0], stage2=t_stages[1], stage3=t_stages[2], stage4=t_stages[3],stage5=t_stages[4], stage6=t_stages[5], stage7=t_stages[6], stage8=t_stages[7])
            t_stages = [x%16+1 for x in t_stages]
            t1 += 2
            t2 += 2

        CapeTownSlots.objects.create(day=t_day,start_time=time(22,0),end_time=time(23,59),stage1=t_stages[0], stage2=t_stages[1], stage3=t_stages[2], stage4=t_stages[3],stage5=t_stages[4], stage6=t_stages[5], stage7=t_stages[6], stage8=t_stages[7])
            

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CapeTownPastStages)
            schema_editor.delete_model(CapeTownSlots)


    def testSlotsForDayViewWithCorrectUrlParams(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get('/loadshedding_calc/testuser/one-day/', {"date": "01-01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/day.html')
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewNotLoggedIn(self):

        response = self.client.get('/loadshedding_calc/testuser/one-day/', {"date": "01-01-2023"}, True)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'base_generic.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithNoUrlParams(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get('/loadshedding_calc/testuser/one-day/', {}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithIncorrectFormatUrlDateParam(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get('/loadshedding_calc/testuser/one-day/', {"date": "01-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)

    def testSlotsForDayViewWithInvalidUrlDateParam(self):

        self.client.login(username='testuser', password='12345')
        response = self.client.get('/loadshedding_calc/testuser/one-day/', {"date": "01-13-2023"}, True)
        self.assertTemplateUsed(response, 'loadshedding_calc/invalid_day.html')
        self.assertEqual(response.status_code, 200)