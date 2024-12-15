from django.shortcuts import render

# Create your views here.
@login_required
def organ_list(request):
    """机构列表"""
    organs = Organ.objects.all().order_by('name')
    context = {
        'organs': organs,
        'active_menu': 'organ_list'
    }
    return render(request, 'dashboard/organ/list.html', context)

@login_required
def organ_detail(request, organ_id):
    """机构详情"""
    organ = get_object_or_404(Organ, id=organ_id)
    lead_projects = organ.lead_projects.all()
    partner_projects = organ.partner_projects.all()
    party_a_contracts = organ.party_a_contracts.all()
    party_b_contracts = organ.party_b_contracts.all()
    
    context = {
        'organ': organ,
        'lead_projects': lead_projects,
        'partner_projects': partner_projects,
        'party_a_contracts': party_a_contracts,
        'party_b_contracts': party_b_contracts,
        'active_menu': 'organ_list'
    }
    return render(request, 'dashboard/organ/detail.html', context)