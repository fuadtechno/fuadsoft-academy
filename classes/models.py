from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Class(models.Model):
    name = models.CharField(max_length=50)
    level = models.PositiveIntegerField()
    section = models.CharField(max_length=10, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name='classes')
    class_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_classes'
    )
    academic_year = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'section']
        unique_together = ['name', 'section', 'academic_year']

    def __str__(self):
        return f"{self.name} - {self.section}"


class Section(models.Model):
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(default=40)

    class Meta:
        ordering = ['name']
        unique_together = ['class_enrolled', 'name']

    def __str__(self):
        return f"{self.class_enrolled.name} - {self.name}"


class Timetable(models.Model):
    day_choices = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    day = models.CharField(max_length=20, choices=day_choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ['class_enrolled', 'day', 'start_time']

    def __str__(self):
        return f"{self.class_enrolled.name} - {self.subject.name} - {self.day}"