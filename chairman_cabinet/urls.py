from django.conf.urls import url

from chairman_cabinet.views import student_table, mark_form, take_mark, kriterions, change_weights, print_to_pdf

urlpatterns = [
    url(r'^group/(?P<group_id>\d+)$', student_table),
    url(r'^group/print/(?P<group_id>\d+)$', print_to_pdf),
    url(r'^student/(?P<student_id>\d+)$', mark_form),
    url(r'^mark/(?P<student_id>\d+)$', take_mark),
    url(r'^crits$', kriterions),
    url(r'^change_weights$', change_weights),
]
