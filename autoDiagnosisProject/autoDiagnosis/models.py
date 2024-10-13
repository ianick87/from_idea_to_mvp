from django.db import models


class Data(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight = models.FloatField()
    height = models.FloatField()
    temperature = models.FloatField()
    pulse = models.IntegerField()
    blood_pressure = models.CharField(max_length=7)
    headache = models.BooleanField()
    stomach_pain = models.BooleanField()
    throat_pain = models.BooleanField()
    has_disease = models.BooleanField()

    def __str__(self):
        return self.name
