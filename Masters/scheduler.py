from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import send_mail
from django.conf import settings
from .models import Customer
from datetime import date

def send_birthday_email(customer):
    subject = f"Happy Birthday {customer.FirstName}!"
    message = f"""
            Dear {customer.Salutation if customer.Salutation else ''} {customer.LastName},

            Wishing you a very happy birthday! 🎉🎂

            From all of us at CI Loan, we hope you have a wonderful day filled with joy and happiness.

            Best regards,
            CI Loan
            """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [customer.Email],
        fail_silently=False,
    )

def check_birthdays_and_send_emails():
    today = date.today()
    customers = Customer.objects.filter(
        DateOfBirth__month=today.month,
        DateOfBirth__day=today.day,
        Email__isnull=False
    ).exclude(Email__exact='')
    
    for customer in customers:
        send_birthday_email(customer)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Schedule the job to run daily at 12 AM
    scheduler.add_job(
        check_birthdays_and_send_emails,
        trigger=CronTrigger(hour=0, minute=0),  # Midnight
        id="birthday_emails",
        max_instances=1,
        replace_existing=True,
    )
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()