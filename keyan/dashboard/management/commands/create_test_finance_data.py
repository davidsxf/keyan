from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from project.models import Project
from finance.models import Budget, Income, Expense
from decimal import Decimal
import random
from datetime import timedelta

class Command(BaseCommand):
    help = '创建财务测试数据（预算、收入、支出）'

    def handle(self, *args, **kwargs):
        # 确保至少有一个管理员用户
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        # 获取所有项目
        projects = Project.objects.all()
        if not projects.exists():
            self.stdout.write(self.style.ERROR('没有找到任何项目，请先创建项目'))
            return

        # 为每个项目创建预算
        for project in projects:
            # 创建预算
            total_amount = Decimal(str(random.randint(1000000, 10000000)))  # 100-1000万
            equipment_ratio = Decimal('0.3')  # 设备费占比30%
            material_ratio = Decimal('0.15')  # 材料费占比15%
            test_ratio = Decimal('0.1')  # 测试费占比10%
            fuel_ratio = Decimal('0.05')  # 燃料费占比5%
            travel_ratio = Decimal('0.1')  # 差旅费占比10%
            conference_ratio = Decimal('0.05')  # 会议费占比5%
            international_ratio = Decimal('0.05')  # 国际合作费占比5%
            labor_ratio = Decimal('0.1')  # 劳务费占比10%
            expert_ratio = Decimal('0.05')  # 专家费占比5%
            other_ratio = Decimal('0.03')  # 其他费用占比3%
            indirect_ratio = Decimal('0.02')  # 间接费用占比2%

            budget = Budget.objects.create(
                project=project,
                total_amount=total_amount,
                equipment_amount=total_amount * equipment_ratio,
                material_amount=total_amount * material_ratio,
                test_amount=total_amount * test_ratio,
                fuel_amount=total_amount * fuel_ratio,
                travel_amount=total_amount * travel_ratio,
                conference_amount=total_amount * conference_ratio,
                international_amount=total_amount * international_ratio,
                labor_amount=total_amount * labor_ratio,
                expert_amount=total_amount * expert_ratio,
                other_amount=total_amount * other_ratio,
                indirect_amount=total_amount * indirect_ratio,
                created_by=admin_user
            )

            # 创建收入记录（3-5条）
            for _ in range(random.randint(3, 5)):
                income_amount = total_amount / Decimal('3')  # 平均分成3次拨款
                income_date = timezone.now() - timedelta(days=random.randint(0, 365))
                Income.objects.create(
                    project=project,
                    amount=income_amount,
                    category=random.choice(['grant', 'cooperation', 'other']),
                    date=income_date,
                    description=f'{project.name}项目第{_+1}笔拨款',
                    status=random.choice(['pending', 'confirmed', 'cancelled']),
                    created_by=admin_user
                )

            # 创建支出记录（5-10条）
            expense_types = [
                ('equipment', budget.equipment_amount, '设备费'),
                ('material', budget.material_amount, '材料费'),
                ('test', budget.test_amount, '测试化验加工费'),
                ('fuel', budget.fuel_amount, '燃料动力费'),
                ('travel', budget.travel_amount, '差旅费'),
                ('conference', budget.conference_amount, '会议费'),
                ('intl', budget.international_amount, '国际合作交流费'),
                ('labor', budget.labor_amount, '劳务费'),
                ('expert', budget.expert_amount, '专家咨询费'),
                ('other', budget.other_amount, '其他费用')
            ]

            for _ in range(random.randint(5, 10)):
                category_code, max_amount, category_name = random.choice(expense_types)
                expense_amount = max_amount * Decimal(str(random.uniform(0.1, 0.4)))  # 使用10%-40%的预算
                expense_date = timezone.now() - timedelta(days=random.randint(0, 365))
                
                Expense.objects.create(
                    project=project,
                    budget=budget,
                    amount=expense_amount,
                    category=category_code,
                    date=expense_date,
                    payee=f'供应商{random.randint(1, 10)}',
                    description=f'{project.name}项目{category_name}支出',
                    status=random.choice(['draft', 'submitted', 'approved', 'rejected']),
                    created_by=admin_user
                )

        self.stdout.write(self.style.SUCCESS('成功创建财务测试数据！')) 