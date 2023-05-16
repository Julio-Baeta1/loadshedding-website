#import unittest
from django.test import TestCase
from loadshedding_calc.views import stageQuery
from django.db.models import Q

class StageQueryFunctionTest(TestCase):

    def test_returns_single_Q_object_for_stage_1(self):
        t_stage = 1
        t_area_code = 1
        t_query = stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, Q(stage1=1))

    def test_returns_nested_Q_object(self):
        t_stage = 3
        t_area_code = 1
        t_query = stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, Q(Q(stage1=1)|Q(stage2=1)|Q(stage3=1)))

    def test_does_not_return_Q_object_for_stage_0(self):
        t_stage = 0
        t_area_code = 1
        t_query = stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, None)
    
    def test_does_not_return_Q_object_for_stage_greater_8(self):
        t_stage = 20
        t_area_code = 1
        t_query = stageQuery(t_stage,t_area_code)
        self.assertEqual(t_query, None)
