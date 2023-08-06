from .models import School, Committee, Type, Ticket
from django.conf import settings
from django.db import models
import csv
from django.core.validators import validate_email
import warnings
from .tests import run_tests
from datetime import datetime
from django.contrib.auth.models import User


def admin_accounts(name):
    if name == "DEACTIVATE":
        return admin_accounts_deactivate()
    try:
        erroroutput = []
        queryset = User.objects.filter(~models.Q(id=1) & ~models.Q(id=2) & ~models.Q(id=40))
        for user in queryset:
            user.is_active = True
            user.save()
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def admin_accounts_deactivate():
    try:
        erroroutput = []
        queryset = User.objects.filter(~models.Q(id=1) & ~models.Q(id=2) & ~models.Q(id=40))
        for user in queryset:
            user.is_active = False
            user.save()
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_import(name):
    if name == "STAFF":
        return csv_import_staff()
    if name == "CHAPERONE":
        return csv_import_chaperone()
    if name == "GDPRiSAMS":
        return csv_import_gdprisams()
    if name == "GDPRFINAL":
        return csv_import_gdprfinal()
    if name == "GUESTS":
        return csv_import_guests()
    if "VISITOR" in name:
        return create_visitors(name)
    if "CHAPERONE" in name:
        return create_chaperones(name)
    try:
        first = True
        saved = 0
        erroroutput = []
        with open('/home/ubuntu/django/private_files/imports/' + name + '.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            committee = name
            committee = Committee.objects.get(name=committee)
            ticket_type = Type.objects.get(id=settings.CUSTOM_DELEGATE_ID)
            for row in reader:
                if not first:
                    error = False
                    external = False
                    country = row[0]
                    name = row[1].strip()
                    name = name.replace("?", "")
                    name = " ".join(name.split())
                    name = name.title()
                    school = row[2]
                    email = row[3]
                    queryset = Ticket.objects.filter(name=name, ticket_type=ticket_type)
                    if queryset.exists():
                        error = True
                        erroroutput.append(name + " is a possible duplicate. Save Manually")
                    if country == "" or country == " ":
                        country = "N/A"
                    if name == "" or name == " ":
                        error = True
                        erroroutput.append(country + " has no name.")
                    if school == "" or school == " ":
                        school = School.objects.get(name="External")
                        external = True
                    else:
                        try:
                            school = School.objects.get(name=school)
                        except:
                            error = True
                            erroroutput.append(name + " school does not match database.")
                    if external:
                        if email == "" or email == " ":
                            error = True
                            erroroutput.append(name + " is external but has no email.")
                        else:
                            try:
                                validate_email(email)
                            except:
                                error = True
                                erroroutput.append(name + " has invalid email.")
                    else:
                        if not email == "" and not email == " ":
                            try:
                                validate_email(email)
                            except:
                                error = True
                                erroroutput.append(name + " has invalid email.")
                            save_email = True
                        else:
                            save_email = False
                    if not error:
                        if external:
                            Ticket.objects.create(ticket_type=ticket_type, name=name, school_name=school, email=email, country=country, committee=committee)
                        else:
                            if save_email:
                                Ticket.objects.create(ticket_type=ticket_type, name=name, school_name=school, email=email, country=country, committee=committee)
                            else:
                                Ticket.objects.create(ticket_type=ticket_type, name=name, school_name=school, country=country, committee=committee)
                        saved += 1
                first = False
            erroroutput.append(str(saved) + " delegates were saved successfully, for committee " + str(committee))
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_export(filename):
    if filename == "GDPRFORM":
        return csv_export_gdpr()
    if filename == "DATABASE":
        return csv_export_database()
    result = run_tests()
    erroroutput = []
    written = 0
    if result is not None:
        erroroutput.append("Database Checks Failed")
        for i in erroroutput:
            warnings.warn(i, Warning)
        return erroroutput
    try:
        first = True
        datetimenow = datetime.now().strftime("%d-%m--%H-%M")
        filename1 = '/home/ubuntu/django/private_files/exports/non-staff' + datetimenow + '.csv'
        filename2 = '/home/ubuntu/django/private_files/exports/staff' + datetimenow + '.csv'
        graphicsdir = "REDACTED/badge_export/imports/graphics/"
        qrdir = "REDACTED/Desktop/badge_export/imports/qr_codes/"
        with open(filename1, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for ticket in Ticket.objects.all():
                if ticket.is_gdpr_allowed:
                    topgraphic = graphicsdir + "gdpr.png"
                else:
                    topgraphic = graphicsdir + "nongdpr.png"
                if first:
                    writer.writerow(["Name"] + ["Type"] + ["Subtype"] + ["@Logographic"] + ["@Topgraphic"] + ["@Bottomgraphic"] + ["@QR"] + ["#Visibility"])
                    first = False
                    if ticket.ticket_type.id == settings.CUSTOM_DELEGATE_ID:
                        name = ticket.name
                        type = "DELEGATE"
                        subtype = ticket.country
                        logographics = graphicsdir + str(ticket.committee) + "logo.png"
                        bottomgraphics = graphicsdir + str(ticket.committee) + "bottom.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        writer.writerow(
                            [name] + [type] + [subtype] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                qr] + ["True"])
                    if ticket.ticket_type.id == settings.CUSTOM_CHAPERONE_ID:
                        name = ticket.name
                        type = "CHAPERONE"
                        subtype = ticket.school_name
                        logographics = graphicsdir + "Logo.png"
                        bottomgraphics = graphicsdir + "chaperonebottom.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        writer.writerow(
                            [name] + [type] + [subtype] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                qr] + ["True"])
                    if ticket.ticket_type.id == settings.CUSTOM_GUEST_ID:
                        name = ticket.name
                        type = "GUEST"
                        logographics = graphicsdir + "Logo.png"
                        bottomgraphics = graphicsdir + "guestbottom.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        if ticket.country:
                            writer.writerow(
                                [name] + [type] + [ticket.country] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                    qr] + ["True"])
                        else:
                            writer.writerow(
                                [name] + [type] + [""] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                    qr] + ["False"])
                else:
                    if ticket.ticket_type.id == settings.CUSTOM_DELEGATE_ID:
                        name = ticket.name
                        type = "DELEGATE"
                        subtype = ticket.country
                        logographics = graphicsdir + str(ticket.committee) + "logo.png"
                        bottomgraphics = graphicsdir + str(ticket.committee) + "bottom.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        writer.writerow(
                            [name] + [type] + [subtype] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                qr] + ["True"])
                    if ticket.ticket_type.id == settings.CUSTOM_CHAPERONE_ID:
                        name = ticket.name
                        type = "CHAPERONE"
                        subtype = ticket.school_name
                        logographics = graphicsdir + "Logo.png"
                        bottomgraphics = graphicsdir + "chaperonebottom.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        writer.writerow(
                            [name] + [type] + [subtype] + [logographics] + [topgraphic] + [bottomgraphics] + [qr] + ["True"])
                    if ticket.ticket_type.id == settings.CUSTOM_GUEST_ID:
                        name = ticket.name
                        type = "GUEST"
                        logographics = graphicsdir + "Logo.png"
                        bottomgraphics = graphicsdir + "guestbottom.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        if ticket.country:
                            writer.writerow(
                                [name] + [type] + [ticket.country] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                    qr] + ["True"])
                        else:
                            writer.writerow(
                                [name] + [type] + [""] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                    qr] + ["False"])
        first = True
        with open(filename2, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for ticket in Ticket.objects.all():
                if ticket.is_gdpr_allowed:
                    topgraphic = graphicsdir + "gdpr.png"
                else:
                    topgraphic = graphicsdir + "nongdpr.png"
                if first:
                    writer.writerow(["Name"] + ["Type"] + ["Subtype"] + ["@Logographic"] + ["@Topgraphic"] + ["@Bottomgraphic"] + ["@QR"] + ["#Visibility"])
                    first = False
                    if ticket.ticket_type.id == settings.CUSTOM_STAFF_ID:
                        name = ticket.name
                        if ticket.staff_type == "SG" or ticket.staff_type == "DS" or ticket.staff_type == "HL" or ticket.staff_type == "CL" or ticket.staff_type == "HS":
                            type = "EXEC. TEAM"
                            bottomgraphics = graphicsdir + "execteambottom.png"
                        else:
                            type = "STAFF"
                            bottomgraphics = graphicsdir + "staffbottom.png"
                        if ticket.staff_type == "CM" or ticket.staff_type == "MM":
                            bottomgraphics = graphicsdir + "seniorstaffbottom.png"
                        if ticket.staff_type == "MD" or ticket.staff_type == "PR" or ticket.staff_type == "HE" or ticket.staff_type == "HM":
                            bottomgraphics = graphicsdir + "mediapressbottom.png"

                        subtype = ticket.get_staff_type_display()
                        logographics = graphicsdir + "Logoblack.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        writer.writerow(
                            [name] + [type] + [subtype] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                qr] + ["True"])
                else:
                    if ticket.ticket_type.id == settings.CUSTOM_STAFF_ID:
                        name = ticket.name
                        if ticket.staff_type == "SG" or ticket.staff_type == "DS" or ticket.staff_type == "HL" or ticket.staff_type == "CL" or ticket.staff_type == "HS":
                            type = "EXEC. TEAM"
                            bottomgraphics = graphicsdir + "execteambottom.png"
                        else:
                            type = "STAFF"
                            bottomgraphics = graphicsdir + "staffbottom.png"
                        if ticket.staff_type == "CM" or ticket.staff_type == "MM":
                            bottomgraphics = graphicsdir + "seniorstaffbottom.png"
                        if ticket.staff_type == "MD" or ticket.staff_type == "PR" or ticket.staff_type == "HE" or ticket.staff_type == "HM":
                            bottomgraphics = graphicsdir + "mediapressbottom.png"
                        if ticket.staff_type == "CA" or ticket.staff_type == "CC" or ticket.staff_type == "TP":
                            bottomgraphics = graphicsdir + "execteambottom.png"
                        subtype = ticket.get_staff_type_display()
                        logographics = graphicsdir + "Logoblack.png"
                        qr = qrdir + str(ticket.id) + ".png"
                        written += 1
                        writer.writerow(
                            [name] + [type] + [subtype] + [logographics] + [topgraphic] + [bottomgraphics] + [
                                qr] + ["True"])
        erroroutput.append(str(written) + " tickets were written successfully to csv " + filename)
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_export_gdpr():
    result = run_tests()
    erroroutput = []
    written = 0
    if result is not None:
        erroroutput.append("Database Checks Failed")
        for i in erroroutput:
            warnings.warn(i, Warning)
        return erroroutput
    try:
        first = True
        datetimenow = datetime.now().strftime("%d-%m--%H-%M")
        filename = '/home/ubuntu/django/private_files/exports/gdpr' + datetimenow + '.csv'
        with open(filename, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for ticket in Ticket.objects.filter(models.Q(ticket_type=settings.CUSTOM_DELEGATE_ID) | models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID)):
                if first:
                    writer.writerow(["ID"] + ["Type"] + ["Name"] + ["School"] + ["GDPR Allowed?"] + ["Dietary Restrictions"] + ["Medical Conditions"])
                    first = False
                    id = ticket.id
                    name = ticket.name
                    school = ticket.school_name
                    gdpr_status = ""
                    dietary = ticket.dietary_restrictions
                    medical = ticket.medical_conditions
                    ticket_type = ticket.ticket_type
                    written += 1
                    writer.writerow(
                        [id] + [ticket_type] + [name] + [school] + [gdpr_status] + [dietary] + [medical])
                else:
                    id = ticket.id
                    name = ticket.name
                    school = ticket.school_name
                    gdpr_status = ""
                    dietary = ticket.dietary_restrictions
                    medical = ticket.medical_conditions
                    ticket_type = ticket.ticket_type
                    written += 1
                    writer.writerow(
                        [id] + [ticket_type] + [name] + [school] + [gdpr_status] + [dietary] + [medical])
        erroroutput.append(str(written) + " tickets were written successfully to csv " + filename)
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_export_database():
    result = run_tests()
    erroroutput = []
    written = 0
    if result is not None:
        erroroutput.append("Database Checks Failed")
        for i in erroroutput:
            warnings.warn(i, Warning)
        return erroroutput
    try:
        first = True
        datetimenow = datetime.now().strftime("%d-%m--%H-%M")
        filename = '/home/ubuntu/django/private_files/exports/database' + datetimenow + '.csv'
        with open(filename, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for ticket in Ticket.objects.all():
                if first:
                    writer.writerow(["ID"] + ["Type"] + ["Name"] + ["School"] + ["Committee"] + ["Country"] + ["GDPR Allowed?"] + ["Staff Type"] + ["Dietary Restrictions"] + ["Medical Conditions"] + ["Has Registered"] + ["Registered By"] + ["Registered On"])
                    first = False
                    id = ticket.id
                    name = ticket.name
                    school = ticket.school_name
                    if ticket.is_gdpr_allowed:
                        gdpr_status = "TRUE"
                    else:
                        gdpr_status = "FALSE"
                    dietary = ticket.dietary_restrictions
                    medical = ticket.medical_conditions
                    ticket_type = ticket.ticket_type
                    committee = ticket.committee
                    country = ticket.country
                    staff_type = ticket.get_staff_type_display()
                    has_registered = ticket.has_registered
                    registered_by = ticket.registered_by
                    registered_on = ticket.registered_datetime
                    written += 1
                    writer.writerow(
                        [id] + [ticket_type] + [name] + [school] + [committee] + [country] + [gdpr_status] + [
                            staff_type] + [dietary] + [medical] + [has_registered] + [registered_by] + [registered_on])
                else:
                    id = ticket.id
                    name = ticket.name
                    school = ticket.school_name
                    if ticket.is_gdpr_allowed:
                        gdpr_status = "TRUE"
                    else:
                        gdpr_status = "FALSE"
                    dietary = ticket.dietary_restrictions
                    medical = ticket.medical_conditions
                    ticket_type = ticket.ticket_type
                    committee = ticket.committee
                    country = ticket.country
                    staff_type = ticket.get_staff_type_display()
                    has_registered = ticket.has_registered
                    registered_by = ticket.registered_by
                    registered_on = ticket.registered_datetime
                    written += 1
                    writer.writerow(
                        [id] + [ticket_type] + [name] + [school] + [committee] + [country] + [gdpr_status] + [staff_type] + [dietary] + [medical] + [has_registered] + [registered_by] + [registered_on])
            delegates = Ticket.objects.filter(ticket_type_id=settings.CUSTOM_DELEGATE_ID).count()
            chaperones = Ticket.objects.filter(ticket_type_id=settings.CUSTOM_CHAPERONE_ID).count()
            staff = Ticket.objects.filter(ticket_type_id=settings.CUSTOM_STAFF_ID).count()
            guests = Ticket.objects.filter(ticket_type_id=settings.CUSTOM_GUEST_ID).count()
            writer.writerow(
                ["END"] + ["END"] + ["Delegate Count:"] + [delegates] + ["Chaperone Count:"] + [chaperones] + ["Staff Count:"] + [staff] + ["Guest Count:"] + [guests] + ["END"] + ["END"] + ["END"])
        erroroutput.append(str(written) + " tickets were written successfully to csv " + filename)
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_import_staff():
    try:
        first = True
        saved = 0
        erroroutput = []
        with open('/home/ubuntu/django/private_files/imports/staff.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            ticket_type = Type.objects.get(id=settings.CUSTOM_STAFF_ID)
            for row in reader:
                if not first:
                    error = False
                    name = row[0].strip()
                    name = name.replace("?", "")
                    name = " ".join(name.split())
                    name = name.title()
                    position = row[1]
                    gdpr = row[3]
                    if gdpr == "TRUE":
                        gdpr = True
                    elif gdpr == "FALSE":
                        gdpr = False
                    else:
                        error = True
                        erroroutput.append(name + " has no GDPR status.")
                    email = row[4]
                    queryset = Ticket.objects.filter(name=name, ticket_type=ticket_type)
                    if queryset.exists():
                        error = True
                        erroroutput.append(name + " is a possible duplicate. Save Manually")
                    if position == "" or position == " ":
                        error = True
                        erroroutput.append(name + " has no position.")
                    else:
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
                        found = False
                        for i in STAFF_TYPE_CHOICES:
                            if position == i[1]:
                                found = True
                                position = i[0]
                        if not found:
                            error = True
                            erroroutput.append(name + " position does not match database.")
                    if name == "" or name == " ":
                        error = True
                        erroroutput.append(email + " has no name.")
                    if email == "" or email == " ":
                        error = True
                        erroroutput.append(name + " has no email.")
                    else:
                        try:
                            validate_email(email)
                        except:
                            error = True
                            erroroutput.append(name + " has invalid email.")

                    if not error:
                        Ticket.objects.create(ticket_type=ticket_type, name=name, staff_type=position, is_gdpr_allowed=gdpr, email=email)
                        saved += 1

                first = False
            erroroutput.append(str(saved) + " staff were saved successfully")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_import_chaperone():
    try:
        first = True
        saved = 0
        erroroutput = []
        with open('/home/ubuntu/django/private_files/imports/chaperone.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            ticket_type = Type.objects.get(id=settings.CUSTOM_CHAPERONE_ID)
            for row in reader:
                if not first:
                    error = False
                    school = row[0]
                    name = row[1].strip()
                    name = name.replace("?", "")
                    name = " ".join(name.split())
                    name = name.title()
                    email = row[2]
                    queryset = Ticket.objects.filter(name=name, ticket_type=ticket_type)
                    if queryset.exists():
                        error = True
                        erroroutput.append(name + " is a possible duplicate. Save Manually")
                    if name == "" or name == " ":
                        error = True
                        erroroutput.append(email + " has no name.")
                    if school == "" or school == " ":
                        error = True
                        erroroutput.append(name + " has no school.")
                    else:
                        try:
                            school = School.objects.get(name=school)
                        except:
                            school = School.objects.create(name=school)
                    if email == "" or email == " ":
                        chaperone_type = "SC"
                    else:
                        try:
                            validate_email(email)
                            chaperone_type = "MC"
                        except:
                            error = True
                            erroroutput.append(name + " has invalid email.")

                    if not error:
                        Ticket.objects.create(ticket_type=ticket_type, name=name, school_name=school, chaperone_type=chaperone_type, email=email, is_gdpr_allowed=True)
                        saved += 1
                first = False
            try:
                School.objects.get(name="External")
            except:
                School.objects.create(name="External")
            erroroutput.append(str(saved) + " chaperones were saved successfully")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_import_gdprisams():
    try:
        first = True
        saved = 0
        erroroutput = []
        with open('/home/ubuntu/django/private_files/imports/gdprisams.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if not first:
                    error = False
                    studentnumber = row[0]
                    if studentnumber == "" or studentnumber == " ":
                        error = True
                        erroroutput.append("Student Number not filled in for one row.")
                    if row[1] == "TRUE":
                        gdpr = True
                    elif row[1] == "FALSE":
                        gdpr = False
                    else:
                        error = True
                        erroroutput.append(studentnumber + " has no GDPR Status.")
                    if not error:
                        email = studentnumber + "REDACTED"
                        try:
                            instance = Ticket.objects.get(email=email)
                            instance.is_gdpr_allowed = gdpr
                            instance.save()
                            saved += 1
                        except:
                            erroroutput.append(studentnumber + " is not in database.")
                first = False
            erroroutput.append(str(saved) + " gdpr isams items were saved successfully")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_import_gdprfinal():
    try:
        first = True
        saved = 0
        erroroutput = []
        with open('/home/ubuntu/django/private_files/imports/gdprfinal.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                if not first:
                    error = False
                    ticket_id = row[0]
                    if row[4] == "TRUE":
                        gdpr = True
                    elif row[4] == "FALSE" or row[4] == "" or row[4] == " ":
                        gdpr = False
                    else:
                        error = True
                        erroroutput.append(ticket_id + " has foreign gdpr status.")
                    dietary = row[5]
                    if dietary == "" or dietary == " ":
                        dietary = None
                    medical = row[6]
                    if medical == "" or medical == " ":
                        medical = None
                    if not error:
                        try:
                            instance = Ticket.objects.get(id=ticket_id)
                            instance.is_gdpr_allowed = gdpr
                            instance.dietary_restrictions = dietary
                            instance.medical_conditions = medical
                            instance.save()
                            saved += 1
                        except:
                            erroroutput.append(ticket_id + " is not in database.")
                first = False
            erroroutput.append(str(saved) + " gdpr final items were saved successfully")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def csv_import_guests():
    try:
        first = True
        saved = 0
        erroroutput = []
        with open('/home/ubuntu/django/private_files/imports/guests.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if not first:
                    error = False
                    name = row[0]
                    if name == "" or name == " ":
                        error = True
                        erroroutput.append("One of the rows has no name.")
                    if not error:
                        Ticket.objects.create(name=name, ticket_type_id=settings.CUSTOM_GUEST_ID, is_gdpr_allowed=True)
                        saved += 1
                first = False
            erroroutput.append(str(saved) + " guests were saved successfully")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def create_visitors(number):
    try:
        number = int(number.replace("VISITOR", ""))
        saved = 0
        erroroutput = []
        for i in range(1, number + 1):
            if i < 10:
                name = "0" + str(i)
            else:
                name = str(i)
            Ticket.objects.create(ticket_type_id=settings.CUSTOM_GUEST_ID, name=name, is_gdpr_allowed=True)
            saved += 1
        erroroutput.append(str(saved) + " no-name guests were added successfully.")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput


def create_chaperones(number):
    try:
        school = School.objects.get(name="CLIP")
        number = int(number.replace("CHAPERONE", ""))
        saved = 0
        erroroutput = []
        for i in range(21, number + 21):
            if i < 10:
                name = "0" + str(i)
            else:
                name = str(i)
            Ticket.objects.create(ticket_type_id=settings.CUSTOM_CHAPERONE_ID, name=name, is_gdpr_allowed=True, chaperone_type="SC", school_name=school)
            saved += 1
        erroroutput.append(str(saved) + " no-name guests were added successfully.")
    except Exception as e:
        erroroutput.append(e)
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput
