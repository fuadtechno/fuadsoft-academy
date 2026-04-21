from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Announcement, Notification, EmailNotification
from accounts.models import User
from .forms import AnnouncementForm


@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(is_published=True)

    if request.user.is_admin:
        pass
    elif request.user.is_teacher:
        announcements = announcements.filter(Q(target_role='all') | Q(target_role='teachers'))
    else:
        announcements = announcements.filter(Q(target_role='all') | Q(target_role='students'))

    return render(request, 'notifications/announcement_list.html', {'announcements': announcements})


@login_required
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.sent_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('announcement_list')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
    else:
        form = AnnouncementForm()
    return render(request, 'notifications/announcement_form.html', {'form': form})


@login_required
def announcement_update(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.message = request.POST.get('message')
        announcement.priority = request.POST.get('priority')
        announcement.target_role = request.POST.get('target_role')
        announcement.publish_date = request.POST.get('publish_date')
        announcement.expiry_date = request.POST.get('expiry_date')
        announcement.is_published = request.POST.get('is_published') == 'on'
        announcement.save()
        messages.success(request, 'Announcement updated successfully.')
        return redirect('announcement_list')

    return render(request, 'notifications/announcement_form.html', {'announcement': announcement})


@login_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.success(request, 'Announcement deleted successfully.')
    return redirect('announcement_list')


@login_required
def my_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'notifications/my_notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('my_notifications')


@login_required
def send_email_notification(request):
    if request.method == 'POST':
        recipient_email = request.POST.get('recipient')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            EmailNotification.objects.create(
                recipient=recipient_email,
                subject=subject,
                message=message,
                status='sent',
            )
            messages.success(request, 'Email sent successfully.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')

        return redirect('announcement_list')

    return render(request, 'notifications/send_email.html')