from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from staff import views as staffviews
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^robots.txt$',TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_file"),
    path('2020staffaccounts/', admin.site.urls),
    path("registration-details/<str:barcode>/", staffviews.registration_details, name="registration_details"),
    path("unregistration-details/<str:barcode>/", staffviews.unregistration_details, name="unregistration_details"),
    path("get-details/<str:barcode>/", staffviews.get_details, name="get_details"),
    path("conditions-details/<str:barcode>/", staffviews.conditions_details, name="conditions_details"),
    path("dbsearch/<str:query>/", staffviews.dbsearch, name="dbsearch"),
    path("dbdetails/<str:barcode>/", staffviews.dbdetails, name="dbdetails"),
    path("statistics-in-venue-details/<str:barcode>/", staffviews.statistics_in_venue_details, name="statistics_in_venue_details"),
    path("statistics-by-committee-details/<str:id>/", staffviews.statistics_by_committee_details,
         name="statistics_by_committee_details"),
    path("statistics-by-committee-barcode-details/<str:barcode>/", staffviews.statistics_by_committee_barcode_details, name="statistics_by_committee_barcode_details"),
    path("statistics-not-registered-details/<str:barcode>/", staffviews.statistics_not_registered_details,
         name="statistics_not_registered_details"),
    path("security-entry-details/<str:barcode>/", staffviews.security_entry, name="security_entry_details"),
    path("security-exit-details/<str:barcode>/", staffviews.security_exit, name="security_exit_details"),
    path("manage-vote-id/<str:id>/", staffviews.manage_vote_id, name="manage_vote_id"),
    path("end-voting/<str:id>/", staffviews.end_voting, name="end_voting"),
    path("", include('staff.urls')),
]

admin.site.site_header = "OPOMUN Staff Login"
admin.site.site_title = "OPOMUN Portal"
admin.site.index_title = "OPOMUN Portal"
