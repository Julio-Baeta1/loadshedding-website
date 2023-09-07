from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.db.models import Q
#######################################################################################################################################
#Table to link Cape Town Area name to its appropriate Area code 
class CapeTownAreas(models.Model):
    ct_area_id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=80)
    area_code = models.SmallIntegerField()

    def __str__(self):
        return self.area_name + " is in area code: " + str(self.area_code)
    
#######################################################################################################################################
# Table of Day of month with all its loadshedding slots given by start_time and end_time.
# Each respective stage column contains an area code for each slot and is read as:
#               if the load-shedding stage is 4 then all area codes in the columns stage1 -> stage4 will recieve loadshedding for that slot

class CapeTownSlots(models.Model):
    slot_id = models.AutoField(primary_key=True)
    day = models.SmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    stage1 = models.SmallIntegerField()
    stage2 = models.SmallIntegerField()
    stage3 = models.SmallIntegerField()
    stage4 = models.SmallIntegerField()
    stage5 = models.SmallIntegerField()
    stage6 = models.SmallIntegerField()
    stage7 = models.SmallIntegerField()
    stage8 = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'cape_town_slots'
    
    def stageQuery(self,stage,area_code):
        """Function to create DB query for stages 1-8 of loadshedding i.e. for stage 6 load-shedding will occur if area code appears 
        as the field value for column stage6 all the way down to column stage1"""

        if stage <1 or stage > 8:
            return 

        stage_query = Q(stage1 = area_code)

        if stage > 1:
            stage_query |= Q(stage2 =area_code)
        if stage > 2:
            stage_query |= Q(stage3 =area_code)
        if stage > 3:
            stage_query |= Q(stage4 =area_code)
        if stage > 4:
            stage_query |= Q(stage5 =area_code)
        if stage > 5:
            stage_query |= Q(stage6 =area_code)
        if stage > 6:
            stage_query |= Q(stage7 =area_code)
        if stage > 7:
            stage_query |= Q(stage8 =area_code)

        if stage > 1: #Ensures that if only single query in Q object it is not encapsulated by larger Q()
            stage_query = Q(stage_query)

        return stage_query
    
    def filterbyStageTimes(self, q_day, q_area, q_stage, t1, t2):
        day_slots = self.objects.filter(Q(day=q_day) & Q(start_time__gte=t1) & Q(end_time__lte=t2) )
        stage_query = self.stageQuery(self,q_stage,q_area)
        day_slots = day_slots.filter(stage_query)
        return day_slots
    
    def __str__(self):
        return str(self.day)+" = "+self.start_time.strftime('%H:%M')+"-"+self.end_time.strftime('%H:%M')
    
    def printFullDay(self,q_day):
        day_slots = self.objects.filter(day=q_day) 
        for slot in day_slots:
            print(f"{slot.start_time}-{slot.end_time} = 1:{slot.stage1}, 2:{slot.stage2}, 3:{slot.stage3}, 4:{slot.stage4}, 5:{slot.stage5}, 6:{slot.stage6}, 7:{slot.stage7}, 8:{slot.stage8}")
    
#######################################################################################################################################
#Table of past dates and load-shedding stage which occured during relevent python3 manage.py makemigrationstime intervals

#Possible improvement would be to have start and duration instead of start and end, however this might add more complexity to determining
#user defined load-shedding stage intervals

class CapeTownPastStages(models.Model): 
    past_stage_id = models.AutoField(primary_key=True)
    date = models.DateField()
    stage = models.SmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        managed = False
        db_table = 'cape_town_past_stages'

    def filterDateTimes(self,q_date,q_start,q_end):
        #Filters by user's chosen hours for a particular date
        a = datetime.datetime.combine(q_date,q_start) 
        b = datetime.datetime.combine(q_date,q_end) 
        day_slots = self.objects.filter(Q(date=q_date) & (Q(start_time__range=(a, b)) | Q(end_time__range=(a, b))) )
        return day_slots
    

    def __str__(self):
        return str(self.date.strftime('%d-%m-%Y'))+" ["+self.start_time.strftime('%H:%M')+"-"+self.end_time.strftime('%H:%M')+"] = stage " + str(self.stage)    

#######################################################################################################################################
#User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_area = models.ForeignKey(CapeTownAreas, default=0, on_delete=models.PROTECT)
    user_hour_cost = models.DecimalField(null=True, max_digits=12, decimal_places=2)
    user_time_start = models.TimeField(default=datetime.time(00, 00))
    user_time_end = models.TimeField(default=datetime.time(23, 59))

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def getUserArea(self):
        return self.user_area.ct_area_id

    def __str__(self):
        return self.user.username + " is in area code " + str(self.user_area.area_code) + " and has an hourly cost of R" + str(self.user_hour_cost) + " from " + self.user_time_start.strftime('%H:%M')+" to "+self.user_time_end.strftime('%H:%M')
