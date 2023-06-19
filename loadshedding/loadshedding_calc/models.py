from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

#visit bookmark for inetoone field better query implementation

class CapeTownAreas(models.Model):
    ct_area_id = models.AutoField(primary_key=True)
    area_name = models.CharField(max_length=80)
    area_code = models.SmallIntegerField()

    def __str__(self):
        return self.area_name + " is in area code: " + str(self.area_code)
    
    
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

    def __str__(self):
        return self.user.username + " is in area code " + str(self.user_area.area_code) + " and has an hourly cost of R" + str(self.user_hour_cost) + " from " + self.user_time_start.strftime('%H:%M')+" to "+self.user_time_end.strftime('%H:%M')

#class TimeSlotsDay(models.Model):
#    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#    date = models.IntegerField()
#    time_slots = models.CharField(max_length=80)

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

    def __str__(self):
        return str(self.day)+" = "+self.start_time.strftime('%H:%M')+"-"+self.end_time.strftime('%H:%M')
    
    def is_stage(self,stage_val):
        """Returns 1 if contains stage in lower number """
        return True
