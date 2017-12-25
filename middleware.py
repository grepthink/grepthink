import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from tzlocal import get_localzone
from datetime import datetime

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = get_localzone()
        if tzname:
            timezone.activate(tzname)
        else:
            timezone.deactivate()
