from django.contrib import admin
from myapp.models import Course
from myapp.models import Module
from myapp.models import Lesson
from myapp.models import Userregister
from myapp.models import person
from myapp.models import MCQQuestion


# Register your models here.
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(MCQQuestion)
admin.site.register(Userregister)
admin.site.register(person)
