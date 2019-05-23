from django.shortcuts import render, redirect
from django.http import Http404

from core.models import Group, Student, CommissionMark, MapMarkCriterion, Criterion


def student_table(request, group_id):
    groups = Group.objects.filter(pk=group_id)

    if not groups:
        raise Http404('Group is not found')

    group = groups.first()
    students = group.students.all()

    commission_marks = CommissionMark.objects.filter(comission=request.user.profile)
    marks_dict = {mark.student.id: mark.mark for mark in commission_marks}

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

    return render(request, 'example_student_table.html', data)


def mark_form(request, student_id):
    students = Student.objects.filter(pk=student_id)

    if not students:
        raise Http404('Student is not found')

    student = students.first()

    crits = MapMarkCriterion.objects.filter(commission_mark__student=student,
                                            commission_mark__comission=request.user.profile)

    crits_dict = {cr.criterion.id: cr.criterion_mark for cr in crits}

    final_mark = CommissionMark.objects.filter(student=student, comission=request.user.profile)
    final_mark = final_mark.first().mark if final_mark else None

    print(crits_dict)

    if crits:
        av_mark = round(sum(cr.criterion.weight * cr.criterion_mark for cr in crits)/len(crits), 2)
    else:
        av_mark = None

    criteries = [
        {
            'id': crit.id,
            'name': crit.name,
            'value': crits_dict.get(crit.id)
        } for crit in Criterion.objects.all()
    ]

    data = {
        'groups': Group.objects.all(),
        'student': student,
        'criteries': criteries,
        'final_mark': final_mark,
        'av_mark': av_mark
    }

    return render(request, 'example_mark_student.html', data)


def take_mark(request, student_id):
    students = Student.objects.filter(pk=student_id)

    if not students or request.method != 'POST':
        raise Http404('Student is not found')

    student = students.first()

    real_final_mark = CommissionMark.objects.filter(student=student, comission=request.user.profile)
    print(real_final_mark)
    real_crit_marks = MapMarkCriterion.objects.filter(commission_mark__student=student,
                                            commission_mark__comission=request.user.profile)
    real_crit_marks = [x.criterion for x in real_crit_marks]

    crits = dict()

    for cr in Criterion.objects.all():
        crit_mark = request.POST.get('c_{}'.format(cr.id))
        crits[cr.id] = {
            'criterion': cr,
            'mark': crit_mark
        }

    final_mark = request.POST.get('final')

    if real_final_mark:
        real_final_mark.update(mark=final_mark)
        cm = real_final_mark.first()
    else:
        if not final_mark:
            final_mark = round(sum(cr['criterion'].weight * int(cr['mark']) for i, cr in crits.items())/len(crits))
        cm = CommissionMark.objects.create(student=student, comission=request.user.profile, mark=final_mark)

    for i, cr in crits.items():
        if cr['criterion'] in real_crit_marks:
            m = MapMarkCriterion.objects.filter(commission_mark=cm, criterion=cr['criterion'])
            m.update(criterion_mark=cr['mark'])
            print(m)
            # cr['criterion'].criterion_mark=cr['mark']
            # cr['criterion'].save()
        else:
            MapMarkCriterion.objects.create(commission_mark=cm, criterion=cr['criterion'], criterion_mark=cr['mark'])

    return redirect('/cabinet/commission/student/{}'.format(student_id))
