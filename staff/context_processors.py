from django.conf import settings


def custom_settings(request):
    return {'CUSTOM_STAFF_ID': settings.CUSTOM_STAFF_ID, 'CUSTOM_GUEST_ID': settings.CUSTOM_GUEST_ID}