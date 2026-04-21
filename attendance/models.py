from django.db import models
from students.models import Student
from classes.models import Class


class Attendance(models.Model):
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status_choices = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='present')
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'student']
        unique_together = ['student', 'date', 'class_enrolled']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class AttendanceSummary(models.Model):
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_summaries')
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    total_days = models.PositiveIntegerField(default=0)
    present_days = models.PositiveIntegerField(default=0)
    absent_days = models.PositiveIntegerField(default=0)
    late_days = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['class_enrolled', 'month', 'year']

    def __str__(self):
        return f"{self.class_enrolled.name} - {self.month}/{self.year}"

    @property
    def attendance_percentage(self):
        if self.total_days > 0:
            return round((self.present_days / self.total_days) * 100, 2)
        return 0