from django.db import models
from django.contrib.auth.models import User


MARK_CHOICES = (
    (2, 'Неудовлетворительно'),
    (3, 'Удовлетворительно'),
    (4, 'Хорошо'),
    (5, 'Отлично'),
)


class Profile(models.Model):
    ROLE_CHOICES = (
        (1, 'Председатель комиссии'),
        (2, 'Член комиссии'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    fio = models.CharField(max_length=128, verbose_name='ФИО')
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, verbose_name='Роль')
    degree = models.CharField(max_length=32, blank=True, null=True, verbose_name='Науч. степень')

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username


class Group(models.Model):
    name = models.CharField(max_length=16, verbose_name='Название')

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name


class Student(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students', verbose_name='Группа')
    fio = models.CharField(max_length=128, verbose_name='ФИО')
    diploma_name = models.CharField(max_length=128, verbose_name='Тема диплома')

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return self.fio


class Criterion(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    weight = models.FloatField(default=1, verbose_name='Вес')

    class Meta:
        verbose_name = "Критерий"
        verbose_name_plural = "Критерии"

    def __str__(self):
        return self.name


class CommissionMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    comission = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Член комиссии')
    mark = models.PositiveSmallIntegerField(choices=MARK_CHOICES)

    class Meta:
        verbose_name = "Оценка члена комиссии"
        verbose_name_plural = "Оценки членов комиссии"

    def __str__(self):
        return '[{}] {} {}'.format(self.id, self.student, self.comission)


class FinalMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    chairman = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Председатель')
    mark = models.PositiveSmallIntegerField(choices=MARK_CHOICES)

    class Meta:
        verbose_name = "Оценка председателя комиссии"
        verbose_name_plural = "Оценки председателя комиссии"

    def __str__(self):
        return '[{}] {} {}'.format(self.id, self.student, self.chairman)


class MapMarkCriterion(models.Model):
    commission_mark = models.ForeignKey(CommissionMark, on_delete=models.CASCADE, verbose_name='Оценка комиссии')
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE, verbose_name='Критерий')
    criterion_mark = models.PositiveSmallIntegerField(choices=MARK_CHOICES)

    class Meta:
        verbose_name = "Оценка критерия"
        verbose_name_plural = "Оценки критериев"

    def __str__(self):
        return 'Critetion {}'.format(self.id)
