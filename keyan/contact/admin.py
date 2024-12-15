from django.contrib import admin

# Register your models here.
from .models import ContractType, Contract, ContractEvent

@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'title', 'contract_type', 'project',
                   'party_a', 'party_b', 'amount', 'status', 'responsible_person')
    list_filter = ('status', 'contract_type', 'project', 'responsible_person')
    search_fields = ('contract_number', 'title', 'project__name', 
                    'party_a__name', 'party_b__name')
    date_hierarchy = 'created_at'
    raw_id_fields = ('project', 'party_a', 'party_b', 'responsible_person')

@admin.register(ContractEvent)
class ContractEventAdmin(admin.ModelAdmin):
    list_display = ('contract', 'event_type', 'operator', 'created_at')
    list_filter = ('event_type', 'operator')
    search_fields = ('contract__contract_number', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('contract', 'operator')