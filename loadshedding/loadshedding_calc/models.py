from django.db import models

class TimeSlot(models.Model):
    day = models.IntegerField()
    area_code = models.IntegerField()
    time_slots = models.CharField(max_length=80)
