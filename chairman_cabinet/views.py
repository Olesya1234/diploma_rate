from django.http import Http404
from django.shortcuts import render, redirect

from core.models import Group, FinalMark, Student, CommissionMark, Profile
from core.views import check_perm


@check_perm('chairman')
def student_table(request, group_id):
    groups = Group.objects.filter(pk=group_id)

    if not groups:
        raise Http404('Group is not found')

    group = groups.first()
    students = group.students.all()

    chairman_marks = FinalMark.objects.filter(chairman=request.user.profile)
    marks_dict = {mark.student.id: mark.mark for mark in chairman_marks}

    data = {
        'groups': Group.objects.all(),
        'group_name': group.name,
        'students': [
            {
                'id': student.id,
                'fio': student.fio,
                'diploma_name': student.diploma_name,
                'mark': marks_dict.get(student.id, '-')
            } for student in students
        ]
    }

    return render(request, 'chairman_student_table.html', data)


@check_perm('chairman')
def mark_form(request, student_id):
    students = Student.objects.filter(pk=student_id)

    if not students:
        raise Http404('Student is not found')

    student = students.first()

    commissions = Profile.objects.filter(role=2)  # Только члены комиссии
    commission_marks = {cm.comission.id: cm.mark for cm in CommissionMark.objects.filter(student=student)}

    av_mark = sum(mark for mark in commission_marks.values())/len(commission_marks) if commission_marks else None

    commission_dicts = [
        {
            'commission_str': commission.fio + (', {}'.format(commission.degree) if commission.degree else ''),
            'mark': commission_marks.get(commission.id, '-')
        } for commission in commissions
    ]

    final_mark_objs = FinalMark.objects.filter(student=student, chairman=request.user.profile)

    if final_mark_objs:
        final_mark = final_mark_objs.first().mark
    else:
        final_mark = None

    data = {
        'groups': Group.objects.all(),
        'student': student,
        'commissions': commission_dicts,
        'final_mark': final_mark,
        'av_mark': av_mark
    }

    return render(request, 'chairman_mark_student.html', data)


@check_perm('chairman')
def take_mark(request, student_id):
    students = Student.objects.filter(pk=student_id)

    if not students or request.method != 'POST':
        raise Http404('Student is not found')

    student = students.first()

    mark = request.POST.get('final')

    final_mark_objs = FinalMark.objects.filter(student=student, chairman=request.user.profile)

    if final_mark_objs:
        final_mark_objs.first().update(mark=mark)
    else:
        FinalMark.objects.create(student=student, chairman=request.user.profile, mark=mark)

    return redirect('/cabinet/chairman/student/{}'.format(student_id))
