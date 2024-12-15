from django import forms
from finance.models import Budget, Income, Expense

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'project', 'total_amount',
            'equipment_amount', 'material_amount', 'test_amount',
            'fuel_amount', 'travel_amount', 'conference_amount',
            'international_amount', 'labor_amount', 'expert_amount',
            'other_amount', 'indirect_amount'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipment_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'material_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'test_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'travel_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'conference_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'international_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'labor_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expert_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'indirect_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get('total_amount')
        if total_amount:
            # 检查各项金额之和是否等于总金额
            amounts = [
                cleaned_data.get('equipment_amount', 0),
                cleaned_data.get('material_amount', 0),
                cleaned_data.get('test_amount', 0),
                cleaned_data.get('fuel_amount', 0),
                cleaned_data.get('travel_amount', 0),
                cleaned_data.get('conference_amount', 0),
                cleaned_data.get('international_amount', 0),
                cleaned_data.get('labor_amount', 0),
                cleaned_data.get('expert_amount', 0),
                cleaned_data.get('other_amount', 0),
                cleaned_data.get('indirect_amount', 0),
            ]
            total = sum(amount for amount in amounts if amount)
            if total != total_amount:
                raise forms.ValidationError('各项金额之和必须等于总金额')
        return cleaned_data

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            'project', 'amount', 'date', 'category',
            'description', 'attachment', 'remarks'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'project', 'budget', 'amount', 'date', 'category',
            'description', 'payee', 'bank_account', 'bank_name',
            'invoice_number', 'invoice_date', 'attachment', 'remarks'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'budget': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'payee': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.project:
            # 如果是编辑现有支出，只显示该项目的预算
            self.fields['budget'].queryset = Budget.objects.filter(project=self.instance.project) 