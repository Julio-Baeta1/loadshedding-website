#import unittest
from django.test import TestCase
from loadshedding_calc.models import CapeTownSlots, CapeTownPastStages
from django.db.models import Q
from datetime import datetime, time
from django.db import connection

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
    def testOneSlotExact(self):
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
 