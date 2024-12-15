from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from contact.models import Contract, ContractType, ContractEvent
from project.models import Project, ProjectParticipation
from finance.models import Budget, Income, Expense
from organ.models import Organ, Department, Staff
from django.contrib.auth.models import User
from .forms import BudgetForm, IncomeForm, ExpenseForm
import csv
from django.http import HttpResponse

@login_required
def dashboard(request):
    """仪表盘首页"""
    # 基础统计数据
    project_count = Project.objects.count()
    contract_count = Contract.objects.count()
    organ_count = Organ.objects.count()
    pending_contracts = Contract.objects.filter(status='pending').count()
    
    # 项目状态统计
    project_stats = []
    for status_code, status_name in Project.PROJECT_STATUS_CHOICES:
        count = Project.objects.filter(status=status_code).count()
        project_stats.append({
            'status': status_code,
            'get_status_display': status_name,
            'count': count
        })
    
    # 合同类型统计
    contract_stats = Contract.objects.values('contract_type__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 机构类型统计
    organ_stats = Organ.objects.values('organ_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 最近的合同事件
    recent_events = ContractEvent.objects.select_related(
        'contract', 'operator'
    ).order_by('-created_at')[:10]
    
    # 项目金额统计
    project_amount_stats = {
        'total_budget': Project.objects.aggregate(total=Sum('budget'))['total'] or 0,
        'avg_budget': Project.objects.aggregate(avg=Avg('budget'))['avg'] or 0,
    }
    
    # 合同金额统计
    contract_amount_stats = {
        'total_amount': Contract.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'avg_amount': Contract.objects.aggregate(avg=Avg('amount'))['avg'] or 0,
    }
    
    context = {
        'project_count': project_count,
        'contract_count': contract_count,
        'organ_count': organ_count,
        'pending_contracts': pending_contracts,
        'project_stats': project_stats,
        'contract_stats': contract_stats,
        'organ_stats': organ_stats,
        'recent_events': recent_events,
        'project_amount_stats': project_amount_stats,
        'contract_amount_stats': contract_amount_stats,
        'active_menu': 'dashboard'
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def project_list(request):
    """项目列表视图"""
    projects = Project.objects.select_related('lead_organ', 'manager').all()
    
    # 获取所有筛选参数
    filters = {
        'code': request.GET.get('code', ''),
        'name': request.GET.get('name', ''),
        'status': request.GET.get('status', ''),
        'type': request.GET.get('type', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'leader': request.GET.get('leader', ''),
    }
    
    # 应用筛选条件
    if filters['code']:
        projects = projects.filter(code__icontains=filters['code'])
    if filters['name']:
        projects = projects.filter(name__icontains=filters['name'])
    if filters['status']:
        projects = projects.filter(status=filters['status'])
    if filters['type']:
        projects = projects.filter(project_type=filters['type'])
    if filters['start_date']:
        projects = projects.filter(start_date__gte=filters['start_date'])
    if filters['end_date']:
        projects = projects.filter(end_date__lte=filters['end_date'])
    if filters['leader']:
        projects = projects.filter(
            Q(manager__name__icontains=filters['leader'])
        )
    
    # 排序
    sort_by = request.GET.get('sort', '-created_at')
    projects = projects.order_by(sort_by)
    
    # 统计信息
    stats = {
        'total_count': projects.count(),
        'total_budget': projects.aggregate(total=Sum('budget'))['total'] or 0,
        'status_count': dict(projects.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'type_count': dict(projects.values('project_type').annotate(count=Count('id')).values_list('project_type', 'count')),
    }
    
    # 分页
    paginator = Paginator(projects, 10)  # 每页显示10条
    page = request.GET.get('page')
    projects = paginator.get_page(page)
    
    # 构建查询参数字符串（用于分页链接）
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()
    
    context = {
        'projects': projects,
        'project_status': Project.STATUS_CHOICES,
        'project_types': Project.PROJECT_TYPES,
        'filters': filters,
        'stats': stats,
        'query_string': query_string,
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/list.html', context)

@login_required
def project_detail(request, project_id):
    """项目详情"""
    project = get_object_or_404(Project, id=project_id)
    contracts = project.contract_set.all()
    context = {
        'project': project,
        'contracts': contracts,
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/detail.html', context)

@login_required
def organ_list(request):
    """机构列表"""
    organs = Organ.objects.all()
    
    # 获取筛选参数
    filters = {
        'organ_type': request.GET.get('organ_type', ''),
        'search': request.GET.get('search', ''),
        'sort': request.GET.get('sort', 'name'),
    }
    
    # 应用筛选条件
    if filters['organ_type']:
        organs = organs.filter(organ_type=filters['organ_type'])
    if filters['search']:
        organs = organs.filter(
            Q(code__icontains=filters['search']) |
            Q(name__icontains=filters['search']) |
            Q(contact_person__icontains=filters['search']) |
            Q(contact_phone__icontains=filters['search'])
        )
    
    # 排序
    if filters['sort'] == '-created_at':
        organs = organs.order_by('-created_at')
    elif filters['sort'] == 'created_at':
        organs = organs.order_by('created_at')
    elif filters['sort'] == '-name':
        organs = organs.order_by('-name')
    else:
        organs = organs.order_by('name')
    
    # 统计信息
    total_count = organs.count()
    type_stats = {
        'university': organs.filter(organ_type='university').count(),
        'company': organs.filter(organ_type='company').count(),
        'research': organs.filter(organ_type='research').count(),
    }
    
    # 分页
    paginator = Paginator(organs, 10)  # 每页显示10条
    page = request.GET.get('page')
    organs = paginator.get_page(page)
    
    # 构建查询参数字符串（用于分页链接）
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()
    
    context = {
        'organs': organs,
        'organ_types': Organ.ORGAN_TYPES,
        'filters': filters,
        'stats': {
            'total_count': total_count,
            'university_count': type_stats['university'],
            'company_count': type_stats['company'],
            'research_count': type_stats['research'],
        },
        'query_string': query_string,
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

@login_required
def contract_list(request):
    """合同列表"""
    contracts = Contract.objects.select_related(
        'contract_type', 'project', 'party_a', 'party_b', 'responsible_person'
    ).all()
    
    # 获取筛选参数
    filters = {
        'contract_type': request.GET.get('contract_type', ''),
        'project': request.GET.get('project', ''),
        'status': request.GET.get('status', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'search': request.GET.get('search', ''),
    }
    
    # 应用筛选条件
    if filters['contract_type']:
        contracts = contracts.filter(contract_type_id=filters['contract_type'])
    if filters['project']:
        contracts = contracts.filter(project_id=filters['project'])
    if filters['status']:
        contracts = contracts.filter(status=filters['status'])
    if filters['start_date']:
        contracts = contracts.filter(start_date__gte=filters['start_date'])
    if filters['end_date']:
        contracts = contracts.filter(end_date__lte=filters['end_date'])
    if filters['search']:
        contracts = contracts.filter(
            Q(contract_number__icontains=filters['search']) |
            Q(title__icontains=filters['search']) |
            Q(party_a__name__icontains=filters['search']) |
            Q(party_b__name__icontains=filters['search'])
        )
    
    # 排序
    sort_by = request.GET.get('sort', '-created_at')
    contracts = contracts.order_by(sort_by)
    
    # 统计信息
    stats = {
        'total_count': contracts.count(),
        'total_amount': contracts.aggregate(total=Sum('amount'))['total'] or 0,
        'status_count': dict(contracts.values('status').annotate(count=Count('id')).values_list('status', 'count')),
        'type_count': dict(contracts.values('contract_type__name').annotate(count=Count('id')).values_list('contract_type__name', 'count')),
    }
    
    # 分页
    paginator = Paginator(contracts, 10)
    page = request.GET.get('page')
    contracts = paginator.get_page(page)
    
    # 构建查询参数字符串（用于分页链接）
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()
    
    context = {
        'contracts': contracts,
        'contract_types': ContractType.objects.all().order_by('name'),
        'projects': Project.objects.all().order_by('-created_at'),
        'contract_status': Contract.STATUS_CHOICES,
        'filters': filters,
        'stats': stats,
        'query_string': query_string,
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

@login_required
def organ_add(request):
    """添加机构"""
    if request.method == 'POST':
        # 获取表单数据
        code = request.POST.get('code')
        name = request.POST.get('name')
        organ_type = request.POST.get('organ_type')
        address = request.POST.get('address')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        description = request.POST.get('description')
        
        try:
            # 创建新机构
            organ = Organ.objects.create(
                code=code,
                name=name,
                organ_type=organ_type,
                address=address,
                contact_person=contact_person,
                contact_phone=contact_phone,
                description=description
            )
            messages.success(request, f'机构 {organ.name} 创建成功！')
            return redirect('dashboard:organ_detail', organ_id=organ.id)
        except Exception as e:
            messages.error(request, f'创建机构失败：{str(e)}')
            return redirect('dashboard:organ_add')
    
    # GET 请求，显示表单
    context = {
        'organ_types': Organ.ORGAN_TYPES,
        'active_menu': 'organ_list'
    }
    return render(request, 'dashboard/organ/add.html', context)

@login_required
def organ_edit(request, organ_id):
    """编辑机构"""
    organ = get_object_or_404(Organ, id=organ_id)
    
    if request.method == 'POST':
        # 获取表单数据
        code = request.POST.get('code')
        name = request.POST.get('name')
        organ_type = request.POST.get('organ_type')
        address = request.POST.get('address')
        contact_person = request.POST.get('contact_person')
        contact_phone = request.POST.get('contact_phone')
        description = request.POST.get('description')
        
        try:
            # 更新机构信息
            organ.code = code
            organ.name = name
            organ.organ_type = organ_type
            organ.address = address
            organ.contact_person = contact_person
            organ.contact_phone = contact_phone
            organ.description = description
            organ.save()
            
            messages.success(request, f'机构 {organ.name} 更新成功！')
            return redirect('dashboard:organ_detail', organ_id=organ.id)
        except Exception as e:
            messages.error(request, f'更新机构失败：{str(e)}')
            return redirect('dashboard:organ_edit', organ_id=organ.id)
    
    # GET 请求，显示表单
    context = {
        'organ': organ,
        'organ_types': Organ.ORGAN_TYPES,
        'active_menu': 'organ_list'
    }
    return render(request, 'dashboard/organ/edit.html', context)

@login_required
def project_add(request):
    """添加项目"""
    if request.method == 'POST':
        # 获取表单数据
        code = request.POST.get('code')
        name = request.POST.get('name')
        project_type = request.POST.get('project_type')
        lead_organ_id = request.POST.get('lead_organ')
        manager_id = request.POST.get('manager')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget')
        description = request.POST.get('description')
        remarks = request.POST.get('remarks')
        
        try:
            # 获取关联对象
            lead_organ = Organ.objects.get(id=lead_organ_id)
            manager = Staff.objects.get(id=manager_id)
            
            # 创建新项目
            project = Project.objects.create(
                code=code,
                name=name,
                project_type=project_type,
                lead_organ=lead_organ,
                manager=manager,
                start_date=start_date,
                end_date=end_date,
                budget=budget,
                description=description,
                remarks=remarks,
                status='draft'  # 默认状态为草稿
            )
            messages.success(request, f'项目 {project.name} 创建成功！')
            return redirect('dashboard:project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'创建项目失败：{str(e)}')
            return redirect('dashboard:project_add')
    
    # GET 请求，显示表单
    context = {
        'project_types': Project.PROJECT_TYPES,
        'project_status': Project.STATUS_CHOICES,
        'organs': Organ.objects.all().order_by('name'),
        'staffs': Staff.objects.filter(is_active=True).select_related('department').order_by('name'),
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/add.html', context)

@login_required
def project_edit(request, project_id):
    """编辑项目"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        # 获取表单数据
        code = request.POST.get('code')
        name = request.POST.get('name')
        project_type = request.POST.get('project_type')
        lead_organ_id = request.POST.get('lead_organ')
        manager_id = request.POST.get('manager')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget')
        status = request.POST.get('status')
        description = request.POST.get('description')
        remarks = request.POST.get('remarks')
        
        try:
            # 获取关联对象
            lead_organ = Organ.objects.get(id=lead_organ_id)
            manager = Staff.objects.get(id=manager_id)
            
            # 更新项目信息
            project.code = code
            project.name = name
            project.project_type = project_type
            project.lead_organ = lead_organ
            project.manager = manager
            project.start_date = start_date
            project.end_date = end_date
            project.budget = budget
            project.status = status
            project.description = description
            project.remarks = remarks
            project.save()
            
            messages.success(request, f'项目 {project.name} 更新成功！')
            return redirect('dashboard:project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'更新项目失败：{str(e)}')
            return redirect('dashboard:project_edit', project_id=project.id)
    
    # GET 请求，显示表单
    context = {
        'project': project,
        'project_types': Project.PROJECT_TYPES,
        'project_status': Project.STATUS_CHOICES,
        'organs': Organ.objects.all().order_by('name'),
        'staffs': Staff.objects.filter(is_active=True).select_related('department').order_by('name'),
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/edit.html', context)

@login_required
def contract_add(request):
    """添加合同"""
    if request.method == 'POST':
        # 获取表单数据
        contract_number = request.POST.get('contract_number')
        title = request.POST.get('title')
        contract_type_id = request.POST.get('contract_type')
        project_id = request.POST.get('project')
        party_a_id = request.POST.get('party_a')
        party_b_id = request.POST.get('party_b')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        content = request.POST.get('content')
        responsible_person_id = request.POST.get('responsible_person')
        remarks = request.POST.get('remarks')
        
        try:
            # 获取关联对象
            contract_type = ContractType.objects.get(id=contract_type_id)
            project = Project.objects.get(id=project_id)
            party_a = Organ.objects.get(id=party_a_id)
            party_b = Organ.objects.get(id=party_b_id)
            responsible_person = User.objects.get(id=responsible_person_id)
            
            # 创建新合同
            contract = Contract.objects.create(
                contract_number=contract_number,
                title=title,
                contract_type=contract_type,
                project=project,
                party_a=party_a,
                party_b=party_b,
                amount=amount,
                start_date=start_date,
                end_date=end_date,
                content=content,
                responsible_person=responsible_person,
                remarks=remarks,
                status='draft'  # 默认状态为草稿
            )
            
            # 处理附件
            if request.FILES.get('attachment'):
                contract.attachment = request.FILES['attachment']
                contract.save()
            
            # 创建合同事件记录
            ContractEvent.objects.create(
                contract=contract,
                event_type='create',
                description='创建合同',
                operator=request.user
            )
            
            messages.success(request, f'合同 {contract.title} 创建成功！')
            return redirect('dashboard:contract_detail', contract_id=contract.id)
        except Exception as e:
            messages.error(request, f'创建合同失败：{str(e)}')
            return redirect('dashboard:contract_add')
    
    # GET 请求，显示表单
    context = {
        'contract_types': ContractType.objects.all().order_by('name'),
        'projects': Project.objects.all().order_by('-created_at'),
        'organs': Organ.objects.all().order_by('name'),
        'users': User.objects.filter(is_active=True).order_by('username'),
        'active_menu': 'contract_list'
    }
    return render(request, 'dashboard/contract/add.html', context)

@login_required
def contract_edit(request, contract_id):
    """编辑合同"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        # 获取表单数据
        contract_number = request.POST.get('contract_number')
        title = request.POST.get('title')
        contract_type_id = request.POST.get('contract_type')
        project_id = request.POST.get('project')
        party_a_id = request.POST.get('party_a')
        party_b_id = request.POST.get('party_b')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status')
        content = request.POST.get('content')
        responsible_person_id = request.POST.get('responsible_person')
        remarks = request.POST.get('remarks')
        
        try:
            # 获取关联对象
            contract_type = ContractType.objects.get(id=contract_type_id)
            project = Project.objects.get(id=project_id)
            party_a = Organ.objects.get(id=party_a_id)
            party_b = Organ.objects.get(id=party_b_id)
            responsible_person = User.objects.get(id=responsible_person_id)
            
            # 更新合同信息
            contract.contract_number = contract_number
            contract.title = title
            contract.contract_type = contract_type
            contract.project = project
            contract.party_a = party_a
            contract.party_b = party_b
            contract.amount = amount
            contract.start_date = start_date
            contract.end_date = end_date
            contract.status = status
            contract.content = content
            contract.responsible_person = responsible_person
            contract.remarks = remarks
            
            # 处理附件
            if request.FILES.get('attachment'):
                contract.attachment = request.FILES['attachment']
            
            contract.save()
            
            # 创建合同事件记录
            ContractEvent.objects.create(
                contract=contract,
                event_type='update',
                description='更新合同信息',
                operator=request.user
            )
            
            messages.success(request, f'合同 {contract.title} 更新成功！')
            return redirect('dashboard:contract_detail', contract_id=contract.id)
        except Exception as e:
            messages.error(request, f'更新合同失败：{str(e)}')
            return redirect('dashboard:contract_edit', contract_id=contract.id)
    
    # GET 请求，显示表单
    context = {
        'contract': contract,
        'contract_types': ContractType.objects.all().order_by('name'),
        'contract_status': Contract.STATUS_CHOICES,
        'projects': Project.objects.all().order_by('-created_at'),
        'organs': Organ.objects.all().order_by('name'),
        'users': User.objects.filter(is_active=True).order_by('username'),
        'active_menu': 'contract_list'
    }
    return render(request, 'dashboard/contract/edit.html', context)

@login_required
def project_participants(request, project_id):
    """项目参与人员列表"""
    project = get_object_or_404(Project, id=project_id)
    
    # 获取过滤参数
    search = request.GET.get('search', '')
    role = request.GET.get('role', '')
    department_id = request.GET.get('department', '')
    is_active = request.GET.get('is_active', '')
    
    # 构建查询条件
    participations = project.projectparticipation_set.select_related('staff', 'staff__department')
    
    if search:
        participations = participations.filter(
            Q(staff__name__icontains=search) | Q(staff__code__icontains=search)
        )
    if role:
        participations = participations.filter(role=role)
    if department_id:
        participations = participations.filter(staff__department_id=department_id)
    if is_active:
        participations = participations.filter(is_active=is_active == '1')
    
    # 分页
    paginator = Paginator(participations.order_by('-is_active', 'staff__name'), 10)
    page = request.GET.get('page')
    participations = paginator.get_page(page)
    
    context = {
        'project': project,
        'participations': participations,
        'role_choices': ProjectParticipation.ROLE_CHOICES,
        'departments': Department.objects.all(),
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/participants.html', context)

@login_required
def project_participant_detail(request, project_id, participation_id):
    """项目参与人员详情"""
    project = get_object_or_404(Project, id=project_id)
    participation = get_object_or_404(ProjectParticipation, id=participation_id, project=project)
    
    context = {
        'project': project,
        'participation': participation,
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/participant_detail.html', context)

@login_required
def project_participant_add(request, project_id):
    """添加项目参与人员"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff')
        role = request.POST.get('role')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or None
        workload = request.POST.get('workload') or None
        responsibility = request.POST.get('responsibility')
        
        try:
            staff = Staff.objects.get(id=staff_id)
            
            # 检查是否已经在项目中
            if ProjectParticipation.objects.filter(project=project, staff=staff, is_active=True).exists():
                messages.error(request, f'{staff.name} 已经是项目成员')
                return redirect('dashboard:project_participant_add', project_id=project.id)
            
            participation = ProjectParticipation.objects.create(
                project=project,
                staff=staff,
                role=role,
                start_date=start_date,
                end_date=end_date,
                workload=workload,
                responsibility=responsibility,
                created_by=request.user
            )
            
            messages.success(request, f'已将 {staff.name} 添加到项目')
            return redirect('dashboard:project_participants', project_id=project.id)
            
        except Exception as e:
            messages.error(request, f'添加项目成员失败：{str(e)}')
            return redirect('dashboard:project_participant_add', project_id=project.id)
    
    # 获取可选的人员列表（排除已经在项目中的人员）
    existing_staff_ids = project.participants.filter(projectparticipation__is_active=True).values_list('id', flat=True)
    available_staff = Staff.objects.exclude(id__in=existing_staff_ids).filter(is_active=True)
    
    context = {
        'project': project,
        'available_staff': available_staff,
        'role_choices': ProjectParticipation.ROLE_CHOICES,
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/participant_add.html', context)

@login_required
def project_participant_edit(request, project_id, participation_id):
    """编辑项目参与人员"""
    project = get_object_or_404(Project, id=project_id)
    participation = get_object_or_404(ProjectParticipation, id=participation_id, project=project)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or None
        workload = request.POST.get('workload') or None
        responsibility = request.POST.get('responsibility')
        performance = request.POST.get('performance')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            participation.role = role
            participation.start_date = start_date
            participation.end_date = end_date
            participation.workload = workload
            participation.responsibility = responsibility
            participation.performance = performance
            participation.is_active = is_active
            participation.save()
            
            messages.success(request, f'更新 {participation.staff.name} 的信息')
            return redirect('dashboard:project_participants', project_id=project.id)
            
        except Exception as e:
            messages.error(request, f'更新项目成员失败：{str(e)}')
            return redirect('dashboard:project_participant_edit', project_id=project.id, participation_id=participation_id)
    
    context = {
        'project': project,
        'participation': participation,
        'role_choices': ProjectParticipation.ROLE_CHOICES,
        'active_menu': 'project_list'
    }
    return render(request, 'dashboard/project/participant_edit.html', context)

@login_required
def project_participant_remove(request, project_id, participation_id):
    """移除项目参与人员"""
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        participation = get_object_or_404(ProjectParticipation, id=participation_id, project=project)
        
        try:
            participation.is_active = False
            participation.end_date = timezone.now().date()
            participation.save()
            
            messages.success(request, f'已将 {participation.staff.name} 从项目中移除')
        except Exception as e:
            messages.error(request, f'移除项目成员失败：{str(e)}')
    
    return redirect('dashboard:project_participants', project_id=project_id)

# 预算管理视图
@login_required
def budget_list(request):
    """预算列表"""
    # 获取筛选参数
    project_id = request.GET.get('project', '')
    year = request.GET.get('year', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')

    # 构建查询
    budgets = Budget.objects.all()
    
    if project_id:
        budgets = budgets.filter(project_id=project_id)
    
    if year:
        budgets = budgets.filter(created_at__year=year)
    
    if status:
        budgets = budgets.filter(status=status)
    
    if search:
        budgets = budgets.filter(
            Q(project__name__icontains=search) |
            Q(project__code__icontains=search)
        )
    
    # 排序
    if sort:
        budgets = budgets.order_by(sort)

    # 统计信息
    stats = {
        'total_count': budgets.count(),
        'total_amount': budgets.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'approved_count': budgets.filter(status='approved').count(),
        'pending_count': budgets.filter(status='pending').count(),
    }

    # 获取所有项目，用于筛选
    projects = Project.objects.all()
    
    # 获取年份列表
    years = Budget.objects.dates('created_at', 'year', order='DESC')
    
    # 状态选项
    status_choices = Budget.STATUS_CHOICES

    # 分页
    paginator = Paginator(budgets, 10)
    page = request.GET.get('page')
    try:
        budgets = paginator.page(page)
    except PageNotAnInteger:
        budgets = paginator.page(1)
    except EmptyPage:
        budgets = paginator.page(paginator.num_pages)

    # 构建查询字符串，用于分页
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    context = {
        'budgets': budgets,
        'stats': stats,
        'projects': projects,
        'years': years,
        'status_choices': status_choices,
        'filters': {
            'project': project_id,
            'year': year,
            'status': status,
            'search': search,
            'sort': sort,
        },
        'query_string': query_string,
        'active_menu': 'budget_list'
    }
    
    return render(request, 'dashboard/finance/budget_list.html', context)

@login_required
def budget_detail(request, budget_id):
    """预算详情"""
    budget = get_object_or_404(Budget, id=budget_id)
    expenses = budget.expense_set.all().order_by('-date')
    context = {
        'budget': budget,
        'expenses': expenses,
        'active_menu': 'budget_list'
    }
    return render(request, 'dashboard/finance/budget_detail.html', context)

@login_required
def budget_add(request):
    """添加预算"""
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.created_by = request.user
            budget.save()
            messages.success(request, f'预算创建成功！')
            return redirect('dashboard:budget_detail', budget_id=budget.id)
    else:
        form = BudgetForm()
    
    context = {
        'form': form,
        'active_menu': 'budget_list'
    }
    return render(request, 'dashboard/finance/budget_add.html', context)

@login_required
def budget_edit(request, budget_id):
    """编辑预算"""
    budget = get_object_or_404(Budget, id=budget_id)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, f'预算更新成功！')
            return redirect('dashboard:budget_detail', budget_id=budget.id)
    else:
        form = BudgetForm(instance=budget)
    
    context = {
        'form': form,
        'budget': budget,
        'active_menu': 'budget_list'
    }
    return render(request, 'dashboard/finance/budget_edit.html', context)

# 收入管理视图
@login_required
def income_list(request):
    projects = Project.objects.all()
    incomes = Income.objects.select_related('project', 'created_by').all()
    
    # 筛选条件
    project_id = request.GET.get('project')
    category = request.GET.get('category')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if project_id:
        incomes = incomes.filter(project_id=project_id)
    if category:
        incomes = incomes.filter(category=category)
    if status:
        incomes = incomes.filter(status=status)
    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)
        
    # 分页
    paginator = Paginator(incomes, 10)
    page = request.GET.get('page')
    incomes = paginator.get_page(page)
    
    context = {
        'projects': projects,
        'incomes': incomes,
        'income_categories': Income.CATEGORY_CHOICES,
        'income_status': Income.STATUS_CHOICES,
        'total_amount': Income.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'confirmed_amount': Income.objects.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0,
        'pending_amount': Income.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'dashboard/finance/income_list.html', context)

@login_required
def income_detail(request, pk):
    income = get_object_or_404(Income, pk=pk)
    context = {'income': income}
    return render(request, 'dashboard/finance/income_detail.html', context)

@login_required
def income_add(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, request.FILES)
        if form.is_valid():
            income = form.save(commit=False)
            income.created_by = request.user
            income.save()
            messages.success(request, '收入记录创建成功')
            return redirect('dashboard:income_detail', pk=income.pk)
    else:
        form = IncomeForm()
    
    context = {
        'form': form,
        'projects': Project.objects.all(),
        'income_categories': Income.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/finance/income_edit.html', context)

@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        form = IncomeForm(request.POST, request.FILES, instance=income)
        if form.is_valid():
            income = form.save()
            messages.success(request, '收入记录更新成功')
            return redirect('dashboard:income_detail', pk=income.pk)
    else:
        form = IncomeForm(instance=income)
    
    context = {
        'form': form,
        'income': income,
        'projects': Project.objects.all(),
        'income_categories': Income.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/finance/income_edit.html', context)

@login_required
def income_confirm(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        income.status = 'confirmed'
        income.confirm_date = timezone.now()
        income.confirm_remarks = request.POST.get('confirm_remarks')
        income.save()
        messages.success(request, '收入已确认')
    return redirect('dashboard:income_detail', pk=pk)

@login_required
def income_cancel(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if request.method == 'POST':
        income.status = 'cancelled'
        income.cancel_reason = request.POST.get('cancel_reason')
        income.save()
        messages.success(request, '收入已取消')
    return redirect('dashboard:income_detail', pk=pk)

@login_required
def income_delete_attachment(request, pk):
    income = get_object_or_404(Income, pk=pk)
    if income.attachment:
        income.attachment.delete()
        messages.success(request, '附件已删除')
    return redirect('dashboard:income_detail', pk=pk)

# 支出管理视图
@login_required
def expense_list(request):
    projects = Project.objects.all()
    expenses = Expense.objects.select_related('project', 'budget', 'created_by').all()
    
    # 筛选条件
    project_id = request.GET.get('project')
    category = request.GET.get('category')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if project_id:
        expenses = expenses.filter(project_id=project_id)
    if category:
        expenses = expenses.filter(category=category)
    if status:
        expenses = expenses.filter(status=status)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
        
    # 分页
    paginator = Paginator(expenses, 10)
    page = request.GET.get('page')
    expenses = paginator.get_page(page)
    
    context = {
        'projects': projects,
        'expenses': expenses,
        'expense_categories': Expense.CATEGORY_CHOICES,
        'expense_status': Expense.STATUS_CHOICES,
        'total_amount': Expense.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'approved_amount': Expense.objects.filter(status='approved').aggregate(total=Sum('amount'))['total'] or 0,
        'pending_amount': Expense.objects.filter(status='submitted').aggregate(total=Sum('amount'))['total'] or 0,
        'rejected_amount': Expense.objects.filter(status='rejected').aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'dashboard/finance/expense_list.html', context)

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    context = {'expense': expense}
    return render(request, 'dashboard/finance/expense_detail.html', context)

@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, '支出记录创建成功')
            return redirect('dashboard:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm()
    
    context = {
        'form': form,
        'projects': Project.objects.all(),
        'expense_categories': Expense.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/finance/expense_edit.html', context)

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            expense = form.save()
            messages.success(request, '支出记录更新成功')
            return redirect('dashboard:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    
    context = {
        'form': form,
        'expense': expense,
        'projects': Project.objects.all(),
        'expense_categories': Expense.CATEGORY_CHOICES,
    }
    return render(request, 'dashboard/finance/expense_edit.html', context)

@login_required
def expense_submit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.status = 'submitted'
        expense.submit_date = timezone.now()
        expense.submit_remarks = request.POST.get('submit_remarks')
        expense.save()
        messages.success(request, '支出已提交审批')
    return redirect('dashboard:expense_detail', pk=pk)

@login_required
def expense_approve(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST' and request.user.is_staff:
        expense.status = 'approved'
        expense.approve_date = timezone.now()
        expense.approver = request.user
        expense.approve_remarks = request.POST.get('approve_remarks')
        expense.save()
        
        # 更新预算使用金额
        budget = expense.budget
        budget.used_amount = budget.used_amount + expense.amount
        budget.save()
        
        messages.success(request, '支出已批准')
    return redirect('dashboard:expense_detail', pk=pk)

@login_required
def expense_reject(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST' and request.user.is_staff:
        expense.status = 'rejected'
        expense.approve_date = timezone.now()
        expense.approver = request.user
        expense.approve_remarks = request.POST.get('reject_reason')
        expense.save()
        messages.success(request, '支出已拒绝')
    return redirect('dashboard:expense_detail', pk=pk)

@login_required
def expense_delete_attachment(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if expense.attachment:
        expense.attachment.delete()
        messages.success(request, '附件已删除')
    return redirect('dashboard:expense_detail', pk=pk)

@login_required
def contract_statistics(request):
    """合同统计分析"""
    # 获取筛选参数
    time_range = request.GET.get('time_range', '30')
    contract_type_id = request.GET.get('contract_type')
    status = request.GET.get('status')
    amount_range = request.GET.get('amount_range')

    # 基础查询集
    contracts = Contract.objects.all()

    # 应用时间筛选
    if time_range != 'custom':
        days = int(time_range)
        start_date = timezone.now() - timezone.timedelta(days=days)
        contracts = contracts.filter(created_at__gte=start_date)

    # 应用合同类型筛选
    if contract_type_id:
        contracts = contracts.filter(contract_type_id=contract_type_id)

    # 应用状态筛选
    if status:
        contracts = contracts.filter(status=status)

    # 应用金额范围筛选
    if amount_range:
        if amount_range == '0-100000':
            contracts = contracts.filter(amount__lt=100000)
        elif amount_range == '100000-500000':
            contracts = contracts.filter(amount__gte=100000, amount__lt=500000)
        elif amount_range == '500000-1000000':
            contracts = contracts.filter(amount__gte=500000, amount__lt=1000000)
        elif amount_range == '1000000+':
            contracts = contracts.filter(amount__gte=1000000)

    # 计算统计数据
    total_contracts = contracts.count()
    total_amount = contracts.aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_new = contracts.filter(
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month
    ).count()
    pending_review = contracts.filter(status='pending').count()

    # 准备图表数据
    # 1. 合同类型分布
    type_data = list(contracts.values('contract_type__name')
                    .annotate(count=Count('id'))
                    .values_list('count', flat=True))
    type_labels = list(contracts.values('contract_type__name')
                      .annotate(count=Count('id'))
                      .values_list('contract_type__name', flat=True))

    # 2. 合同金额趋势（最近12个月）
    amount_data = []
    amount_labels = []
    for i in range(11, -1, -1):
        date = timezone.now() - timezone.timedelta(days=i*30)
        month_amount = contracts.filter(
            created_at__year=date.year,
            created_at__month=date.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        amount_data.append(float(month_amount))
        amount_labels.append(date.strftime('%Y-%m'))

    # 3. 合同状态分布
    status_data = list(contracts.values('status')
                      .annotate(count=Count('id'))
                      .values_list('count', flat=True))
    status_labels = list(contracts.values('status')
                        .annotate(count=Count('id'))
                        .values_list('status', flat=True))
    status_labels = [dict(Contract.STATUS_CHOICES)[s] for s in status_labels]

    # 4. 项目合同分布（前10个项目）
    project_data = list(contracts.values('project__name')
                       .annotate(count=Count('id'))
                       .order_by('-count')[:10]
                       .values_list('count', flat=True))
    project_labels = list(contracts.values('project__name')
                         .annotate(count=Count('id'))
                         .order_by('-count')[:10]
                         .values_list('project__name', flat=True))

    context = {
        'time_range': time_range,
        'selected_type': contract_type_id,
        'selected_status': status,
        'amount_range': amount_range,
        'contract_types': ContractType.objects.all(),
        'status_choices': Contract.STATUS_CHOICES,
        'total_contracts': total_contracts,
        'total_amount': total_amount,
        'monthly_new': monthly_new,
        'pending_review': pending_review,
        'type_data': type_data,
        'type_labels': type_labels,
        'amount_data': amount_data,
        'amount_labels': amount_labels,
        'status_data': status_data,
        'status_labels': status_labels,
        'project_data': project_data,
        'project_labels': project_labels,
    }

    return render(request, 'dashboard/contract/statistics.html', context)

@login_required
def contract_export(request):
    """导出合同数据"""
    # 获取筛选后的合同数据
    contracts = Contract.objects.all()
    
    # 应用与统计页面相同的筛选逻辑
    time_range = request.GET.get('time_range')
    if time_range and time_range != 'custom':
        days = int(time_range)
        start_date = timezone.now() - timezone.timedelta(days=days)
        contracts = contracts.filter(created_at__gte=start_date)

    contract_type_id = request.GET.get('contract_type')
    if contract_type_id:
        contracts = contracts.filter(contract_type_id=contract_type_id)

    status = request.GET.get('status')
    if status:
        contracts = contracts.filter(status=status)

    amount_range = request.GET.get('amount_range')
    if amount_range:
        if amount_range == '0-100000':
            contracts = contracts.filter(amount__lt=100000)
        elif amount_range == '100000-500000':
            contracts = contracts.filter(amount__gte=100000, amount__lt=500000)
        elif amount_range == '500000-1000000':
            contracts = contracts.filter(amount__gte=500000, amount__lt=1000000)
        elif amount_range == '1000000+':
            contracts = contracts.filter(amount__gte=1000000)

    # 创建响应对象
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contracts.csv"'
    
    # 写入CSV头部
    writer = csv.writer(response)
    writer.writerow([
        '合同编号', '合同标题', '合同类型', '关联项目', 
        '甲方', '乙方', '金额', '开始日期', '结束日期',
        '状态', '创建时间', '更新时间'
    ])
    
    # 写入数据
    for contract in contracts:
        writer.writerow([
            contract.contract_number,
            contract.title,
            contract.contract_type.name,
            contract.project.name,
            contract.party_a.name,
            contract.party_b.name,
            float(contract.amount),
            contract.start_date,
            contract.end_date,
            dict(Contract.STATUS_CHOICES)[contract.status],
            timezone.localtime(contract.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            timezone.localtime(contract.updated_at).strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
def project_archive(request, pk):
    """项目归档"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        project.archive(request.user, reason)
        messages.success(request, f'项目 {project.name} 已成功归档')
        return redirect('dashboard:project_detail', pk=pk)
    
    return render(request, 'dashboard/project/archive_confirm.html', {
        'project': project
    })

@login_required
def project_unarchive(request, pk):
    """取消项目归档"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.unarchive()
        messages.success(request, f'项目 {project.name} 已取消归档')
        return redirect('dashboard:project_detail', pk=pk)
    
    return render(request, 'dashboard/project/unarchive_confirm.html', {
        'project': project
    })

@login_required
def archived_projects(request):
    """已归档项目列表"""
    projects = Project.objects.filter(is_archived=True)
    
    # 搜索过滤
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 排序
    sort = request.GET.get('sort', '-archived_at')
    projects = projects.order_by(sort)
    
    # 分页
    paginator = Paginator(projects, 10)
    page = request.GET.get('page')
    projects = paginator.get_page(page)
    
    return render(request, 'dashboard/project/archived_list.html', {
        'projects': projects,
        'search_query': search_query,
        'sort': sort
    })
