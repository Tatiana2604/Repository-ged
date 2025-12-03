from django.db.models.signals import post_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from audit.models import AuditLog
from audit.middleware import get_current_user, get_current_request
from datetime import datetime, date
from decimal import Decimal

def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value

def serialize_data(data):
    if not data:
        return data
    return {key: serialize_value(value) for key, value in data.items()}


def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_audit_log(instance, action, old_data=None, new_data=None):
    old_data = serialize_data(old_data)
    new_data = serialize_data(new_data)

    user = get_current_user()
    request = get_current_request()
    ip = get_client_ip(request)
    if not user or user.is_anonymous:
        return
    AuditLog.objects.create(
        utilisateur=user,
        action=action,
        modele=instance.__class__.__name__,
        object_id=instance.pk,
        ancienne_valeur=old_data,
        nouvelle_valeur=new_data,
        adresse_ip=ip

    )


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
    action = "creation" if created else "Modification"
    new_data = model_to_dict(instance)
    create_audit_log(instance,action,None, new_data)


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
    old_data = model_to_dict(instance)
    create_audit_log(instance, 'Suppression', old_data, None)