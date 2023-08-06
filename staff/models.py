from django.db import models
from django.dispatch import receiver
from django.conf import settings
import uuid
import qrcode
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import base64
import os
import random


def random_id():
    while True:
        id = str(random.randrange(1000, 10000)) + "-" + str(random.randrange(1000, 10000))
        if not Ticket.objects.filter(voting_id=id).exists():
            return id


class School(models.Model):
    name = models.CharField(max_length=20)
    chaperones = models.ManyToManyField("Ticket",
                                        limit_choices_to=models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                                            id=settings.CUSTOM_CHAPERONE_STAFF_ID), blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Committee(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Voting(models.Model):
    VOTING_TYPE_CHOICES = [
        ('CV', 'Clause Voting Procedure'),
        ('AV', 'Amendment Voting Procedure'),
        ('RV', 'Resolution Voting Procedure'),
    ]
    active = models.BooleanField(default=True)
    custom_text = models.CharField(max_length=20, null=True, blank=True)
    voting_type = models.CharField(max_length=2, choices=VOTING_TYPE_CHOICES)
    committee = models.ForeignKey(Committee, on_delete=models.SET("Unknown"))
    in_favour = models.IntegerField(default=0)
    against = models.IntegerField(default=0)
    abstention = models.IntegerField(default=0)

    class Meta:
        ordering = ['voting_type']

    def __str__(self):
        if self.voting_type == "RV":
            return self.committee.name + " - " + self.get_voting_type_display()
        return self.committee.name + " - " + self.custom_text + "'s " + self.get_voting_type_display()


class CLIPStaff(models.Model):
    staffid = models.IntegerField()
    in_venue = models.BooleanField(default=False)

    class Meta:
        ordering = ['staffid']

    def __str__(self):
        return str(self.staffid)


class Type(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STAFF_TYPE_CHOICES = [
        ('SG', 'Secretary-General'),
        ('DS', 'Deputy Sec-General'),
        ('HL', 'Head of Logistics'),
        ('CL', 'Deputy Head Logistics'),
        ('CM', 'MUN Director'),
        ('MM', 'Media Manager'),
        ('HS', 'Head of Staff'),
        ('HE', 'Head of Press'),
        ('HM', 'Head of Media'),
        ('HH', 'Head of Hospitality'),
        ('HT', 'Head of Security'),
        ('SM', 'Systems Manager'),
        ('AS', 'Administrative Staff'),
        ('LG', 'Logistics'),
        ('PR', 'Press'),
        ('MD', 'Media'),
        ('HP', 'Hospitality'),
        ('SC', 'Security'),
        ('TP', 'Typist'),
        ('CA', 'Chair'),
        ('CC', 'Co-Chair'),
    ]

    CHAPERONE_TYPE_CHOICES = [
        ('MC', 'Main Chaperone'),
        ('SC', 'Secondary Chaperone'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    voting_id = models.CharField(default=random_id, editable=False, max_length=9, unique=True)
    ticket_type = models.ForeignKey(Type, on_delete=models.SET("Unknown"))
    name = models.CharField(max_length=20)
    school_name = models.ForeignKey(School, on_delete=models.SET("Unknown"), blank=True, default="", null=True)
    email = models.EmailField(blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, default="", null=True)
    committee = models.ForeignKey(Committee, on_delete=models.SET("Unknown"), blank=True, default="", null=True)
    staff_type = models.CharField(max_length=2, choices=STAFF_TYPE_CHOICES, null=True, blank=True)
    chaperone_type = models.CharField(max_length=2, choices=CHAPERONE_TYPE_CHOICES, null=True, blank=True)
    is_gdpr_allowed = models.BooleanField(default=False)
    medical_conditions = models.TextField(max_length=50, null=True, blank=True)
    dietary_restrictions = models.TextField(max_length=50, null=True, blank=True)
    has_registered = models.BooleanField(default=False)
    registered_datetime = models.CharField(max_length=30, blank=True, default="", null=True)
    registered_by = models.CharField(max_length=30, blank=True, default="", null=True)
    in_venue = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        permissions = (
            ("has_admin_access", "Has Admin Access"),
            ("has_voting_access", "Has Voting Access"),
            ("has_security_access", "Has Security Access"),
            ("has_registration_access", "Has Registration Access"),
        )

    def __str__(self):
        return self.name


class Voter(models.Model):
    voter = models.ForeignKey(Ticket, on_delete=models.SET("Unknown"))
    voting = models.ForeignKey(Voting, on_delete=models.SET("Unknown"))

    class Meta:
        ordering = ['voting_id']

    def __str__(self):
        return str(self.voting_id) + " - " + str(self.voter_id)


# @receiver(models.signals.post_save, sender=Ticket)
def execute_after_save(sender, instance, created, raw, using, update_fields, *args, **kwargs):
    if created:
        ID = instance.id
        qr = qrcode.QRCode(
            border=1,
        )
        qr.add_data(ID)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("/home/ubuntu/django/private_files/ticket-generation/qr-codes/" + str(ID) + ".png", format="PNG")
        if instance.ticket_type.id != settings.CUSTOM_GUEST_ID and instance.ticket_type.id != settings.CUSTOM_STAFF_ID:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            if instance.ticket_type.id == settings.CUSTOM_CHAPERONE_ID:
                template = "chaperone.html"
                context = {
                    'name': instance.name,
                    'school': instance.school_name,
                    'qrcode': img_str,
                    'id': instance.id
                }
            else:
                template = "delegate.html"
                if instance.school_name:
                    query = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                        id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(school_name=instance.school_name) & models.Q(
                        chaperone_type="MC"))
                    if query.count() == 0:
                        chaperone = "N/A"
                    else:
                        chaperone = query[0]
                else:
                    chaperone = "N/A"
                if instance.committee:
                    committee = instance.committee
                else:
                    committee = "N/A"
                if instance.country:
                    country = instance.country
                else:
                    country = "N/A"

                context = {
                    'name': instance.name,
                    'school': instance.school_name,
                    'chaperone': chaperone,
                    'committee': committee,
                    'country': country,
                    'qrcode': img_str,
                    'id': instance.id

                }

            html = render_to_string(template, context)
            with open("/home/ubuntu/django/private_files/ticket-generation/ticket-pdfs/" + str(ID) + ".pdf",
                      'wb+') as output:
                pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), output)


@receiver(models.signals.post_delete, sender=Ticket)
def execute_after_delete(sender, instance, using, *args, **kwargs):
    ID = instance.id
    if os.path.exists("/home/ubuntu/django/private_files/ticket-generation/qr-codes/" + str(ID) + ".png"):
        os.remove("/home/ubuntu/django/private_files/ticket-generation/qr-codes/" + str(ID) + ".png")
    if os.path.exists("/home/ubuntu/django/private_files/ticket-generation/ticket-pdfs/" + str(ID) + ".pdf"):
        os.remove("/home/ubuntu/django/private_files/ticket-generation/ticket-pdfs/" + str(ID) + ".pdf")
