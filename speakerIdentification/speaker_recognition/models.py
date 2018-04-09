from django.db import models

class Customer(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=200, null=False)
    keyAPI = models.CharField(max_length=200, null=False)
    pathTrainingDataSet = models.CharField(max_length=1000, null=True)
    status = models.BooleanField(default=1, null=False)
    class Meta:
        db_table = "Customer"

class User(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    identificationProfileId = models.CharField(max_length=200, null=False)
    pathNN = models.CharField(max_length=1000, null=True)
    status = models.BooleanField(default=1, null=False)
    idCostumer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    class Meta:
        db_table = "User"
# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     rating = models.CharField(max_length=400, default='some string')
#     def __str__(self):
#         return self.choice_text
# Create your models here.
