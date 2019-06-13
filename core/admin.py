from django.contrib import admin

from core.models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    pass


@admin.register(CommissionMark)
class CommissionMarkAdmin(admin.ModelAdmin):
    pass


@admin.register(FinalMark)
class FinalMarkAdmin(admin.ModelAdmin):
    pass


@admin.register(MapMarkCriterion)
class MapMarkCriterionAdmin(admin.ModelAdmin):
    pass


@admin.register(CriterionRanking)
class CriterionRankingAdmin(admin.ModelAdmin):
    pass
