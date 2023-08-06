from .models import School, Committee, Type, Ticket
from django.conf import settings
import warnings
import os
from django.db import models
from django.core import mail
import time

def run_tests():
    erroroutput = []
    error = False
    try:
        for ticket in Ticket.objects.all():
            if ticket.ticket_type.id == settings.CUSTOM_DELEGATE_ID:
                if not os.path.exists("/home/ubuntu/django/private_files/ticket-generation/qr-codes/" + str(ticket.id) + ".png"):
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " has no qr code assigned.")
                if not os.path.exists("/home/ubuntu/django/private_files/ticket-generation/ticket-pdfs/" + str(ticket.id) + ".pdf"):
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " has no pdf ticket assigned.")
                if not ticket.school_name:
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " has no school assigned.")
                if not ticket.country:
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " has no allocated country assigned.")
                if not ticket.committee:
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " has no committee assigned.")
                if ticket.staff_type:
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " should not have staff type assigned.")
                if ticket.chaperone_type:
                    error = True
                    erroroutput.append("Delegate Ticket ID: " + str(ticket.id) + " should not have chaperone type assigned.")
            if ticket.ticket_type.id == settings.CUSTOM_CHAPERONE_ID:
                if not os.path.exists("/home/ubuntu/django/private_files/ticket-generation/qr-codes/" + str(ticket.id) + ".png"):
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " has no qr code assigned.")
                if not os.path.exists("/home/ubuntu/django/private_files/ticket-generation/ticket-pdfs/" + str(ticket.id) + ".pdf"):
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " has no pdf ticket assigned.")
                if not ticket.school_name:
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " has no school assigned.")
                else:
                    school = School.objects.get(id=ticket.school_name.id)
                    chaperone_found_in_school = False
                    for chaperones in school.chaperones.all():
                        if chaperones.id == ticket.id:
                            chaperone_found_in_school = True
                    if not chaperone_found_in_school:
                        error = True
                        erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " is not assigned in School Model.")
                if ticket.country:
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " should not have allocated country assigned.")
                if ticket.committee:
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " should not have committee assigned.")
                if ticket.staff_type:
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " should not have staff type assigned.")
                if not ticket.chaperone_type:
                    error = True
                    erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " should have chaperone type assigned.")
                else:
                    if str(ticket.chaperone_type) == "MC":
                        if not ticket.email:
                            error = True
                            erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " has no email assigned.")
                    else:
                        if ticket.email:
                            error = True
                            erroroutput.append("Chaperone Ticket ID: " + str(ticket.id) + " is secondary but has email assigned.")
            if ticket.ticket_type.id == settings.CUSTOM_GUEST_ID:
                if ticket.school_name:
                    error = True
                    erroroutput.append("Guest Ticket ID: " + str(ticket.id) + " should not have school name assigned.")
                if ticket.email:
                    error = True
                    erroroutput.append("Guest Ticket ID: " + str(ticket.id) + " should not have email assigned.")
                if ticket.committee:
                    error = True
                    erroroutput.append("Guest Ticket ID: " + str(ticket.id) + " should not have committee assigned.")
                if ticket.staff_type:
                    error = True
                    erroroutput.append("Guest Ticket ID: " + str(ticket.id) + " should not have staff type assigned.")
                if ticket.chaperone_type:
                    error = True
                    erroroutput.append("Guest Ticket ID: " + str(ticket.id) + " should not have chaperone type assigned.")
            if ticket.ticket_type.id == settings.CUSTOM_STAFF_ID:
                if str(ticket.id) != str(settings.CUSTOM_CHAPERONE_STAFF_ID):
                    if ticket.school_name:
                        error = True
                        erroroutput.append("Staff Ticket ID: " + str(ticket.id) + " should not have school name assigned.")
                    if ticket.country:
                        error = True
                        erroroutput.append("Staff Ticket ID: " + str(ticket.id) + " should not have country assigned.")
                    if ticket.committee:
                        error = True
                        erroroutput.append("Staff Ticket ID: " + str(ticket.id) + " should not have committee assigned.")
                    if not ticket.staff_type:
                        error = True
                        erroroutput.append("Staff Ticket ID: " + str(ticket.id) + " has no staff type assigned.")
                    if ticket.chaperone_type:
                        error = True
                        erroroutput.append(
                            "Staff Ticket ID: " + str(ticket.id) + " should not have chaperone type assigned.")
                else:
                    if not ticket.school_name:
                        error = True
                        erroroutput.append("Staff / Chaperone Ticket ID: " + str(ticket.id) + " has no school assigned.")
                    else:
                        school = School.objects.get(id=ticket.school_name.id)
                        chaperone_found_in_school = False
                        for chaperones in school.chaperones.all():
                            if chaperones.id == ticket.id:
                                chaperone_found_in_school = True
                        if not chaperone_found_in_school:
                            error = True
                            erroroutput.append(
                                "Staff / Chaperone Ticket ID: " + str(ticket.id) + " is not assigned in School Model.")
                    if not ticket.email:
                        error = True
                        erroroutput.append("Staff / Chaperone Ticket ID: " + str(ticket.id) + " has no email assigned.")
                    if ticket.country:
                        error = True
                        erroroutput.append("Staff / Chaperone Ticket ID: " + str(ticket.id) + " should not have country assigned.")
                    if ticket.committee:
                        error = True
                        erroroutput.append(
                            "Staff / Chaperone Ticket ID: " + str(ticket.id) + " should not have committee assigned.")
                    if not ticket.staff_type:
                        error = True
                        erroroutput.append("Staff / Chaperone Ticket ID: " + str(ticket.id) + " has no staff type assigned.")
                    if not ticket.chaperone_type:
                        error = True
                        erroroutput.append(
                            "Staff / Chaperone Ticket ID: " + str(ticket.id) + " should have chaperone type assigned.")

        for school_item in School.objects.all():
            if school_item.chaperones:
                for chaperone in school_item.chaperones.all():
                    chaperone_id = Ticket.objects.get(id=chaperone.id)
                    if chaperone_id.school_name:
                        if not chaperone_id.school_name.id == school_item.id:
                            error = True
                            erroroutput.append("School ID: " + str(school_item.id) + " | Chaperone " + str(chaperone.id) + " is not assigned in Ticket Model.")
                    else:
                        error = True
                        erroroutput.append("School ID: " + str(school_item.id) + " | Chaperone " + str(
                            chaperone.id) + " is not assigned in Ticket Model.")
            if str(school_item) != "External":
                mainchaperone = Ticket.objects.filter(models.Q(school_name=school_item) & (models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(chaperone_type="MC"))
                if mainchaperone.count() != 1:
                    error = True
                    erroroutput.append("School ID: " + str(school_item.id) + " has none / more than one main chaperone.")
            else:
                if school_item.chaperones.count() != 0:
                    error = True
                    erroroutput.append(
                        "External School has non-zero chaperones.")
    except Exception as e:
        error = True
        erroroutput.append(e)
    if error:
        return erroroutput
    else:
        return None


chaperonemessage = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html style="width:100%;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0;"><head><meta charset="UTF-8"><meta content="width=device-width, initial-scale=1" name="viewport"><meta name="x-apple-disable-message-reformatting"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta content="telephone=no" name="format-detection"><title>OPOMUN Ticket</title> <!--[if (mso 16)]><style type="text/css">     a {text-decoration: none;}     </style><![endif]--> <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> <!--[if !mso]><!-- --><link href="https://fonts.googleapis.com/css?family=Roboto:400,400i,700,700i" rel="stylesheet"> <!--<![endif]--><style type="text/css">
@media only screen and (max-width:600px) {.st-br { padding-left:10px!important; padding-right:10px!important } p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important; text-align:center } h2 a { font-size:26px!important; text-align:center } h3 a { font-size:20px!important; text-align:center } .es-menu td a { font-size:14px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:14px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { 
font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } a.es-button { font-size:16px!important; display:block!important; border-left-width:0px!important; border-right-width:0px!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { 
display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } .es-desk-hidden { display:table-row!important; width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } .es-desk-menu-hidden { display:table-cell!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } }.rollover:hover .rollover-first {	max-height:0px!important;}.rollover:hover .rollover-second 
{	max-height:none!important;}#outlook a {	padding:0;}.ExternalClass {	width:100%;}.ExternalClass,.ExternalClass p,.ExternalClass span,.ExternalClass font,.ExternalClass td,.ExternalClass div {	line-height:100%;}.es-button {	mso-style-priority:100!important;	text-decoration:none!important;}a[x-apple-data-detectors] {	color:inherit!important;	text-decoration:none!important;	font-size:inherit!important;	font-family:inherit!important;	font-weight:inherit!important;	line-height:inherit!important;}.es-desk-hidden {	display:none;	float:left;	overflow:hidden;	width:0;	max-height:0;	line-height:0;	mso-hide:all;}.es-button-border:hover {	border-style:solid solid solid solid!important;	background:#d6a700!important;	border-color:#42d159 #42d159 #42d159 #42d159!important;}.es-button-border:hover a.es-button {	background:#d6a700!important;	border-color:#d6a700!important;}td .es-button-border:hover a.es-button-1 
{	background:#0081cc!important;	border-color:#0081cc!important;}td .es-button-border-2:hover {	background:#0081cc!important;}</style></head><body style="width:100%;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0;"><span style="display:none !important;font-size:0px;line-height:0;color:#FFFFFF;visibility:hidden;opacity:0;height:0;width:0;mso-hide:all;">Download Your Ticket Now!</span><div class="es-wrapper-color" style="background-color:#F6F6F6;"> <!--[if gte mso 9]><v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t"> <v:fill type="tile" color="#f6f6f6"></v:fill> </v:background><![endif]-->
<table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top;"><tr style="border-collapse:collapse;"><td class="st-br" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" class="es-header" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:transparent;background-repeat:repeat;background-position:center top;"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;background-color:#FEFAFA;" bgcolor="#fefafa"> <!--[if gte mso 9]><v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="mso-width-percent:1000;height:204px;">
<v:fill type="tile" src="https://pics.esputnik.com/repository/home/17278/common/images/1546958148946.jpg" color="#343434" origin="0.5, 0" position="0.5,0"></v:fill><v:textbox inset="0,0,0,0"><![endif]--><div><table bgcolor="transparent" class="es-header-body" align="center" cellpadding="0" cellspacing="0" width="600" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;"><tr style="border-collapse:collapse;"><td align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;"><table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="560" align="center" valign="top" style="padding:0;Margin:0;">
<table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;"><a target="_blank" href="https://opomun.com" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;font-size:14px;text-decoration:underline;color:#1376C8;"><img src="https://opomun.com/images/text-logo.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;width:220px;height:82px;" class="adapt-img" height="82" width="218"></a></td></tr><tr style="border-collapse:collapse;"><td align="center" height="0" style="padding:0;Margin:0;"></td></tr></table></td></tr></table></td></tr></table></div> <!--[if gte mso 9]></v:textbox></v:rect>
<![endif]--></td></tr></table><table cellpadding="0" cellspacing="0" class="es-content" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;"><tr style="border-collapse:collapse;"><td align="center" bgcolor="transparent" style="padding:0;Margin:0;background-color:transparent;"><table bgcolor="transparent" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;"><tr style="border-collapse:collapse;"><td align="left" style="Margin:0;padding-bottom:15px;padding-top:30px;padding-left:30px;padding-right:30px;border-radius:10px 10px 0px 0px;background-color:#FFFFFF;background-position:left bottom;" bgcolor="#ffffff">
<table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="540" align="center" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-position:left bottom;" role="presentation"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;"><h1 style="Margin:0;line-height:36px;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;font-size:30px;font-style:normal;font-weight:bold;color:#212121;">IMPORTANT - OPOMUN 2020 Ticket</h1></td></tr><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;">
<h2 style="Margin:0;line-height:29px;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;font-size:24px;font-style:normal;font-weight:bold;color:#212121;"><br></h2><h4 style="Margin:0;line-height:120%;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;">Dear Chaperone, attached to this email is your personal ticket and tickets for any other chaperones and delegates of your school, for OPOMUN 2020, in PDF format. It is necessary that these are shown at registration in order to gain access, either printed or shown on a device. More information is written on the tickets themselves.</h4></td></tr></table></td></tr></table></td></tr><tr style="border-collapse:collapse;"><td align="left" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:30px;padding-right:30px;border-radius:0px 0px 10px 10px;background-position:left top;background-color:#FFFFFF;">
<table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="540" align="center" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" style="padding:20px;Margin:0;"><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td style="padding:0;Margin:0px 0px 0px 0px;border-bottom:1px solid #CCCCCC;background:none;height:1px;width:100%;margin:0px;"></td></tr></table></td></tr><tr style="border-collapse:collapse;">
<td align="center" style="padding:0;Margin:0;"><img class="adapt-img" alt width="300" src="https://cdt-timer.stripocdn.email/api/v1/images/Sv7wWTWTVr14v-nkHgLBw1g_hhJuIamsc2mcyET21iw?l=1580930326449" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;"></td></tr><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;padding-top:20px;"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:16px;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;line-height:24px;color:#131313;">The day we´ve all been waiting for is nearly here!</p></td></tr></table></td></tr></table></td></tr></table></td></tr></table>
<table cellpadding="0" cellspacing="0" class="es-footer" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#F6F6F6;background-repeat:repeat;background-position:center top;"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;background-color:#00A3FF;" bgcolor="#00A3FF"><table bgcolor="#31cb4b" class="es-footer-body" align="center" cellpadding="0" cellspacing="0" width="600" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;"><tr style="border-collapse:collapse;"><td style="Margin:0;padding-top:30px;padding-bottom:30px;padding-left:30px;padding-right:30px;border-radius:0px 0px 10px 10px;background-color:#EFEFEF;" align="left" bgcolor="#efefef"> <!--[if mso]><table width="540" cellpadding="0" cellspacing="0"><tr>
<td width="186" valign="top"><![endif]--><table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left;"><tr style="border-collapse:collapse;"><td width="166" align="center" style="padding:0;Margin:0;"><table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" height="12" style="padding:0;Margin:0;"></td></tr><tr style="border-collapse:collapse;"><td class="es-m-txt-c" align="center" style="padding:0;Margin:0;"><table class="es-table-not-adapt es-social" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;">
<td valign="top" align="center" style="padding:0;Margin:0;padding-right:10px;"><a target="_blank" href="https://www.facebook.com/opomun/" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;font-size:16px;text-decoration:underline;color:#FFFFFF;"><img title="Facebook" src="https://evftff.stripocdn.email/content/assets/img/social-icons/logo-black/facebook-logo-black.png" alt="Fb" width="32" height="32" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;"></a></td><td valign="top" align="center" style="padding:0;Margin:0;">
<a target="_blank" href="https://www.instagram.com/opomun2020/" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;font-size:16px;text-decoration:underline;color:#FFFFFF;"><img title="Instagram" src="https://evftff.stripocdn.email/content/assets/img/social-icons/logo-black/instagram-logo-black.png" alt="Inst" width="32" height="32" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;"></a></td></tr></table></td></tr></table></td><td class="es-hidden" width="20" style="padding:0;Margin:0;"></td></tr></table> <!--[if mso]></td><td width="165" valign="top"><![endif]--><table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left;"><tr style="border-collapse:collapse;">
<td class="es-m-p20b" width="165" align="center" style="padding:0;Margin:0;"><table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" style="padding:20px;Margin:0;"><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td style="padding:0;Margin:0px 0px 0px 0px;border-bottom:1px solid #CCCCCC;background:none;height:1px;width:100%;margin:0px;"></td></tr></table></td></tr></table></td></tr></table> <!--[if mso]></td><td width="20"></td><td width="169" valign="top"><![endif]-->
<table class="es-right" cellspacing="0" cellpadding="0" align="right" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:right;"><tr style="border-collapse:collapse;"><td class="es-m-p0r es-m-p20b" width="169" align="center" style="padding:0;Margin:0;"><table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" class="es-m-txt-c" style="padding:10px;Margin:0;"><span class="es-button-border es-button-border-2" style="border-style:solid;border-color:#2CB543;background:#00A3FF;border-width:0px;display:inline-block;border-radius:40px;width:auto;">
<a href="https://opomun.com/privacy-notice" class="es-button es-button-1" target="_blank" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;font-size:16px;color:#FFFFFF;border-style:solid;border-color:#00A3FF;border-width:10px 20px 10px 20px;display:inline-block;background:#00A3FF;border-radius:40px;font-weight:normal;font-style:normal;line-height:19px;width:auto;text-align:center;border-left-width:20px;border-right-width:20px;">Privacy Notice</a></span></td></tr></table></td></tr></table> <!--[if mso]></td></tr></table><![endif]--></td></tr><tr style="border-collapse:collapse;"><td align="left" style="padding:0;Margin:0;background-position:left top;">
<table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="600" align="center" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" height="40" style="padding:0;Margin:0;"></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr></table></div></body>
</html>"""

delegatemessage = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html style="width:100%;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0;"><head><meta charset="UTF-8"><meta content="width=device-width, initial-scale=1" name="viewport"><meta name="x-apple-disable-message-reformatting"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta content="telephone=no" name="format-detection"><title>OPOMUN Ticket</title> <!--[if (mso 16)]><style type="text/css">     a {text-decoration: none;}     </style><![endif]--> <!--[if gte mso 9]><style>sup { font-size: 100% !important; }</style><![endif]--> <!--[if !mso]><!-- --><link href="https://fonts.googleapis.com/css?family=Roboto:400,400i,700,700i" rel="stylesheet"> <!--<![endif]--><style type="text/css">
@media only screen and (max-width:600px) {.st-br { padding-left:10px!important; padding-right:10px!important } p, ul li, ol li, a { font-size:16px!important; line-height:150%!important } h1 { font-size:30px!important; text-align:center; line-height:120%!important } h2 { font-size:26px!important; text-align:center; line-height:120%!important } h3 { font-size:20px!important; text-align:center; line-height:120%!important } h1 a { font-size:30px!important; text-align:center } h2 a { font-size:26px!important; text-align:center } h3 a { font-size:20px!important; text-align:center } .es-menu td a { font-size:14px!important } .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a { font-size:16px!important } .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a { font-size:14px!important } .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a { 
font-size:12px!important } *[class="gmail-fix"] { display:none!important } .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 { text-align:center!important } .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 { text-align:right!important } .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 { text-align:left!important } .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img { display:inline!important } .es-button-border { display:block!important } a.es-button { font-size:16px!important; display:block!important; border-left-width:0px!important; border-right-width:0px!important } .es-btn-fw { border-width:10px 0px!important; text-align:center!important } .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right { width:100%!important } .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header { width:100%!important; max-width:600px!important } .es-adapt-td { 
display:block!important; width:100%!important } .adapt-img { width:100%!important; height:auto!important } .es-m-p0 { padding:0px!important } .es-m-p0r { padding-right:0px!important } .es-m-p0l { padding-left:0px!important } .es-m-p0t { padding-top:0px!important } .es-m-p0b { padding-bottom:0!important } .es-m-p20b { padding-bottom:20px!important } .es-mobile-hidden, .es-hidden { display:none!important } .es-desk-hidden { display:table-row!important; width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important } .es-desk-menu-hidden { display:table-cell!important } table.es-table-not-adapt, .esd-block-html table { width:auto!important } table.es-social { display:inline-block!important } table.es-social td { display:inline-block!important } }.rollover:hover .rollover-first {	max-height:0px!important;}.rollover:hover .rollover-second 
{	max-height:none!important;}#outlook a {	padding:0;}.ExternalClass {	width:100%;}.ExternalClass,.ExternalClass p,.ExternalClass span,.ExternalClass font,.ExternalClass td,.ExternalClass div {	line-height:100%;}.es-button {	mso-style-priority:100!important;	text-decoration:none!important;}a[x-apple-data-detectors] {	color:inherit!important;	text-decoration:none!important;	font-size:inherit!important;	font-family:inherit!important;	font-weight:inherit!important;	line-height:inherit!important;}.es-desk-hidden {	display:none;	float:left;	overflow:hidden;	width:0;	max-height:0;	line-height:0;	mso-hide:all;}.es-button-border:hover {	border-style:solid solid solid solid!important;	background:#d6a700!important;	border-color:#42d159 #42d159 #42d159 #42d159!important;}.es-button-border:hover a.es-button {	background:#d6a700!important;	border-color:#d6a700!important;}td .es-button-border:hover a.es-button-1 
{	background:#0081cc!important;	border-color:#0081cc!important;}td .es-button-border-2:hover {	background:#0081cc!important;}</style></head><body style="width:100%;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0;"><span style="display:none !important;font-size:0px;line-height:0;color:#FFFFFF;visibility:hidden;opacity:0;height:0;width:0;mso-hide:all;">Download Your Ticket Now!</span><div class="es-wrapper-color" style="background-color:#F6F6F6;"> <!--[if gte mso 9]><v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t"> <v:fill type="tile" color="#f6f6f6"></v:fill> </v:background><![endif]-->
<table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top;"><tr style="border-collapse:collapse;"><td class="st-br" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" class="es-header" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:transparent;background-repeat:repeat;background-position:center top;"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;background-color:#FEFAFA;" bgcolor="#fefafa"> <!--[if gte mso 9]><v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="mso-width-percent:1000;height:204px;">
<v:fill type="tile" src="https://pics.esputnik.com/repository/home/17278/common/images/1546958148946.jpg" color="#343434" origin="0.5, 0" position="0.5,0"></v:fill><v:textbox inset="0,0,0,0"><![endif]--><div><table bgcolor="transparent" class="es-header-body" align="center" cellpadding="0" cellspacing="0" width="600" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;"><tr style="border-collapse:collapse;"><td align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;"><table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="560" align="center" valign="top" style="padding:0;Margin:0;">
<table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;"><a target="_blank" href="https://opomun.com" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;font-size:14px;text-decoration:underline;color:#1376C8;"><img src="https://opomun.com/images/text-logo.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;width:220px;height:82px;" class="adapt-img" height="82" width="218"></a></td></tr><tr style="border-collapse:collapse;"><td align="center" height="0" style="padding:0;Margin:0;"></td></tr></table></td></tr></table></td></tr></table></div> <!--[if gte mso 9]></v:textbox></v:rect>
<![endif]--></td></tr></table><table cellpadding="0" cellspacing="0" class="es-content" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;"><tr style="border-collapse:collapse;"><td align="center" bgcolor="transparent" style="padding:0;Margin:0;background-color:transparent;"><table bgcolor="transparent" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;"><tr style="border-collapse:collapse;"><td align="left" style="Margin:0;padding-bottom:15px;padding-top:30px;padding-left:30px;padding-right:30px;border-radius:10px 10px 0px 0px;background-color:#FFFFFF;background-position:left bottom;" bgcolor="#ffffff">
<table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="540" align="center" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-position:left bottom;" role="presentation"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;"><h1 style="Margin:0;line-height:36px;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;font-size:30px;font-style:normal;font-weight:bold;color:#212121;">IMPORTANT - OPOMUN 2020 Ticket</h1></td></tr><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;">
<h2 style="Margin:0;line-height:29px;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;font-size:24px;font-style:normal;font-weight:bold;color:#212121;"><br></h2><h4 style="Margin:0;line-height:120%;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;">Dear Delegate, attached to this email is your personal ticket for OPOMUN 2020, in PDF format. It is necessary that you show it at registration in order to gain access, either printed or shown on your device. More information is written on the ticket itself.</h4></td></tr></table></td></tr></table></td></tr><tr style="border-collapse:collapse;"><td align="left" style="Margin:0;padding-top:5px;padding-bottom:5px;padding-left:30px;padding-right:30px;border-radius:0px 0px 10px 10px;background-position:left top;background-color:#FFFFFF;">
<table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="540" align="center" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" style="padding:20px;Margin:0;"><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td style="padding:0;Margin:0px 0px 0px 0px;border-bottom:1px solid #CCCCCC;background:none;height:1px;width:100%;margin:0px;"></td></tr></table></td></tr><tr style="border-collapse:collapse;">
<td align="center" style="padding:0;Margin:0;"><img class="adapt-img" alt width="300" src="https://cdt-timer.stripocdn.email/api/v1/images/Sv7wWTWTVr14v-nkHgLBw1g_hhJuIamsc2mcyET21iw?l=1580930326449" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;"></td></tr><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;padding-top:20px;"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:16px;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;line-height:24px;color:#131313;">The day we´ve all been waiting for is nearly here!</p></td></tr></table></td></tr></table></td></tr></table></td></tr></table>
<table cellpadding="0" cellspacing="0" class="es-footer" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;background-color:#F6F6F6;background-repeat:repeat;background-position:center top;"><tr style="border-collapse:collapse;"><td align="center" style="padding:0;Margin:0;background-color:#00A3FF;" bgcolor="#00A3FF"><table bgcolor="#31cb4b" class="es-footer-body" align="center" cellpadding="0" cellspacing="0" width="600" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;"><tr style="border-collapse:collapse;"><td style="Margin:0;padding-top:30px;padding-bottom:30px;padding-left:30px;padding-right:30px;border-radius:0px 0px 10px 10px;background-color:#EFEFEF;" align="left" bgcolor="#efefef"> <!--[if mso]><table width="540" cellpadding="0" cellspacing="0"><tr>
<td width="186" valign="top"><![endif]--><table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left;"><tr style="border-collapse:collapse;"><td width="166" align="center" style="padding:0;Margin:0;"><table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" height="12" style="padding:0;Margin:0;"></td></tr><tr style="border-collapse:collapse;"><td class="es-m-txt-c" align="center" style="padding:0;Margin:0;"><table class="es-table-not-adapt es-social" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;">
<td valign="top" align="center" style="padding:0;Margin:0;padding-right:10px;"><a target="_blank" href="https://www.facebook.com/opomun/" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;font-size:16px;text-decoration:underline;color:#FFFFFF;"><img title="Facebook" src="https://evftff.stripocdn.email/content/assets/img/social-icons/logo-black/facebook-logo-black.png" alt="Fb" width="32" height="32" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;"></a></td><td valign="top" align="center" style="padding:0;Margin:0;">
<a target="_blank" href="https://www.instagram.com/opomun2020/" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:roboto, 'helvetica neue', helvetica, arial, sans-serif;font-size:16px;text-decoration:underline;color:#FFFFFF;"><img title="Instagram" src="https://evftff.stripocdn.email/content/assets/img/social-icons/logo-black/instagram-logo-black.png" alt="Inst" width="32" height="32" style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;"></a></td></tr></table></td></tr></table></td><td class="es-hidden" width="20" style="padding:0;Margin:0;"></td></tr></table> <!--[if mso]></td><td width="165" valign="top"><![endif]--><table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left;"><tr style="border-collapse:collapse;">
<td class="es-m-p20b" width="165" align="center" style="padding:0;Margin:0;"><table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" style="padding:20px;Margin:0;"><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td style="padding:0;Margin:0px 0px 0px 0px;border-bottom:1px solid #CCCCCC;background:none;height:1px;width:100%;margin:0px;"></td></tr></table></td></tr></table></td></tr></table> <!--[if mso]></td><td width="20"></td><td width="169" valign="top"><![endif]-->
<table class="es-right" cellspacing="0" cellpadding="0" align="right" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:right;"><tr style="border-collapse:collapse;"><td class="es-m-p0r es-m-p20b" width="169" align="center" style="padding:0;Margin:0;"><table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" class="es-m-txt-c" style="padding:10px;Margin:0;"><span class="es-button-border es-button-border-2" style="border-style:solid;border-color:#2CB543;background:#00A3FF;border-width:0px;display:inline-block;border-radius:40px;width:auto;">
<a href="https://opomun.com/privacy-notice" class="es-button es-button-1" target="_blank" style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:tahoma, verdana, segoe, sans-serif;font-size:16px;color:#FFFFFF;border-style:solid;border-color:#00A3FF;border-width:10px 20px 10px 20px;display:inline-block;background:#00A3FF;border-radius:40px;font-weight:normal;font-style:normal;line-height:19px;width:auto;text-align:center;border-left-width:20px;border-right-width:20px;">Privacy Notice</a></span></td></tr></table></td></tr></table> <!--[if mso]></td></tr></table><![endif]--></td></tr><tr style="border-collapse:collapse;"><td align="left" style="padding:0;Margin:0;background-position:left top;">
<table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td width="600" align="center" valign="top" style="padding:0;Margin:0;"><table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;"><tr style="border-collapse:collapse;"><td align="center" height="40" style="padding:0;Margin:0;"></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr></table></div></body>
</html>"""


def test_mass_emails():
    result = run_tests()
    erroroutput = []
    sent = 0
    if result is not None:
        erroroutput.append("Database Checks Failed")
        for i in erroroutput:
            warnings.warn(i, Warning)
        return erroroutput
    with mail.get_connection() as connection:
        queryset = Ticket.objects.filter((models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID) | models.Q(id=settings.CUSTOM_CHAPERONE_STAFF_ID)) & models.Q(chaperone_type="MC"))
        for ticket in queryset:
            try:
                email = mail.EmailMessage(
                    'TEST OPOMUN 2020 - Tickets for ' + str(ticket.school_name),
                    chaperonemessage,
                    'REDACTED',
                    ['REDACTED'],
                    connection=connection,
                )
                email.content_subtype = "html"
                allchaperones = Ticket.objects.filter(models.Q(school_name=ticket.school_name) & models.Q(ticket_type=settings.CUSTOM_CHAPERONE_ID))
                for chaperone in allchaperones:
                    email.attach_file("private_files/ticket-generation/ticket-pdfs/" + str(chaperone.id) + ".pdf")
                chaperonees = Ticket.objects.filter(models.Q(school_name=ticket.school_name) & models.Q(ticket_type=settings.CUSTOM_DELEGATE_ID))
                for chaperonee in chaperonees:
                    email.attach_file("private_files/ticket-generation/ticket-pdfs/" + str(chaperonee.id) + ".pdf")
                response = email.send()
                if response != 1:
                    raise NameError('Email for Ticket ID ' + ticket.id + ' failed.')
                sent += 1
                time.sleep(3)
            except Exception as e:
                erroroutput.append(e)
        queryset = Ticket.objects.filter(ticket_type=settings.CUSTOM_DELEGATE_ID)
        for ticket in queryset:
            try:
                if ticket.email:
                    email = mail.EmailMessage(
                        'TEST OPOMUN 2020 - Ticket for ' + str(ticket.name),
                        delegatemessage,
                        'REDACTED',
                        ['REDACTED'],
                        connection=connection,
                    )
                    email.content_subtype = "html"
                    email.attach_file("private_files/ticket-generation/ticket-pdfs/" + str(ticket.id) + ".pdf")
                    response = email.send()
                    if response != 1:
                        raise NameError('Email for Ticket ID ' + ticket.id + ' failed.')
                    sent += 1
                    time.sleep(3)
            except Exception as e:
                erroroutput.append(e)
    erroroutput.append(str(sent) + " emails were successfully sent.")
    for i in erroroutput:
        warnings.warn(i, Warning)
    return erroroutput
