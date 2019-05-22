from django.shortcuts import render


def index(request):
    return render(request, 'example_mark_student.html', {})
