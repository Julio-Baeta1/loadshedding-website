from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.db.models import Q

###################################################################################################################################
#Function to return queryset of load-shedding slots for given date, area code and between start and end times
def oneDaySlotsBetweenTimes(date,area,start,end):
    final_obj = CapeTownSlots.objects.none()
    day_stages = CapeTownPastStages.filterDateTimes(CapeTownPastStages ,date,start,end)

    for obj in day_stages:
        if(obj.start_time < start):
            obj.start_time = start
        if(obj.end_time > end):
            obj.end_time = end

        if(obj.end_time == datetime.time(0,0)):
            obj.end_time = datetime.time(23,59)

        temp_obj = CapeTownSlots.filterbyStageTimes(CapeTownSlots, date.day,area,obj.stage,obj.start_time,obj.end_time)
        final_obj = final_obj | temp_obj

    return final_obj

#######################################################################################################################################
#Table to link Cape Town Area name to its appropriate Area code 
class CapeTownAreas(models.Model):
    ct_area_id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=80)
    area_code = models.SmallIntegerField()

    def __str__(self):
        return self.area_name + " is in area code: " + str(self.area_code)
    
#######################################################################################################################################
#Table of time slots/intervals for which load-shedding occured given the Cape Town area code and date 

class CapeTownPastSlots(models.Model):
    past_slot_id = models.AutoField(primary_key=True)
    date = models.DateField()
    area_code = models.SmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def populateSlotsForDateArea(self,date,area):
        slots = CapeTownSlots.objects.none()
        day_stages = CapeTownPastStages.filterDateTimes(CapeTownPastStages ,date,datetime.time(0,0),datetime.time(23,59))

        for obj in day_stages:
            temp_obj = CapeTownSlots.filterbyStageTimes(CapeTownSlots, date.day,area,obj.stage,obj.start_time,obj.end_time)
            slots = slots | temp_obj

        for slot in slots:
           s_time = slot.start_time
           e_time = slot.end_time

           for stage in day_stages:
               if stage.start_time > slot.start_time and stage.start_time < slot.end_time :
                   s_time = stage.start_time

               if stage.end_time > slot.start_time and stage.end_time < slot.end_time :
                   e_time = stage.end_time
            
           self.objects.create(date=date, area_code=area, start_time=s_time, end_time=e_time)

    def populateAll(self):
        min_date = self.getLatestDate(self)
        #Assume that no new dates will be earlier than latest current date
        if not min_date:
            min_date = CapeTownPastStages.getEarliestDate(CapeTownPastStages)
     
        max_date = CapeTownPastStages.getLatestDate(CapeTownPastStages)
        n_days = int( (max_date-min_date).days )
        max_area = 16
        
        for d in range(n_days):
            for a in range(1,max_area):
                self.populateSlotsForDateArea(self,min_date+datetime.timedelta(d),a)
            
           
    def __str__(self):
        
        return "For date: " + str(self.date) + " and area code: " + str(self.area_code) + " Load-shedding slot "+self.start_time.strftime('%H:%M')+"-"+self.end_time.strftime('%H:%M')
    
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
    
    def stageQuery(stage,area_code):
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
    
    def cleanDates(t1,t2):
        #Clean dates to work in filterbyStageTimes function below
        if(t1.minute != 0):
            t1 = datetime.time(t1.hour, 0)
        if(t1.hour %2 != 0):
            t1 = datetime.time(t1.hour-1, 0)
        if(t2.hour<22):
            if(t2.minute != 0):
                t2 = datetime.time(t2.hour+1, 0)
            if(t2.hour %2 != 0):
                t2 = datetime.time(t2.hour+1, 0)
        elif(t2.hour==22 and t2.minute==0):
            #Find better solution
            t2 = datetime.time(22,0)
        else:
            t2 = datetime.time(23, 59)

        return t1, t2

    
    def filterbyStageTimes(self, q_day, q_area, q_stage, t1, t2):
        
        t1, t2 = self.cleanDates(t1,t2)

        day_slots = self.objects.filter(Q(day=q_day) & Q(start_time__gte=t1) & Q(end_time__lte=t2) )
        stage_query = self.stageQuery(q_stage,q_area)

        if stage_query is None:
            day_slots = self.objects.none()
        else:
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

    def getEarliestDate(self):
        return self.objects.earliest('date').date
    
    def getLatestDate(self):
        return self.objects.latest('date').date

    def filterDateTimes(self,q_date,q_start,q_end):
        """"Simple filter that will return query set for date q_date of stage intervals that span the time window ranging from q_start
            to q_end
        """  
        start_a = datetime.datetime.combine(q_date,q_start) 
        end_b = datetime.datetime.combine(q_date,q_end) 

        #Must not include q_end in q_start's search range if it is possibly the boundary of a stage time interval
        if q_end.minute == 0:
            start_b = datetime.datetime.combine(q_date,datetime.time(q_end.hour-1,59)) 
        else:
            start_b = datetime.datetime.combine(q_date,q_end)

        #Same as above except to exclude q_start from the q_end seacrh range
        if q_start.minute == 0:
            end_a = datetime.datetime.combine(q_date,datetime.time(q_start.hour,1)) 
        else:
            end_a = datetime.datetime.combine(q_date,q_start) 

        #Returns Query set if stage time interval falls within search window
        day_slots = self.objects.filter(Q(date=q_date) & (Q(start_time__range=(start_a, start_b)) | Q(end_time__range=(end_a, end_b))) )
        
        #For the case when the search window is fully contained within a stage interval 
        if not day_slots:

            day_stages = self.objects.filter(date=q_date) 
            for stage in day_stages:

                if q_start >= stage.start_time and q_end <= stage.end_time:
                    return self.objects.filter(past_stage_id = stage.past_stage_id ) #Only one query item is expected

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
    
    def getUserStartTime(self):
        return self.user_time_start
    
    def getUserEndTime(self):
        return self.user_time_end

    def __str__(self):
        return self.user.username + " is in area code " + str(self.user_area.area_code) + " and has an hourly cost of R" + str(self.user_hour_cost) + " from " + self.user_time_start.strftime('%H:%M')+" to "+self.user_time_end.strftime('%H:%M')
