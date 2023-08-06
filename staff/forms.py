from django import forms
from .models import Voting, Committee

COMMITTEE_CHOICES = [
    ('ECOSOC', 'ECOSOC'),
    ('HR', 'HR'),
    ('ICJ', 'ICJ'),
    ('SC', 'SC'),
    ('G20', 'G20'),
    ("STAFF", "STAFF"),
    ("CHAPERONE", "CHAPERONE"),
    ("GDPRiSAMS", "GDPRiSAMS"),
    ("GDPRFINAL", "GDPRFINAL"),
    ("GUESTS", "GUESTS"),
    ("VISITOR10", "VISITOR10"),
    ("VISITOR11", "VISITOR11"),
    ("VISITOR12", "VISITOR12"),
    ("VISITOR13", "VISITOR13"),
    ("VISITOR14", "VISITOR14"),
    ("VISITOR15", "VISITOR15"),
    ("VISITOR16", "VISITOR16"),
    ("VISITOR17", "VISITOR17"),
    ("VISITOR18", "VISITOR18"),
    ("VISITOR19", "VISITOR19"),
    ("VISITOR20", "VISITOR20"),
    ("VISITOR21", "VISITOR21"),
    ("VISITOR22", "VISITOR22"),
    ("VISITOR23", "VISITOR23"),
    ("VISITOR24", "VISITOR24"),
    ("VISITOR25", "VISITOR25"),
    ("VISITOR26", "VISITOR26"),
    ("VISITOR27", "VISITOR27"),
    ("VISITOR28", "VISITOR28"),
    ("VISITOR29", "VISITOR29"),
    ("VISITOR30", "VISITOR30"),
    ("CHAPERONE10", "CHAPERONE10"),
    ("CHAPERONE11", "CHAPERONE11"),
    ("CHAPERONE12", "CHAPERONE12"),
    ("CHAPERONE13", "CHAPERONE13"),
    ("CHAPERONE14", "CHAPERONE14"),
    ("CHAPERONE15", "CHAPERONE15"),
    ("CHAPERONE16", "CHAPERONE16"),
    ("CHAPERONE17", "CHAPERONE17"),
    ("CHAPERONE18", "CHAPERONE18"),
    ("CHAPERONE19", "CHAPERONE19"),
    ("CHAPERONE20", "CHAPERONE20"),
    ("CHAPERONE21", "CHAPERONE21"),
    ("CHAPERONE22", "CHAPERONE22"),
    ("CHAPERONE23", "CHAPERONE23"),
    ("CHAPERONE24", "CHAPERONE24"),
    ("CHAPERONE25", "CHAPERONE25"),
    ("CHAPERONE26", "CHAPERONE26"),
    ("CHAPERONE27", "CHAPERONE27"),
    ("CHAPERONE28", "CHAPERONE28"),
    ("CHAPERONE29", "CHAPERONE29"),
    ("CHAPERONE30", "CHAPERONE30"),
    ]

EXPORT_CHOICES = [
    ('BADGES', 'BADGES'),
    ('GDPRFORM', 'GDPRFORM'),
    ('DATABASE', 'DATABASE'),
    ]

ACCOUNT_CHOICES = [
    ('ACTIVATE', 'ACTIVATE'),
    ('DEACTIVATE', 'DEACTIVATE'),
    ]

VOTING_CHOICES = [
    ('CLAUSE', 'Clause Voting Procedure'),
    ('AMENDMENT', 'Amendment Voting Procedure'),
    ('RESOLUTION', 'Resolution Voting Procedure'),
    ]

COMMITTEE_ACTUAL_CHOICES = [
    ('ECOSOC', 'ECOSOC'),
    ('HR', 'HR'),
    ('ICJ', 'ICJ'),
    ('SC', 'SC'),
    ('G20', 'G20')
]

class ImportForm(forms.Form):
    committee = forms.CharField(label='Choose Option to Import', widget=forms.Select(choices=COMMITTEE_CHOICES))


class ExportForm(forms.Form):
    committee = forms.CharField(label='Choose File to Export', widget=forms.Select(choices=EXPORT_CHOICES))


class AccountForm(forms.Form):
    committee = forms.CharField(label='Choose Account Action', widget=forms.Select(choices=ACCOUNT_CHOICES))


class VotingForm(forms.Form):
    committee = forms.ModelChoiceField(label="Committee:", queryset=Committee.objects.all())
    type = forms.CharField(label='Voting Procedure Type:', widget=forms.Select(choices=Voting.VOTING_TYPE_CHOICES))
    custom_text = forms.CharField(label="Relevant Country:", max_length=30, required=False)
