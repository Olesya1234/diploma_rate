import numpy as np

from django.http import Http404
from django.shortcuts import render, redirect

from chairman_cabinet.calc_weight import calc_weights
from core.models import Group, FinalMark, Student, CommissionMark, Profile, Criterion, CriterionRanking
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
    av_mark = round(av_mark, 2) if av_mark else None

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
        final_mark_objs.update(mark=mark)
    else:
        FinalMark.objects.create(student=student, chairman=request.user.profile, mark=mark)

    return redirect('/cabinet/chairman/student/{}'.format(student_id))


@check_perm('chairman')
def kriterions(request):
    comm_map = {}
    krit_map = {}

    commissions = Profile.objects.filter(role=2)
    crits = Criterion.objects.all()

    for i, comm in enumerate(commissions):
        comm_map[comm.id] = i

    for i, cr in enumerate(crits):
        krit_map[cr.id] = i

    cr_ranks = CriterionRanking.objects.filter()

    cr_table = np.zeros((len(commissions), len(crits)), dtype=np.int8)

    for comm in commissions:
        for cr in crits:
            rank = cr_ranks.filter(comission=comm, criterion=cr)
            rank = rank.first().rank if rank else 0
            cr_table[comm_map[comm.id]][krit_map[cr.id]] = rank

    table = [x for x in cr_table if all(x)]

    print(table)

    if table:
        weights, W = calc_weights(table)
        W = round(W, 2)
    else:
        weights, W = ['-'] * len(crits), ''

    data = {
        'commissions': [
            {
                'i': comm_map[comm.id] + 1,
                'obj': comm
            } for comm in commissions
        ],
        'crits': [
            {
                'i': krit_map[crit.id] + 1,
                'obj': crit,
                'ranks': cr_table[:, krit_map[crit.id]],
                'weight': weights[krit_map[crit.id]]
            } for crit in crits
        ],
        'groups': Group.objects.all(),
        'W': W
    }

    return render(request, 'chairman_krits.html', data)


@check_perm('chairman')
def change_weights(request):
    comm_map = {}
    krit_map = {}

    commissions = Profile.objects.filter(role=2)
    crits = Criterion.objects.all()

    for i, comm in enumerate(commissions):
        comm_map[comm.id] = i

    for i, cr in enumerate(crits):
        krit_map[cr.id] = i

    cr_ranks = CriterionRanking.objects.filter()

    cr_table = np.zeros((len(commissions), len(crits)), dtype=np.int8)

    for comm in commissions:
        for cr in crits:
            rank = cr_ranks.filter(comission=comm, criterion=cr)
            rank = rank.first().rank if rank else 0
            cr_table[comm_map[comm.id]][krit_map[cr.id]] = rank

    table = [x for x in cr_table if all(x)]

    if table:
        weights, W = calc_weights(table)
    else:
        return redirect('/cabinet/chairman/crits')

    for crit in crits:
        crit.weight = weights[krit_map[crit.id]]
        crit.save()

    return redirect('/cabinet/chairman/crits')
