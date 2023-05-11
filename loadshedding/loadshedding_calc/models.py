from django.db import models

class TimeSlot(models.Model):
    day = models.IntegerField()
    area_code = models.IntegerField()
    time_slots = models.CharField(max_length=80)

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
