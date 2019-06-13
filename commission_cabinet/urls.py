from django.conf.urls import url

from commission_cabinet.views import student_table, mark_form, take_mark, kriterions


urlpatterns = [
    url(r'^group/(?P<group_id>\d+)$', student_table),
    url(r'^student/(?P<student_id>\d+)$', mark_form),
    url(r'^mark/(?P<student_id>\d+)$', take_mark),
    url(r'^crits$', kriterions),
]
