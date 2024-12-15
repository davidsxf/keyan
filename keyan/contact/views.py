from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def contract_list(request):
    """合同列表"""
    contracts = Contract.objects.all().order_by('-created_at')
    context = {
        'contracts': contracts,
        'active_menu': 'contract_list'
    }
    return render(request, 'dashboard/contract/list.html', context)



@login_required
def contract_detail(request, contract_id):
    """合同详情"""
    contract = get_object_or_404(Contract, id=contract_id)
    events = contract.contractevent_set.all().order_by('-created_at')
    context = {
        'contract': contract,
        'events': events,
        'active_menu': 'contract_list'
    }
    return render(request, 'dashboard/contract/detail.html', context)