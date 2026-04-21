from django.contrib import admin
from .models import FeeStructure, FeePayment, FeeDue


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_enrolled', 'fee_type', 'amount', 'due_date', 'academic_year', 'is_active')
    list_filter = ('academic_year', 'fee_type', 'is_active')
    search_fields = ('class_enrolled__name',)


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_paid', 'payment_date', 'payment_method', 'receipt_number')
    list_filter = ('payment_date', 'payment_method')
    search_fields = ('student__student_id', 'receipt_number')


@admin.register(FeeDue)
class FeeDueAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_due', 'amount_paid', 'is_paid', 'due_date')
    list_filter = ('is_paid', 'due_date')
    search_fields = ('student__student_id',)