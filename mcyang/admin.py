from django.contrib import admin
from .models import *


class McyangTeacherAdmin(admin.ModelAdmin):
    list_display = [field.name for field in McyangTeacher._meta.fields]


class McyangStudentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in McyangStudent._meta.fields]


class McyangCourseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in McyangCourse._meta.fields]


class McyangCourseRecordAdmin(admin.ModelAdmin):
    list_display = [field.name for field in McyangCourseRecord._meta.fields]


admin.site.register(McyangTeacher, McyangTeacherAdmin)
admin.site.register(McyangStudent, McyangStudentAdmin)
admin.site.register(McyangCourse, McyangCourseAdmin)
admin.site.register(McyangCourseRecord, McyangCourseRecordAdmin)
