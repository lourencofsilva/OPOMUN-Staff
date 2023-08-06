from django.shortcuts import render, redirect from django.db import models
from django.contrib.admin.views.decorators import staff_member_required,
user_passes_test from django.views.decorators.clickjacking import
xframe_options_exempt from .models import Ticket, execute_after_save,
Committee, CLIPStaff, Voting, Voter from .tests import run_tests,
test_mass_emails from datetime import datetime from .imports import
csv_import, csv_export, admin_accounts from .alerts import send_mass_emails,
send_slack_alert, send_one_email from .forms import ImportForm, ExportForm,
AccountForm, VotingForm import threading from django.conf import settings
import requests


def index(request):
    if request.user.has_perm("staff.has_voting_access"):
        voting = True
    else:
        voting = False
    context = {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "user": request.user, "voting": voting}
    return render(request, "staff/index.html", context)


@staff_member_required
def search(request):
    return render(request, "staff/search.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@staff_member_required
def registration_details(request, barcode):
    if not request.user.has_perm("staff.has_registration_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.has_registered:
            allowed = False
            message = "Ticket Name " + ticket_details.name + " tried using an already registered ticket with scanner of " + request.user.first_name + " " + request.user.last_name + "."
            send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
            send_alert_thread.start()
        else:
            if (ticket_details.ticket_type.id == settings.CUSTOM_GUEST_ID or ticket_details.ticket_type.id == settings.CUSTOM_STAFF_ID) and not request.user.has_perm("staff.is_adminteam"):
                return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
            allowed = True
            ticket_details.has_registered = True
            ticket_details.registered_by = request.user.first_name + " " + request.user.last_name
            ticket_details.registered_datetime = datetime.now().strftime("%d/%m/%y %H:%M:%S")
            ticket_details.save()
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": False, 'allowed': allowed, 'register': True})
    except:
        message = "An invalid ticket was scanned with scanner of " + request.user.first_name + " " + request.user.last_name + "."
        send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
        send_alert_thread.start()
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": False, 'register': True})


@staff_member_required
def get_details(request, barcode):
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.school_name:
            query = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(school_name=ticket_details.school_name) & models.Q(
                chaperone_type="MC"))
            if query.count() == 0:
                chaperone = None
            else:
                chaperone = query[0]
        else:
            chaperone = None
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "details": True, 'chaperone': chaperone})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": True})


@staff_member_required
def conditions_details(request, barcode):
    if not request.user.has_perm("staff.has_admin_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "conditions": True})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "conditions": True})


@staff_member_required
def dbdetails(request, barcode):
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.school_name:
            query = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(school_name=ticket_details.school_name) & models.Q(
                chaperone_type="MC"))
            if query.count() == 0:
                chaperone = None
            else:
                chaperone = query[0]
        else:
            chaperone = None
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "details": True, "search": True, 'chaperone': chaperone})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": True, "search": True})


@staff_member_required
def security_entry(request, barcode):
    if not request.user.has_perm("staff.has_security_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    try:
        if len(barcode) == 3 or len(barcode) == 4:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'}
            url = "REDACTED" + barcode + ".jpg"
            if requests.get(url, headers=headers).status_code == 200:
                try:
                    query = CLIPStaff.objects.get(staffid=barcode)
                    query.in_venue = True
                    query.save()
                except:
                    CLIPStaff.objects.create(staffid=barcode, in_venue=True)
                return render(request, "staff/ticket_details.html",
                              {"ticket": True, "superuser": request.user.is_superuser,
                               "authenticated": request.user.is_authenticated, "allowed": True, "security": True,
                               "security_type": "Entry",
                               'registered': True, 'clipstaff': True, "url": url})
            else:
                return render(request, "staff/ticket_details.html",
                              {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                               "security": True, 'security_type': "Entry", 'clipstaff': True})
        ticket_details = Ticket.objects.get(id=barcode)
        floor = None
        if ticket_details.has_registered:
            registered = True
            if ticket_details.in_venue:
                security_allowed = False
                message = "Ticket Name " + ticket_details.name + " tried entering venue with ticket already inside venue with scanner of " + request.user.first_name + " " + request.user.last_name + "."
                send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
                send_alert_thread.start()
            else:
                if not str(ticket_details.ticket_type) == "Staff" and not str(ticket_details.ticket_type) == "Chaperone" and not str(ticket_details.ticket_type) == "Guest":
                    floor = None
                    date = str(datetime.now().strftime("%d"))
                    time = int(datetime.now().strftime("%H"))
                    if date == "21" and time < 19:
                        if str(ticket_details.committee.name) == "ICJ":
                            floor = "4"
                        elif str(ticket_details.committee.name) == "HR":
                            floor = "0"
                        elif str(ticket_details.committee.name) == "SC" or str(ticket_details.committee.name) == "ECOSOC" or str(ticket_details.committee.name) == "G20":
                            floor = "-1"
                        else:
                            floor = None
                    elif date == "22":
                        if str(ticket_details.committee.name) == "ICJ":
                            floor = "4"
                        elif str(ticket_details.committee.name) == "HR" or str(ticket_details.committee.name) == "ECOSOC":
                            floor = "0"
                        elif str(ticket_details.committee.name) == "SC" or str(ticket_details.committee.name) == "G20":
                            floor = "-1"
                        else:
                            floor = None
                security_allowed = True
                ticket_details.in_venue = True
                ticket_details.save()
        else:
            security_allowed = False
            registered = False
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "security": True, "security_type": "Entry", 'security_allowed': security_allowed, 'registered': registered, 'floor': floor})
    except Exception as e:
        message = str(e)
        send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
        send_alert_thread.start()
        message = "An invalid ticket was scanned with scanner of " + request.user.first_name + " " + request.user.last_name + "."
        send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
        send_alert_thread.start()
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "security": True, 'security_type': "Entry"})


@staff_member_required
def security_exit(request, barcode):
    if not request.user.has_perm("staff.has_security_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    try:
        if len(barcode) == 3 or len(barcode) == 4:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'}
            url = "REDACTED" + barcode + ".jpg"
            if requests.get(url, headers=headers).status_code == 200:
                try:
                    query = CLIPStaff.objects.get(staffid=barcode)
                    query.in_venue = False
                    query.save()
                except:
                    CLIPStaff.objects.create(staffid=barcode, in_venue=False)
                return render(request, "staff/ticket_details.html",
                              {"ticket": True, "superuser": request.user.is_superuser,
                               "authenticated": request.user.is_authenticated, "allowed": True, "security": True,
                               "security_type": "Exit",
                               'registered': True, 'clipstaff': True, "url": url})
            else:
                return render(request, "staff/ticket_details.html",
                              {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                               "security": True, 'security_type': "Exit", 'clipstaff': True})
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.has_registered:
            registered = True
            if ticket_details.in_venue:
                security_allowed = True
                ticket_details.in_venue = False
                ticket_details.save()
            else:
                security_allowed = False
                message = "Ticket Name " + ticket_details.name + " tried exiting venue with ticket already outside venue with scanner of " + request.user.first_name + " " + request.user.last_name + "."
                send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
                send_alert_thread.start()
        else:
            security_allowed = False
            registered = False
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "security": True, "security_type": "Exit", 'security_allowed': security_allowed, 'registered': registered})
    except:
        message = "An invalid ticket was scanned with scanner of " + request.user.first_name + " " + request.user.last_name + "."
        send_alert_thread = threading.Thread(target=send_slack_alert, args=(message,))
        send_alert_thread.start()
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "security": True, "security_type": "Exit"})


@staff_member_required
def security_scanner_entry(request):
    if not request.user.has_perm("staff.has_security_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    header = "ENTRY Security"
    redirectbasedir = "security-entry-details"
    return render(request, "staff/scanner.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "header": header, "redirectbasedir": redirectbasedir})


@staff_member_required
def security_scanner_exit(request):
    if not request.user.has_perm("staff.has_security_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    header = "EXIT Security"
    redirectbasedir = "security-exit-details"
    return render(request, "staff/scanner.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "header": header, "redirectbasedir": redirectbasedir})


@staff_member_required
def scanner_choice(request):
    if request.user.has_perm("staff.has_registration_access"):
        hospitality = True
    else:
        hospitality = False
    if request.user.has_perm("staff.has_security_access"):
        security = True
    else:
        security = False
    if request.user.has_perm("staff.has_admin_access"):
        admin = True
    else:
        admin = False
    return render(request, "staff/scanner_chooser.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "security": security, "hospitality": hospitality, "admin": admin})


@staff_member_required
def registration_scanner(request):
    if not request.user.has_perm("staff.has_registration_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    header = "Registration"
    redirectbasedir = "registration-details"
    return render(request, "staff/scanner.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "header": header, "redirectbasedir": redirectbasedir})


@staff_member_required
def details_scanner(request):
    header = "Details"
    redirectbasedir = "get-details"
    return render(request, "staff/scanner.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "header": header, "redirectbasedir": redirectbasedir})


@staff_member_required
def conditions_scanner(request):
    if not request.user.has_perm("staff.has_admin_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})
    header = "Conditions"
    redirectbasedir = "conditions-details"
    return render(request, "staff/scanner.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "header": header, "redirectbasedir": redirectbasedir})


@staff_member_required
def dbsearch(request, query):
    queryanswer = Ticket.objects.filter(name__icontains=query)
    if queryanswer.exists():
        exists = True
    else:
        exists = False
    return render(request, "staff/dbsearch.html",
                  {"queryanswer": queryanswer, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "exists": exists})


@user_passes_test(lambda u: u.is_superuser)
def admin_tools(request):
    return render(request, "staff/admin_tools.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_count_reset_confirmation(request):
    return render(request, "staff/admin_count_reset_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_count_reset(request):
    queryset1 = Ticket.objects.all()
    queryset2 = CLIPStaff.objects.all()
    for ticket in queryset1:
        ticket.in_venue = False
        ticket.save()
    for ticket in queryset2:
        ticket.in_venue = False
        ticket.save()
    return render(request, "staff/admin_count_reset.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_regenerate_confirmation(request):
    return render(request, "staff/admin_regenerate_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_regenerate(request):
    queryset = Ticket.objects.all()
    for ticket in queryset:
        execute_after_save(Ticket, ticket, True, True, None, None)
    return render(request, "staff/admin_regenerate.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_register(request):
    queryanswer = Ticket.objects.filter(models.Q(ticket_type=settings.CUSTOM_GUEST_ID) | models.Q(ticket_type=settings.CUSTOM_STAFF_ID))
    if queryanswer.exists():
        exists = True
    else:
        exists = False
    return render(request, "staff/admin_register.html",
                  {"queryanswer": queryanswer, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "exists": exists})


@user_passes_test(lambda u: u.is_superuser)
def unregistration_details(request, barcode):
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        allowed = True
        ticket_details.has_registered = False
        ticket_details.registered_by = ""
        ticket_details.registered_datetime = ""
        ticket_details.save()
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": False, 'allowed': allowed, 'register': False})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": False, 'register': False})


@staff_member_required
def statistics(request):
    return render(request, "staff/statistics.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@staff_member_required
def statistics_in_venue(request):
    registered_count = 0
    in_venue_count = 0
    for ticket in Ticket.objects.all():
        if ticket.has_registered:
            registered_count += 1
        if ticket.in_venue:
            in_venue_count += 1
    for staff in CLIPStaff.objects.all():
        registered_count += 1
        if staff.in_venue:
            in_venue_count += 1
    people_in_venue = str(in_venue_count) + " / " + str(registered_count)
    queryanswer1 = Ticket.objects.filter(in_venue=True)
    queryanswer2 = CLIPStaff.objects.filter(in_venue=True)
    if queryanswer1.exists() or queryanswer2.exists():
        exists = True
    else:
        exists = False
    return render(request, "staff/statistics_in_venue.html",
                  {"queryanswer1": queryanswer1, "queryanswer2": queryanswer2, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "exists": exists, "people_in_venue": people_in_venue})


@staff_member_required
def statistics_in_venue_details(request, barcode):
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.school_name:
            query = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(school_name=ticket_details.school_name) & models.Q(
                chaperone_type="MC"))
            if query.count() == 0:
                chaperone = None
            else:
                chaperone = query[0]
        else:
            chaperone = None
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "details": True, 'chaperone': chaperone, 'in_venue': True})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": True, 'in_venue': True})


@staff_member_required
def statistics_by_committee(request):
    queryanswer = Committee.objects.all()
    if queryanswer.exists():
        exists = True
    else:
        exists = False
    return render(request, "staff/statistics_by_committee.html",
                  {"queryanswer": queryanswer, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "exists": exists})


@staff_member_required
def statistics_by_committee_details(request, id):
    queryanswer = Ticket.objects.filter(models.Q(committee_id=id) & models.Q(has_registered=True))
    committee = Committee.objects.get(id=id)
    if queryanswer.exists():
        exists = True
    else:
        exists = False
    return render(request, "staff/statistics_by_committee_details.html",
                  {"queryanswer": queryanswer, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "exists": exists, "committee": committee.name})


@staff_member_required
def statistics_by_committee_barcode_details(request, barcode):
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.school_name:
            query = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(school_name=ticket_details.school_name) & models.Q(
                chaperone_type="MC"))
            if query.count() == 0:
                chaperone = None
            else:
                chaperone = query[0]
        else:
            chaperone = None
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "details": True, 'chaperone': chaperone, 'by_committee': True})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": True, 'by_committee': True})


@staff_member_required
def statistics_not_registered(request):
    registered_count = 0
    total_count = 0
    for ticket in Ticket.objects.all():
        total_count += 1
        if not ticket.has_registered:
            registered_count += 1
    not_registered_count = str(registered_count) + " / " + str(total_count)
    queryanswer = Ticket.objects.filter(has_registered=False)
    if queryanswer.exists():
        exists = True
    else:
        exists = False
    return render(request, "staff/statistics_not_registered.html",
                  {"queryanswer": queryanswer, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "exists": exists, "not_registered_count": not_registered_count})


@staff_member_required
def statistics_get_help(request):
    return render(request, "staff/statistics_get_help.html",
                  {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@staff_member_required
def statistics_not_registered_details(request, barcode):
    try:
        ticket_details = Ticket.objects.get(id=barcode)
        if ticket_details.school_name:
            query = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(
                id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(school_name=ticket_details.school_name) & models.Q(
                chaperone_type="MC"))
            if query.count() == 0:
                chaperone = None
            else:
                chaperone = query[0]
        else:
            chaperone = None
        return render(request, "staff/ticket_details.html",
                      {"ticket": ticket_details, "superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "allowed": True, "details": True, 'chaperone': chaperone, 'statistics_not_registered': True})
    except:
        return render(request, "staff/ticket_details.html",
                      {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "details": True, 'statistics_not_registered': True})


@user_passes_test(lambda u: u.is_superuser)
def admin_badge_export(request):
    erroroutput = csv_export()
    return render(request, "staff/admin_badge_export.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'erroroutput': erroroutput})


@user_passes_test(lambda u: u.is_superuser)
def admin_database_check_confirmation(request):
    return render(request, "staff/admin_database_check_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_database_check(request):
    erroroutput = run_tests()
    return render(request, "staff/admin_database_check.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'erroroutput': erroroutput})


@user_passes_test(lambda u: u.is_superuser)
def admin_database_import_confirmation(request):
    if request.method == "POST":
        form = ImportForm(request.POST)
        if form.is_valid():
            filename = form.cleaned_data['committee']
            erroroutput = csv_import(filename)
            return render(request, "staff/admin_database_import.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'erroroutput': erroroutput})
        else:
            return render(request, "staff/admin_database_import_confirmation.html",
                          {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                           'form': form})
    else:
        form = ImportForm()
        return render(request, "staff/admin_database_import_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_badge_export_confirmation(request):
    if request.method == "POST":
        form = ImportForm(request.POST)
        if form.is_valid():
            filename = form.cleaned_data['committee']
            erroroutput = csv_export(filename)
            return render(request, "staff/admin_badge_export.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'erroroutput': erroroutput})
        else:
            return render(request, "staff/admin_badge_export_confirmation.html",
                          {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                           'form': form})
    else:
        form = ExportForm()
        return render(request, "staff/admin_badge_export_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'form': form})


@user_passes_test(lambda u: u.is_superuser)
def admin_email_send_confirmation(request):
    return render(request, "staff/admin_email_send_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_email_send(request):
    erroroutput = send_one_email()
    return render(request, "staff/admin_email_send.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'erroroutput': erroroutput})


def locked_out(request):
    return render(request, "staff/lockedout.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})


@user_passes_test(lambda u: u.is_superuser)
def admin_accounts_confirmation(request):
    if request.method == "POST":
        form = ImportForm(request.POST)
        if form.is_valid():
            filename = form.cleaned_data['committee']
            erroroutput = admin_accounts(filename)
            return render(request, "staff/admin_accounts.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'erroroutput': erroroutput})
        else:
            return render(request, "staff/admin_accounts_confirmation.html",
                          {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                           'form': form})
    else:
        form = AccountForm()
        return render(request, "staff/admin_accounts_confirmation.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'form': form})


@staff_member_required
def schedules(request):
    context = {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "user": request.user}
    return render(request, "staff/schedules.html", context)


@staff_member_required()
def voting_management(request):
    if not request.user.has_perm("staff.has_voting_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})

    context = {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "user": request.user}
    return render(request, "staff/voting_management.html", context)


@staff_member_required()
def create_vote(request):
    if not request.user.has_perm("staff.has_voting_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})

    if request.method == "POST":
        form = VotingForm(request.POST)
        if form.is_valid():
            committee = form.cleaned_data['committee']
            type = form.cleaned_data['type']
            custom_text = form.cleaned_data['custom_text']

            if type != "RV" and custom_text == "" or custom_text == " ":
                return render(request, "staff/create_vote.html",
                              {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                               'form': form, "error": True, "error1": True})

            for Vote in Voting.objects.filter(committee=committee):
                if Vote.active:
                    return render(request, "staff/create_vote.html",
                                  {"superuser": request.user.is_superuser,
                                   "authenticated": request.user.is_authenticated,
                                   'form': form, "error": True, "error3": True})

            if type == "RV":
                if Voting.objects.filter(voting_type=type, committee=committee).exists():
                    return render(request, "staff/create_vote.html",
                                  {"superuser": request.user.is_superuser,
                                   "authenticated": request.user.is_authenticated,
                                   'form': form, "error": True, "error2": True})
                voting = Voting.objects.create(voting_type=type, committee=committee)
            else:
                if Voting.objects.filter(voting_type=type, committee=committee, custom_text=custom_text, active=True).exists():
                    return render(request, "staff/create_vote.html",
                                  {"superuser": request.user.is_superuser,
                                   "authenticated": request.user.is_authenticated,
                                   'form': form, "error": True, "error2": True})
                voting = Voting.objects.create(voting_type=type, committee=committee, custom_text=custom_text)
            return redirect('/manage-vote-id/' + str(committee.id) + '/')
        else:
            return render(request, "staff/create_vote.html",
                          {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated,
                           'form': form, "error": True})
    else:
        form = VotingForm()
        return render(request, "staff/create_vote.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, 'form': form})


@staff_member_required()
def manage_vote(request):
    if not request.user.has_perm("staff.has_voting_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})

    committees = Committee.objects.all()
    remove = []
    for committee in committees:
        vote_to_search = Voting.objects.filter(committee=committee)
        active = False
        for Vote in vote_to_search:
            if Vote.active:
                active = True
        if not active:
            remove.append(committee.id)

    context = {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "user": request.user, "committeees": committees, "remove": remove}
    return render(request, "staff/manage_vote.html", context)


@staff_member_required()
def manage_vote_id(request, id):
    if not request.user.has_perm("staff.has_voting_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})

    vote_to_search = Voting.objects.filter(committee=Committee.objects.get(id=id))
    for Vote in vote_to_search:
        if Vote.active:
            voting = Vote

    votes_submitted = voting.in_favour + voting.against + voting.abstention
    voters_available = Ticket.objects.filter(committee_id=id).count()

    context = {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "user": request.user, "voting": voting, "votes_submitted": votes_submitted, "voters_available": voters_available}
    return render(request, "staff/manage_vote_id.html", context)


@staff_member_required()
def end_voting(request, id):
    if not request.user.has_perm("staff.has_voting_access"):
        return render(request, "403.html", {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated})

    if Voting.objects.filter(id=id).exists():
        voting_active = Voting.objects.get(id=id)
        voting_active.active = False
        voting_active.save()

    context = {"superuser": request.user.is_superuser, "authenticated": request.user.is_authenticated, "user": request.user}
    return render(request, "staff/end_voting.html", context)


@xframe_options_exempt
def frontend_index(request):
    remove = request.GET.get("remove", None)

    if remove == "true":
        response = render(request, "staff/frontend_index.html")
        response.set_cookie(key='voting_id', value="", secure=True, max_age=604800)
        response.delete_cookie("voting_id")
        return response

    cookie = request.COOKIES.get("voting_id")
    if cookie is None or cookie == "":
        return render(request, "staff/frontend_index.html")

    return redirect("/frontend/vote?auth=" + cookie)


@xframe_options_exempt
def frontend_vote(request):
    auth = request.GET.get("auth", None)
    decision = request.GET.get("decision", None)

    if decision is not None:
        voter = Ticket.objects.get(voting_id=auth)
        vote = Voting.objects.get(committee=voter.committee, active=True)

        if Voter.objects.filter(voter=voter, voting=vote).exists() or (decision == "abstention" and vote.voting_type == "RV"):
            raise Exception

        if decision == "favour":
            vote.in_favour += 1
        elif decision == "against":
            vote.against += 1
        elif decision == "abstention":
            vote.abstention += 1
        vote.save()

        Voter.objects.create(voter=voter, voting=vote)

        context = {"error3": True, "name": voter.name, "vote": vote}
        return render(request, "staff/frontend_vote.html", context)

    try:
        voter = Ticket.objects.get(voting_id=auth)
    except Ticket.DoesNotExist:
        context = {"alert": True}
        return render(request, "staff/frontend_index.html", context)

    if Voting.objects.filter(committee=voter.committee, active=True).exists():
        vote = Voting.objects.get(committee=voter.committee, active=True)
        if Voter.objects.filter(voter=voter, voting=vote).exists():
            context = {"error2": True, "name": voter.name, "vote": vote}
        else:
            context = {"name": voter.name, "vote": vote, "auth": auth}
    else:
        context = {"error1": True, "name": voter.name}

    response = render(request, "staff/frontend_vote.html", context)
    response.set_cookie(key='voting_id', value=auth, secure=True, max_age=604800)
    return response
