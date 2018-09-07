from django.core.management.base import BaseCommand
from django.db.models import F, Q
from datetime import timedelta
from cms.utils import send_email_template
from ...models import PropertyAlert, PropertyAlertLog


class Command(BaseCommand):
    help = 'Identifies alerts that have new listings and need to send'

    def add_arguments(self, parser):
        parser.add_argument('--alert_id', type=int, action='store', dest='alert_id')

    def handle(self, *args, **options):
        ready_alerts = PropertyAlert.subscribers.filter(
            Q(last_sent__lte=F('last_sent') - timedelta(days=1)*F('frequency')) |  # hack for timedelta + F
            Q(last_sent=None)
        )

        if options.get('alert_id'):
            ready_alerts = PropertyAlert.objects.filter(pk=options['alert_id'])

        for alert in ready_alerts:
            listings = alert.get_new_listings()
            if not listings:
                continue
            send_email_template(
                alert.get_email_subject(),
                alert.email_sender,
                [alert.email],
                alert.get_email_template(),
                {'alert': alert, 'listings': listings},
                include_cc=False
            )
            PropertyAlertLog(alert=alert).save()
