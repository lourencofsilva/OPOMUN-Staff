from django.contrib.auth.models import Permission
from django.contrib import admin
from .models import Ticket, Committee, School, Type, CLIPStaff, Voting, Voter


class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'voting_id',)


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Committee)
admin.site.register(School)
admin.site.register(Type)
admin.site.register(Permission)
admin.site.register(CLIPStaff)
admin.site.register(Voting)
admin.site.register(Voter)
