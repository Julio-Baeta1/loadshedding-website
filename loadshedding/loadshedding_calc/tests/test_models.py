#import unittest
from django.test import TestCase
from loadshedding_calc.models import CapeTownSlots, CapeTownPastStages, CapeTownPastSlots
from django.db.models import Q
from datetime import datetime, time
from django.db import connection
from django.core import serializers
import json

###################################################################################################################################
###################################################################################################################################
# Model: CapeTownSlots 

class CapeTownSlotsStageQueryTest(TestCase):

    def testReturnsSingleQObjectForStage1(self):
        t_stage = 1
        t_area_code = 1
        ct_slots = CapeTownSlots.objects.all()
        t_query = CapeTownSlots.stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, Q(stage1=1))

    def testReturnsNestedQObject(self):
        t_stage = 3
        t_area_code = 1
        t_query = CapeTownSlots.stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, Q(Q(stage1=1)|Q(stage2=1)|Q(stage3=1)))

    def testDoesNotReturnQObjectForStage0(self):
        t_stage = 0
        t_area_code = 1
        t_query = CapeTownSlots.stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, None)
    
    def testDoesNotReturnQObjectForStageGreater8(self):
        t_stage = 20
        t_area_code = 1
        t_query = CapeTownSlots.stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, None)

###################################################################################################################################
# Model: CapeTownSlots 

class CapeTownSlotsCleanDatesTest(TestCase):

    def testFullDay(self):
        t1 = time(0,0)
        t2 = time(23,59)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        self.assertEqual(test_1, t1)
        self.assertEqual(test_2, t2)

    def testMinutesInFirstTime(self):
        t1 = time(2,11)
        t2 = time(14,00)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e1 = time(2,0)
        self.assertEqual(test_1, e1)

    def testOddFirstTime(self):
        t1 = time(17,00)
        t2 = time(20,00)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e1 = time(16,0)
        self.assertEqual(test_1, e1)

    def testMinutesInSecondTimeAndOddHour(self):
        t1 = time(8,0)
        t2 = time(11,15)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e2 = time(12,0)
        self.assertEqual(test_2, e2)

    def testMinutesInSecondTimeAndEvenHour(self):
        t1 = time(8,0)
        t2 = time(12,45)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e2 = time(14,0)
        self.assertEqual(test_2, e2)

    def testSecondTime2300(self):
        t1 = time(8,0)
        t2 = time(23,00)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e2 = time(23,59)
        self.assertEqual(test_2, e2)

    def testSecondTime22AndMinutes(self):
        t1 = time(8,0)
        t2 = time(22,15)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e2 = time(23,59)
        self.assertEqual(test_2, e2)

    def testSecondTime2200(self):
        t1 = time(8,0)
        t2 = time(22,00)
        test_1, test_2 = CapeTownSlots.cleanDates(t1,t2)
        e2 = time(22,00)
        self.assertEqual(test_2, e2)

###################################################################################################################################
# Model: CapeTownSlots 

class CapeTownSlotsFilterByStageTimesTest(TestCase):

    def setUp(self):
        super().setUp()
        with connection.schema_editor() as schema_editor:
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
        t_day = 8
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
            schema_editor.delete_model(CapeTownSlots)

    def testBaseCaseStage6Area1(self):
        t_area = 1
        t_stage = 6
        t_start = time(0,0)
        t_end = time(23,59)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        exp_set = CapeTownSlots.objects.filter(Q(slot_id=8) | Q(slot_id=4) | Q(slot_id=12) | Q(slot_id=7))
        self.assertEqual(list(t_set), list(exp_set))

    def testSlotTimeFilterStage6Area1Times6To16(self):
        #Test time interval filtering works by comparing to base case
        t_area = 1
        t_stage = 6
        t_start = time(6,0)
        t_end = time(16,0)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        base_set = CapeTownSlots.objects.filter(Q(slot_id=4)  | Q(slot_id=7) | Q(slot_id=8) | Q(slot_id=12))
        exp_set = CapeTownSlots.objects.filter(Q(slot_id=4)  | Q(slot_id=7) | Q(slot_id=8))
        self.assertNotEqual(list(t_set),list(base_set))
        self.assertEqual(list(t_set), list(exp_set))

    def testStageFilterStage2Area1(self):
        #Test stage filtering works by comparing to base case
        t_area = 1
        t_stage = 2
        t_start = time(0,0)
        t_end = time(23,59)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        base_set = CapeTownSlots.objects.filter(Q(slot_id=4)  | Q(slot_id=7) | Q(slot_id=8) | Q(slot_id=12))
        exp_set = CapeTownSlots.objects.filter(slot_id=8)
        self.assertNotEqual(list(t_set),list(base_set))
        self.assertEqual(list(t_set), list(exp_set))

    def testAreaFilterStage6Area5(self):
        #Test Area code filtering works by comparing to base case
        t_area = 5
        t_stage = 6
        t_start = time(0,0)
        t_end = time(23,59)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        base_set = CapeTownSlots.objects.filter(Q(slot_id=4)  | Q(slot_id=7) | Q(slot_id=8) | Q(slot_id=12))
        exp_set = CapeTownSlots.objects.filter(Q(slot_id=3)  | Q(slot_id=4) | Q(slot_id=8) | Q(slot_id=8) | Q(slot_id=11) | Q(slot_id=12))
        self.assertNotEqual(list(t_set),list(base_set))
        self.assertEqual(list(t_set), list(exp_set))

    def testNonBoundarySlotTimeIntervalStartContains(self):
        t_area = 1
        t_stage = 6
        t_start = time(14,30)
        t_end = time(23,59)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        exp_set = CapeTownSlots.objects.filter(Q(slot_id=8) | Q(slot_id=12))
        self.assertEqual(list(t_set), list(exp_set))

    def testNonBoundarySlotTimeIntervalEndContains(self):
        t_area = 1
        t_stage = 6
        t_start = time(8,00)
        t_end = time(15,00)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        exp_set = CapeTownSlots.objects.filter(Q(slot_id=7) | Q(slot_id=8))
        self.assertEqual(list(t_set), list(exp_set))

    def testNonBoundaryContainedInOneSlotTimeInterval(self):
        t_area = 1
        t_stage = 6
        t_start = time(14,15)
        t_end = time(15,0)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        exp_set = CapeTownSlots.objects.filter(slot_id=8)
        self.assertEqual(list(t_set), list(exp_set))

    def testBoundaryContainedInOneSlotTimeInterval(self):
        t_area = 1
        t_stage = 6
        t_start = time(14,0)
        t_end = time(16,0)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        exp_set = CapeTownSlots.objects.filter(slot_id=8)
        self.assertEqual(list(t_set), list(exp_set))

    def testNoValidSlots(self):
        t_area = 1
        t_stage = 1
        t_start = time(0,0)
        t_end = time(23,59)
        t_set = CapeTownSlots.filterbyStageTimes(CapeTownSlots, 8, t_area, t_stage, t_start, t_end)
        exp_set = CapeTownSlots.objects.none()
        self.assertEqual(list(t_set), list(exp_set))

###################################################################################################################################
###################################################################################################################################
#model: CapeTownPastStages

class CapeTownPastStagesFilterDateTimesTest(TestCase):

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
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=6,start_time=time(0,0),end_time=time(5,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=5,start_time=time(5,0),end_time=time(16,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=4,start_time=time(16,0),end_time=time(20,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=6,start_time=time(20,0),end_time=time(23,59))
            

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CapeTownPastStages)

    def testFullDay(self):
        t_date = datetime(2023,1,1)
        t_start = time(0,0)
        t_end = time(23,59)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.all()
        self.assertEqual(list(t_set), list(exp_set))

###################################################################################################################################
#One slot tests
    def testOneSlotExactlySameAsInterval(self):
        t_date = datetime(2023,1,1)
        t_start = time(16,0)
        t_end = time(20,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(past_stage_id=3)

        self.assertEqual(list(t_set), list(exp_set))

    def testInsideOneSlot(self):
        t_date = datetime(2023,1,1)
        t_start = time(9,0)
        t_end = time(13,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(past_stage_id=2)

        self.assertEqual(list(t_set), list(exp_set))

    def testOneSlotStartAndMiddle(self):
        t_date = datetime(2023,1,1)
        t_start = time(5,0)
        t_end = time(13,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(past_stage_id=2)

        self.assertEqual(list(t_set), list(exp_set))

    def testOneSlotMiddleAndEnd(self):
        t_date = datetime(2023,1,1)
        t_start = time(11,0)
        t_end = time(16,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(past_stage_id=2)

        self.assertEqual(list(t_set), list(exp_set))

###################################################################################################################################
#Multiple slots
    def testMultipleSlotsExactlySameAsIntervals(self):
        t_date = datetime(2023,1,1)
        t_start = time(5,0)
        t_end = time(20,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(Q(past_stage_id=2) | Q(past_stage_id=3))
        self.assertEqual(list(t_set), list(exp_set))

    def testInsideMultipleSlotsNoBoundarySharedWithIntervals(self):
        t_date = datetime(2023,1,1)
        t_start = time(5,30)
        t_end = time(16,7)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(Q(past_stage_id=2) | Q(past_stage_id=3))
        self.assertEqual(list(t_set), list(exp_set))

    def testMultipleSlotsStartAndMiddle(self):
        t_date = datetime(2023,1,1)
        t_start = time(5,0)
        t_end = time(17,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(Q(past_stage_id=2) | Q(past_stage_id=3))
        self.assertEqual(list(t_set), list(exp_set))

    def testMultipleSlotsMiddleAndEnd(self):
        t_date = datetime(2023,1,1)
        t_start = time(11,0)
        t_end = time(20,0)
        t_set = CapeTownPastStages.filterDateTimes(CapeTownPastStages,t_date,t_start,t_end)
        exp_set = CapeTownPastStages.objects.filter(Q(past_stage_id=2) | Q(past_stage_id=3))
        self.assertEqual(list(t_set), list(exp_set))

###################################################################################################################################
###################################################################################################################################

##Fix once serialiser added
class CapeTownPastSlotsPopulateTest(TestCase):

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
            
        CapeTownPastStages.objects.create(date=datetime(2023,1,1),stage=1,start_time=time(0,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=4,start_time=time(0,0),end_time=time(8,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=2,start_time=time(8,0),end_time=time(16,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,2),stage=4,start_time=time(16,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,3),stage=3,start_time=time(0,0),end_time=time(13,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,3),stage=5,start_time=time(13,0),end_time=time(23,59))
        CapeTownPastStages.objects.create(date=datetime(2023,1,4),stage=5,start_time=time(0,0),end_time=time(13,0))
        CapeTownPastStages.objects.create(date=datetime(2023,1,4),stage=3,start_time=time(13,0),end_time=time(23,59))

        for t_day in range(1,5):
            t1 = 0
            t2 = 2  
            t_stages = [1,9,13,5,2,10,14,6]

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

    def testCapeTownPastSlotsPopulateOne(self):
        CapeTownPastSlots.populateSlotsForDateArea(CapeTownPastSlots,datetime(2023,1,1),1)

        raw_data = serializers.serialize('python', CapeTownPastSlots.objects.filter(date=datetime(2023,1,1)))
        qs = [d['fields'] for d in raw_data]

        expected = [{"date": datetime(2023, 1, 1).date(),"area_code": 1, "start_time":time(0, 0), "end_time":time(2, 0)}] 

        self.assertEqual(qs,expected)

    def testCapeTownPastSlotsPopulateMultiple(self):
        CapeTownPastSlots.populateSlotsForDateArea(CapeTownPastSlots,datetime(2023,1,2),13)

        raw_data = serializers.serialize('python', CapeTownPastSlots.objects.filter(date=datetime(2023,1,2)))
        qs = [d['fields'] for d in raw_data]

        expected = [{"date": datetime(2023, 1, 2).date(),"area_code": 13, "start_time":time(0, 0), "end_time":time(2, 0)},
                    {"date": datetime(2023, 1, 2).date(),"area_code": 13, "start_time":time(8, 0), "end_time":time(10, 0)},
                    {"date": datetime(2023, 1, 2).date(),"area_code": 13, "start_time":time(16, 0), "end_time":time(18, 0)}] 
        self.assertEqual(qs,expected)

    def testCapeTownPastSlotsPopulateStageFromLowerToHigherChangeMidInterval(self):
        CapeTownPastSlots.populateSlotsForDateArea(CapeTownPastSlots,datetime(2023,1,3),8)

        raw_data = serializers.serialize('python', CapeTownPastSlots.objects.filter(date=datetime(2023,1,3)))
        qs = [d['fields'] for d in raw_data]
        #print(qs)

        expected = [{"date": datetime(2023, 1, 3).date(),"area_code": 8, "start_time":time(13, 0), "end_time":time(14, 0)},
                    {"date": datetime(2023, 1, 3).date(),"area_code": 8, "start_time":time(14, 0), "end_time":time(16, 0)},
                    {"date": datetime(2023, 1, 3).date(),"area_code": 8, "start_time":time(22, 0), "end_time":time(23, 59)}] 
        self.assertEqual(qs,expected)
        #self.assertEqual(1+1,2)

    def testCapeTownPastSlotsPopulateStageFromHigherToLowerChangeMidInterval(self):
        CapeTownPastSlots.populateSlotsForDateArea(CapeTownPastSlots,datetime(2023,1,4),11)

        raw_data = serializers.serialize('python', CapeTownPastSlots.objects.filter(date=datetime(2023,1,4),area_code=11))
        qs = [d['fields'] for d in raw_data]
        #print(qs)

        expected = [{"date": datetime(2023, 1, 4).date(),"area_code": 11, "start_time":time(4, 0), "end_time":time(6, 0)},
                    {"date": datetime(2023, 1, 4).date(),"area_code": 11, "start_time":time(12, 0), "end_time":time(13, 0)},
                    {"date": datetime(2023, 1, 4).date(),"area_code": 11, "start_time":time(20, 0), "end_time":time(22, 0)}] 
        self.assertEqual(qs,expected)
        #self.assertEqual(1+1,2)

    #def testCapeTownPastSlotsPopulateStageFromHigherToLowerChangeMidIntervalNotChange(self):
    #    CapeTownPastSlots.populateSlotsForDateArea(CapeTownPastSlots,datetime(2023,1,4),7)

    #    raw_data = serializers.serialize('python', CapeTownPastSlots.objects.filter(date=datetime(2023,1,4),area_code=7))
    #    qs = [d['fields'] for d in raw_data]
    #    print(qs)

    #    expected = [{"date": datetime(2023, 1, 4).date(),"area_code": 7, "start_time":time(4, 0), "end_time":time(6, 0)},
    #                {"date": datetime(2023, 1, 4).date(),"area_code": 7, "start_time":time(10, 0), "end_time":time(12, 0)},
    #                {"date": datetime(2023, 1, 4).date(),"area_code": 7, "start_time":time(12, 0), "end_time":time(14, 0)},
    #                {"date": datetime(2023, 1, 4).date(),"area_code": 7, "start_time":time(20, 0), "end_time":time(22, 0)}] 
        #self.assertEqual(qs,expected)
    #    self.assertEqual(1+1,2)



    