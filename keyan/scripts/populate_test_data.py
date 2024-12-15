import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keyan.settings')
django.setup()

from django.contrib.auth.models import User
from organ.models import Organ, Department, Staff
from project.models import Project, ProjectParticipation
from contact.models import ContractType, Contract, ContractEvent
from finance.models import Budget, Income, Expense

def create_users():
    """创建测试用户"""
    print("创建测试用户...")
    users = []
    for i in range(1, 6):
        username = f'user{i}'
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                password='password123',
                first_name=f'名{i}',
                last_name=f'姓{i}',
                email=f'user{i}@example.com'
            )
            users.append(user)
            print(f"创建用户: {username}")
        else:
            user = User.objects.get(username=username)
            users.append(user)
            print(f"已存在用户: {username}")
    return users

def create_organs():
    """创建测试机构"""
    print("\n创建测试机构...")
    organs = []
    organ_types = ['university', 'enterprise', 'research', 'government', 'other']
    for i in range(1, 6):
        name = f'测试机构{i}'
        if not Organ.objects.filter(name=name).exists():
            organ = Organ.objects.create(
                name=name,
                code=f'ORG{i:03d}',
                organ_type=random.choice(organ_types),
                address=f'测试地址{i}',
                contact_person=f'联系人{i}',
                contact_phone=f'1380000{i:04d}',
                email=f'org{i}@example.com',
                description=f'这是测试机构{i}的描述信息'
            )
            organs.append(organ)
            print(f"创建机构: {name}")
        else:
            organ = Organ.objects.get(name=name)
            organs.append(organ)
            print(f"已存在机构: {name}")
    
    if not organs:
        # 如果没有创建任何机构，创建一个默认机构
        default_organ = Organ.objects.create(
            name='默认机构',
            code='ORG000',
            organ_type='other',
            description='这是默认机构'
        )
        organs.append(default_organ)
        print(f"创建默认机构: {default_organ.name}")
    
    return organs

def create_departments(organs):
    """创建测试部门"""
    print("\n创建测试部门...")
    departments = []
    for organ in organs:
        for i in range(1, 4):
            name = f'{organ.name}部门{i}'
            code = f'DEPT{organ.id:02d}{i:02d}'
            if not Department.objects.filter(organ=organ, code=code).exists():
                department = Department.objects.create(
                    name=name,
                    code=code,
                    organ=organ,
                    description=f'这是{name}的描述信息'
                )
                departments.append(department)
                print(f"创建部门: {name}")
            else:
                department = Department.objects.get(organ=organ, code=code)
                departments.append(department)
                print(f"已存在部门: {name}")
    return departments

def create_staff(users, organs, departments):
    """创建测试人员"""
    print("\n创建测试人员...")
    staff_list = []
    titles = ['professor', 'associate_professor', 'lecturer', 'researcher', 'engineer']
    
    # 确保每个机构至少有一个部门
    organ_departments = {}
    for organ in organs:
        organ_deps = [d for d in departments if d.organ == organ]
        if not organ_deps:
            # 如果机构没有部门，创建一个默认部门
            default_dep = Department.objects.create(
                name=f'{organ.name}默认部门',
                code=f'DEPT{organ.id:02d}00',
                organ=organ,
                description=f'这是{organ.name}的默认部门'
            )
            departments.append(default_dep)
            organ_deps = [default_dep]
        organ_departments[organ.id] = organ_deps

    # 确保每个用户都被分配到一个部门
    for i, user in enumerate(users):
        # 轮流选择机构，确保均匀分布
        organ = organs[i % len(organs)]
        department = random.choice(organ_departments[organ.id])
        
        if not Staff.objects.filter(user=user).exists():
            staff = Staff.objects.create(
                user=user,
                name=f"{user.last_name}{user.first_name}",
                organ=organ,
                department=department,
                gender=random.choice(['M', 'F']),
                title=random.choice(titles),
                phone=f'1390000{user.id:04d}',
                email=user.email,
                entry_date=datetime.now().date() - timedelta(days=random.randint(0, 365))
            )
            staff_list.append(staff)
            print(f"创建人员: {staff.name}")
        else:
            staff = Staff.objects.get(user=user)
            staff_list.append(staff)
            print(f"已存在人员: {staff.name}")
    
    if not staff_list:
        raise ValueError("没有成功创建任何员工！")
        
    return staff_list

def create_projects(organs, staff_list):
    """创建测试项目"""
    print("\n创建测试项目...")
    projects = []
    project_types = ['research', 'development', 'consulting', 'other']
    statuses = ['draft', 'pending', 'active', 'completed', 'cancelled']
    for i in range(1, 6):
        name = f'测试项目{i}'
        if not Project.objects.filter(name=name).exists():
            project = Project.objects.create(
                name=name,
                code=f'PRJ{i:03d}',
                project_type=random.choice(project_types),
                lead_organ=random.choice(organs),
                manager=random.choice(staff_list),
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=random.randint(30, 365)),
                budget=Decimal(random.randint(100000, 1000000)),
                status=random.choice(statuses),
                description=f'这是测试项目{i}的描述信息'
            )
            projects.append(project)
            print(f"创建项目: {name}")
    return projects

def create_project_participations(projects, staff_list):
    """创建测试项目参与记录"""
    print("\n创建测试项目参与记录...")
    roles = ['manager', 'leader', 'researcher', 'developer', 'consultant']
    for project in projects:
        # 为每个项目随机选择3-5名成员
        members = random.sample(staff_list, random.randint(3, 5))
        for staff in members:
            if not ProjectParticipation.objects.filter(project=project, staff=staff).exists():
                participation = ProjectParticipation.objects.create(
                    project=project,
                    staff=staff,
                    role=random.choice(roles),
                    start_date=project.start_date,
                    end_date=project.end_date if random.random() > 0.5 else None,
                    workload=Decimal(random.randint(1, 12)),
                    responsibility=f'负责{project.name}的相关工作',
                    created_by=staff.user
                )
                print(f"创建项目参与记录: {project.name} - {staff.name}")

def create_contract_types():
    """创建测试合同类型"""
    print("\n创建测试合同类型...")
    types = []
    type_names = ['技术开发', '技术服务', '技术咨询', '技术转让', '合作研发']
    for i, name in enumerate(type_names, 1):
        if not ContractType.objects.filter(name=name).exists():
            contract_type = ContractType.objects.create(
                name=name,
                code=f'CT{i:02d}',
                description=f'这是{name}合同的描述信息'
            )
            types.append(contract_type)
            print(f"创建合同类型: {name}")
    return types

def create_contracts(contract_types, projects, organs, users):
    """创建测试合同"""
    print("\n创建测试合同...")
    contracts = []
    statuses = ['draft', 'pending', 'active', 'completed', 'terminated']
    for i in range(1, 11):
        number = f'HT{datetime.now().year}{i:04d}'
        if not Contract.objects.filter(contract_number=number).exists():
            project = random.choice(projects)
            contract = Contract.objects.create(
                contract_number=number,
                title=f'测试合同{i}',
                contract_type=random.choice(contract_types),
                project=project,
                party_a=project.lead_organ,
                party_b=random.choice([org for org in organs if org != project.lead_organ]),
                amount=Decimal(random.randint(50000, 500000)),
                start_date=project.start_date,
                end_date=project.end_date,
                status=random.choice(statuses),
                content=f'这是测试合同{i}的内容',
                responsible_person=random.choice(users)
            )
            contracts.append(contract)
            print(f"创建合同: {contract.title}")
            
            # 创建合同事件
            ContractEvent.objects.create(
                contract=contract,
                event_type='create',
                description='创建合同',
                operator=contract.responsible_person
            )
    return contracts

def create_budgets(projects, users):
    """创建测试预算"""
    print("\n创建测试预算...")
    for project in projects:
        if not Budget.objects.filter(project=project).exists():
            total_amount = project.budget
            budget = Budget.objects.create(
                project=project,
                total_amount=total_amount,
                equipment_amount=total_amount * Decimal('0.2'),
                material_amount=total_amount * Decimal('0.1'),
                test_amount=total_amount * Decimal('0.1'),
                fuel_amount=total_amount * Decimal('0.05'),
                travel_amount=total_amount * Decimal('0.1'),
                conference_amount=total_amount * Decimal('0.05'),
                international_amount=total_amount * Decimal('0.1'),
                labor_amount=total_amount * Decimal('0.1'),
                expert_amount=total_amount * Decimal('0.1'),
                other_amount=total_amount * Decimal('0.05'),
                indirect_amount=total_amount * Decimal('0.05'),
                created_by=random.choice(users)
            )
            print(f"创建预算: {project.name}")

def create_incomes(projects, users):
    """创建测试收入记录"""
    print("\n创建测试收入...")
    categories = ['funding', 'contract', 'consulting', 'other']
    statuses = ['draft', 'pending', 'confirmed', 'cancelled']
    for project in projects:
        # 为每个项目创建2-4条收入记录
        for i in range(random.randint(2, 4)):
            income = Income.objects.create(
                project=project,
                category=random.choice(categories),
                amount=Decimal(random.randint(10000, 100000)),
                date=datetime.now().date() - timedelta(days=random.randint(0, 180)),
                status=random.choice(statuses),
                description=f'{project.name}的收入记录{i+1}',
                created_by=random.choice(users)
            )
            print(f"创建收入记录: {project.name} - {income.amount}")

def create_expenses(projects, users):
    """���建测试支出记录"""
    print("\n创建测试支出...")
    categories = ['equipment', 'material', 'testing', 'travel', 'meeting']
    statuses = ['draft', 'submitted', 'approved', 'rejected']
    for project in projects:
        budget = Budget.objects.get(project=project)
        # 为每个项目创建3-6条支出记录
        for i in range(random.randint(3, 6)):
            expense = Expense.objects.create(
                project=project,
                budget=budget,
                category=random.choice(categories),
                amount=Decimal(random.randint(5000, 50000)),
                date=datetime.now().date() - timedelta(days=random.randint(0, 180)),
                status=random.choice(statuses),
                description=f'{project.name}的支出记录{i+1}',
                created_by=random.choice(users)
            )
            print(f"创建支出记录: {project.name} - {expense.amount}")

def main():
    """主函数"""
    print("开始创建测试数据...")
    
    users = create_users()
    organs = create_organs()
    departments = create_departments(organs)
    staff_list = create_staff(users, organs, departments)
    projects = create_projects(organs, staff_list)
    create_project_participations(projects, staff_list)
    contract_types = create_contract_types()
    contracts = create_contracts(contract_types, projects, organs, users)
    create_budgets(projects, users)
    create_incomes(projects, users)
    create_expenses(projects, users)
    
    print("\n测试数据创建完成！")

if __name__ == '__main__':
    main() 