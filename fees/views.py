from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import FeeStructure, FeePayment, FeeDue
from students.models import Student
from classes.models import Class
from .forms import FeeStructureForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_superuser
        )


class FeeStructureListView(AdminRequiredMixin, ListView):
    model = FeeStructure
    template_name = 'fees/fee_structure_list.html'
    context_object_name = 'fee_structures'

    def get_queryset(self):
        queryset = FeeStructure.objects.all().select_related('class_enrolled')
        class_id = self.request.GET.get('class')
        academic_year = self.request.GET.get('academic_year')
        if class_id:
            queryset = queryset.filter(class_enrolled_id=class_id)
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
        return queryset


class FeeStructureCreateView(AdminRequiredMixin, CreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fees/fee_structure_form.html'
    success_url = reverse_lazy('fee_structure_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fee structure created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class FeeStructureUpdateView(AdminRequiredMixin, UpdateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fees/fee_structure_form.html'
    success_url = reverse_lazy('fee_structure_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fee structure updated successfully.')
        return super().form_valid(form)


fee_structure_list = FeeStructureListView.as_view()
fee_structure_create = FeeStructureCreateView.as_view()
fee_structure_update = FeeStructureUpdateView.as_view()


@login_required
def fee_structure_update(request, pk):
    fee_structure = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=fee_structure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee structure updated successfully.')
            return redirect('fee_structure_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = FeeStructureForm(instance=fee_structure)
    return render(request, 'fees/fee_structure_form.html', {'form': form, 'fee_structure': fee_structure})


@login_required
def fee_payment(request):
    student_id = request.GET.get('student')
    class_id = request.GET.get('class')

    students = Student.objects.filter(is_active=True).select_related('user', 'class_enrolled')

    if student_id:
        students = students.filter(id=student_id)
    if class_id:
        students = students.filter(class_enrolled_id=class_id)

    payments = FeePayment.objects.all().select_related('student__user', 'fee_structure')
    if student_id:
        payments = payments.filter(student_id=student_id)

    return render(request, 'fees/fee_payment.html', {'students': students, 'payments': payments})


@login_required
def record_payment(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        fee_structure_id = request.POST.get('fee_structure_id')
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '')
        remarks = request.POST.get('remarks', '')

        student = get_object_or_404(Student, id=student_id)
        fee_structure = get_object_or_404(FeeStructure, id=fee_structure_id)

        payment = FeePayment.objects.create(
            student=student,
            fee_structure=fee_structure,
            amount_paid=amount,
            payment_method=method,
            transaction_id=transaction_id,
            remarks=remarks,
        )

        due = FeeDue.objects.filter(student=student, fee_structure=fee_structure).first()
        if due:
            due.amount_paid += float(amount)
            if due.amount_paid >= due.amount_due:
                due.is_paid = True
            due.save()

        messages.success(request, f'Payment recorded. Receipt: {payment.receipt_number}')
        return redirect('fee_payment')

    student_id = request.GET.get('student_id')
    student = get_object_or_404(Student, id=student_id)
    fee_structures = FeeStructure.objects.filter(class_enrolled=student.class_enrolled)

    return render(request, 'fees/record_payment.html', {
        'student': student,
        'fee_structures': fee_structures,
    })


@login_required
def fee_dues(request):
    class_id = request.GET.get('class')
    is_paid = request.GET.get('is_paid')

    dues = FeeDue.objects.all().select_related('student__user', 'fee_structure__class_enrolled')

    if class_id:
        dues = dues.filter(fee_structure__class_enrolled_id=class_id)
    if is_paid:
        dues = dues.filter(is_paid=is_paid == 'true')

    return render(request, 'fees/fee_dues.html', {'dues': dues})


@login_required
def generate_receipt(request, payment_id):
    payment = get_object_or_404(FeePayment, pk=payment_id)

    return render(request, 'fees/receipt.html', {'payment': payment})


@login_required
def revenue_report(request):
    class_id = request.GET.get('class')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    payments = FeePayment.objects.all()

    if class_id:
        payments = payments.filter(fee_structure__class_enrolled_id=class_id)
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)

    total_collected = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    return render(request, 'fees/revenue_report.html', {
        'payments': payments,
        'total_collected': total_collected,
    })