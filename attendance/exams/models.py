from django.db import models
from classes.models import Class, Subject


class Exam(models.Model):
    name = models.CharField(max_length=100)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    exam_type_choices = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]
    exam_type = models.CharField(max_length=20, choices=exam_type_choices)
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    total_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=35)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date', 'start_time']

    def __str__(self):
        return f"{self.name} - {self.class_enrolled.name} - {self.subject.name}"


class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='exam_results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-exam__date']
        unique_together = ['exam', 'student']

    def __str__(self):
        return f"{self.student} - {self.exam.name} - {self.marks_obtained}"

    def save(self, *args, **kwargs):
        if self.marks_obtained >= self.exam.total_marks * 0.9:
            self.grade = 'A+'
        elif self.marks_obtained >= self.exam.total_marks * 0.8:
            self.grade = 'A'
        elif self.marks_obtained >= self.exam.total_marks * 0.7:
            self.grade = 'B+'
        elif self.marks_obtained >= self.exam.total_marks * 0.6:
            self.grade = 'B'
        elif self.marks_obtained >= self.exam.total_marks * 0.5:
            self.grade = 'C'
        elif self.marks_obtained >= self.exam.passing_marks:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='report_cards')
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    rank = models.PositiveIntegerField(null=True, blank=True)
    generated_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-exam__date']

    def __str__(self):
        return f"{self.student} - {self.exam.name} - Grade: {self.grade}"

    def save(self, *args, **kwargs):
        self.percentage = (self.obtained_marks / self.total_marks) * 100
        if self.percentage >= 90:
            self.grade = 'A+'
        elif self.percentage >= 80:
            self.grade = 'A'
        elif self.percentage >= 70:
            self.grade = 'B+'
        elif self.percentage >= 60:
            self.grade = 'B'
        elif self.percentage >= 50:
            self.grade = 'C'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)