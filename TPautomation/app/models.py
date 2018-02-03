from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    # belongs_to = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name_zh = models.CharField(max_length=200)
    company_name_en = models.CharField(max_length=200)
    report_year = models.IntegerField()
    setup_year = models.IntegerField()
    setup_place = models.CharField(max_length=200)  #TODO: This may use choice Field(enumerate)
    business = models.CharField(max_length=1000)
    organization_chart = models.ImageField()
    def __str__(self):
        return str(self.report_year) + "_" + self.company_name_zh + "_" + self.business
