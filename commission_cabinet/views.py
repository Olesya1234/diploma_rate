from django.shortcuts import render, redirect
from django.http import Http404

from core.models import Group, Student, CommissionMark, MapMarkCriterion, Criterion, CriterionRanking
from core.views import check_perm


@check_perm('commission')
def student_table(request, group_id):
    groups = Group.objects.filter(pk=group_id)

    if not groups:
        raise Http404('Group is not found')

    group = groups.first()
    students = group.students.all()

    commission_marks = CommissionMark.objects.filter(comission=request.user.profile)
    marks_dict = {mark.student.id: mark.calc_average_mark() for mark in commission_marks}

    data = {
        'groups': Group.objects.all(),
        'group_name': group.name,
        'students': [
            {
                'id': student.id,
                'fio': student.fio,
                'diploma_name': student.diploma_name,
                'mark': '{:0<4}'.format(marks_dict.get(student.id)) if marks_dict.get(student.id) else '-'
            } for student in students
        ]
    }

    return render(request, 'commission_student_table.html', data)


@check_perm('commission')
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
        sum_weights = sum(cr.criterion.weight for cr in crits)
        av_mark = '{:0<4}'.format(round(sum(cr.criterion.weight * cr.criterion_mark for cr in crits)/sum_weights, 2))
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

    return render(request, 'commission_mark_student.html', data)


@check_perm(['chairman', 'commission'])
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

    sum_weights = sum(cr['criterion'].weight for i, cr in crits.items())
    final_mark = round(sum(cr['criterion'].weight * int(cr['mark']) for i, cr in crits.items()) / sum_weights)

    if real_final_mark:
        real_final_mark.update(mark=final_mark)
        cm = real_final_mark.first()
    else:
        cm = CommissionMark.objects.create(student=student, comission=request.user.profile, mark=final_mark)

    for i, cr in crits.items():
        if cr['criterion'] in real_crit_marks:
            m = MapMarkCriterion.objects.filter(commission_mark=cm, criterion=cr['criterion'])
            m.update(criterion_mark=cr['mark'])
        else:
            MapMarkCriterion.objects.create(commission_mark=cm, criterion=cr['criterion'], criterion_mark=cr['mark'])

    if request.user.profile.role == 1:
        return redirect('/cabinet/chairman/student/{}'.format(student_id))
    else:
        return redirect('/cabinet/commission/student/{}'.format(student_id))


@check_perm('commission')
def kriterions(request):
    crits = Criterion.objects.all()

    cr_ranks = CriterionRanking.objects.filter(comission=request.user.profile)

    crits = [
        {
            'obj': x,
            'rank': cr_ranks.filter(criterion=x).first() if cr_ranks.filter(criterion=x) else None
        } for x in crits
    ]

    if request.method == 'GET':
        data = {
            'groups': Group.objects.all(),
            'criteries': crits,
            'len_crit': len(crits)
        }
        return render(request, 'commission_krits.html', data)

    crits = dict()

    for cr in Criterion.objects.all():
        crit_rank = request.POST.get('c_{}'.format(cr.id))
        crits[cr.id] = {
            'criterion': cr,
            'rank': crit_rank
        }

    all_ranks = {x['rank'] for x in crits.values()}
    k = 1
    for rank in sorted(all_ranks):
        if int(rank) != k:
            print('Недопустимые критерии')
            print(rank, k)
            return redirect('/cabinet/commission/crits')
        k += 1

    if len(all_ranks) != len(crits):
        print('Заполнены не все критерии')
        data = {
            'groups': Group.objects.all(),
            'criteries': crits,
            'len_crit': len(crits),
        }
        return render(request, 'commission_krits.html', data)

    if cr_ranks:
        cr_ranks.delete()

    for i, cr in crits.items():
        CriterionRanking.objects.create(comission=request.user.profile, criterion=cr['criterion'], rank=cr['rank'])

    return redirect('/cabinet/commission/crits')
