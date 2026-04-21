from django.db import models
from classes.models import Class


class FeeStructure(models.Model):
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='fee_structures')
    fee_type_choices = [
        ('tuition', 'Tuition Fee'),
        ('admission', 'Admission Fee'),
        ('exam', 'Exam Fee'),
        ('transport', 'Transport Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Lab Fee'),
        ('annual', 'Annual Charge'),
        ('other', 'Other'),
    ]
    fee_type = models.CharField(max_length=20, choices=fee_type_choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    is_active = models.BooleanField(default=True)
    academic_year = models.CharField(max_length=20)

    class Meta:
        ordering = ['-academic_year', 'due_date']
        unique_together = ['class_enrolled', 'fee_type', 'academic_year']

    def __str__(self):
        return f"{self.class_enrolled.name} - {self.fee_type} - {self.amount}"


class FeePayment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fee_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method_choices = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card Payment'),
        ('online', 'Online Payment'),
    ]
    payment_method = models.CharField(max_length=20, choices=payment_method_choices)
    transaction_id = models.CharField(max_length=100, blank=True)
    remarks = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.student} - {self.fee_structure.fee_type} - {self.amount_paid}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last_payment = FeePayment.objects.order_by('-id').first()
            if last_payment and last_payment.receipt_number.startswith('RCP'):
                last_num = int(last_payment.receipt_number[3:])
                self.receipt_number = f"RCP{last_num + 1:04d}"
            else:
                self.receipt_number = "RCP0001"
        super().save(*args, **kwargs)


class FeeDue(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fee_dues')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    due_date = models.DateField()

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.student} - {self.fee_structure.fee_type}"

    @property
    def balance(self):
        return self.amount_due - self.amount_paid