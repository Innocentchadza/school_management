from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Program)
admin.site.register(Students)
admin.site.register(SchoolFees)
admin.site.register(Examination)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(StudentResponse)
admin.site.register(ExamResult)