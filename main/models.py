from django.db import models
from django.db.models import JSONField


class User(models.Model):
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=50)
    fname = models.CharField(max_length=70, default='First Name')
    lname = models.CharField(max_length=70, default='Last Name')
    department = models.CharField(max_length=70, default='Engineering')

    class Meta:
        db_table = "user" 

class TemplateActualNormal(models.Model):
    templateID = models.IntegerField()
    templateName = models.CharField(max_length=70)
    templateType = models.CharField(max_length=70)
    startRow = models.IntegerField()
    columnName = models.CharField(max_length=70)
    columnNumber = models.CharField(max_length=30)
    fileType = models.CharField(max_length=30)
    condition = models.CharField(max_length=200)
    amountdaysplus = models.IntegerField(default=0)
    columnNumberplus = models.IntegerField(default=0)
    needBackupData = models.CharField(max_length=30)
    
    class Meta:
        db_table = "template_actual_n"

class TemplateSpecial(models.Model):
    templateID = models.IntegerField()
    templateName = models.CharField(max_length=70)
    templateType = models.CharField(max_length=70)
    startRow = models.IntegerField()
    columnName = models.CharField(max_length=70)
    columnNumber = models.CharField(max_length=30)
    fileType = models.CharField(max_length=30)
    needBackupData = models.CharField(max_length=30)
    
    class Meta:
        db_table = "template_s"
    

class CustomerOrder(models.Model):
    templateName = models.CharField(max_length=70)
    customerCode = models.CharField(max_length=70)
    customerPartNumber = models.CharField(max_length=70)
    orderQuantity = models.IntegerField()
    deliveryDate = models.CharField(max_length=70)
    deliveryTime = models.CharField(max_length=70,default='NULL')
    deliveryPlant = models.CharField(max_length=70,default='NULL')
    templateID = models.CharField(max_length=70)
    
    class Meta:
        db_table = "customerOrder" 

class CustomerOrderForecast(models.Model):
    templateName = models.CharField(max_length=70)
    customerCode = models.CharField(max_length=70)
    customerPartNumber = models.CharField(max_length=70)
    orderQuantity = models.IntegerField()
    deliveryDate = models.CharField(max_length=70)
    deliveryTime = models.CharField(max_length=70,default='NULL')
    deliveryPlant = models.CharField(max_length=70,default='NULL')
    templateID = models.CharField(max_length=70)
    
    class Meta:
        db_table = "customerOrderForecast" 

class CustomerData(models.Model):
    customerName = models.CharField(max_length=70)
    customerCode = models.CharField(max_length=70)
    templateName = models.CharField(max_length=70)
    customerPartNumber = models.CharField(max_length=70)
    SNSSPartNumber = models.CharField(max_length=70)
    category = models.CharField(max_length=70, default='GEN')
    templateID = models.CharField(max_length=70,default='NULL', )

    class Meta:
        db_table = "customerData" 

class StockData(models.Model):
    snssPartID = models.IntegerField()
    snssPartNumber = models.CharField(max_length=70)
    stockQty = models.CharField(max_length=70)
    lineInfo = models.CharField(max_length=70)
    dateImport = models.CharField(max_length=70)

    class Meta:
        db_table = "stockData" 

        