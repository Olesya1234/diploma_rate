import numpy as np
import jinja2
import weasyprint
from datetime import datetime

from django.http import Http404
from django.shortcuts import render, redirect

from chairman_cabinet.calc_weight import calc_weights
from core.models import Group, FinalMark, Student, CommissionMark, Profile, Criterion, CriterionRanking, \
    MapMarkCriterion
from core.views import check_perm

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa


@check_perm('chairman')
def student_table(request, group_id):
    groups = Group.objects.filter(pk=group_id)

    if not groups:
        raise Http404('Group is not found')

    group = groups.first()
    students = group.students.all()

    data = {
        'groups': Group.objects.all(),
        'group_name': group.name,
        'group_id': group.id,
        'students': [
            {
                'id': student.id,
                'fio': student.fio,
                'diploma_name': student.diploma_name,
                'av_mark': student.calc_average_mark() if student.calc_average_mark() else '-',
                'final_mark': student.calc_final_mark() if student.calc_final_mark() else '-'
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


def print_to_pdf(request, group_id):
    groups = Group.objects.filter(pk=group_id)

    if not groups:
        raise Http404('Group is not found')

    group = groups.first()
    students = group.students.all()

    data = {
        'group_name': group.name,
        'date_print': datetime.now().strftime("%d.%m.%Y"),
        'students': [
            {
                'counter': i,
                'fio': student.fio,
                'final_mark': student.calc_final_mark() if student.calc_final_mark() else '-'
            } for i, student in enumerate(students, 1)
        ]
    }

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates'),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )

    template = env.get_template('pdf_template.html')
    whtml = weasyprint.HTML(string=template.render(data).encode('utf8'))
    wcss = weasyprint.CSS(filename='./templates/style.css')

    pdf_file = whtml.write_pdf(stylesheets=[wcss])

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="home_page.pdf"'

    return response
