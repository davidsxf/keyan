from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    
    # 项目管理
    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    
    # 机构管理
    path('organs/', views.organ_list, name='organ_list'),
    path('organs/add/', views.organ_add, name='organ_add'),
    path('organs/<int:organ_id>/', views.organ_detail, name='organ_detail'),
    path('organs/<int:organ_id>/edit/', views.organ_edit, name='organ_edit'),
    
    # 合同管理
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/add/', views.contract_add, name='contract_add'),
    path('contracts/<int:contract_id>/', views.contract_detail, name='contract_detail'),
    path('contracts/<int:contract_id>/edit/', views.contract_edit, name='contract_edit'),
    path('contracts/statistics/', views.contract_statistics, name='contract_statistics'),
    path('contracts/export/', views.contract_export, name='contract_export'),
    
    # 项目参与人员管理
    path('project/<int:project_id>/participants/', views.project_participants, name='project_participants'),
    path('project/<int:project_id>/participant/add/', views.project_participant_add, name='project_participant_add'),
    path('project/<int:project_id>/participant/<int:participation_id>/', views.project_participant_detail, name='project_participant_detail'),
    path('project/<int:project_id>/participant/<int:participation_id>/edit/', views.project_participant_edit, name='project_participant_edit'),
    path('project/<int:project_id>/participant/<int:participation_id>/remove/', views.project_participant_remove, name='project_participant_remove'),
    
    # 预算管理
    path('finance/budgets/', views.budget_list, name='budget_list'),
    path('finance/budgets/add/', views.budget_add, name='budget_add'),
    path('finance/budgets/<int:budget_id>/', views.budget_detail, name='budget_detail'),
    path('finance/budgets/<int:budget_id>/edit/', views.budget_edit, name='budget_edit'),
    
    # 收入管理
    path('finance/incomes/', views.income_list, name='income_list'),
    path('finance/incomes/add/', views.income_add, name='income_add'),
    path('finance/incomes/<int:pk>/', views.income_detail, name='income_detail'),
    path('finance/incomes/<int:pk>/edit/', views.income_edit, name='income_edit'),
    path('finance/incomes/<int:pk>/confirm/', views.income_confirm, name='income_confirm'),
    path('finance/incomes/<int:pk>/cancel/', views.income_cancel, name='income_cancel'),
    path('finance/incomes/<int:pk>/delete-attachment/', views.income_delete_attachment, name='income_delete_attachment'),
    
    # 支出管理
    path('finance/expenses/', views.expense_list, name='expense_list'),
    path('finance/expenses/add/', views.expense_add, name='expense_add'),
    path('finance/expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('finance/expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('finance/expenses/<int:pk>/submit/', views.expense_submit, name='expense_submit'),
    path('finance/expenses/<int:pk>/approve/', views.expense_approve, name='expense_approve'),
    path('finance/expenses/<int:pk>/reject/', views.expense_reject, name='expense_reject'),
    path('finance/expenses/<int:pk>/delete-attachment/', views.expense_delete_attachment, name='expense_delete_attachment'),
    
    # 项目归档管理
    path('projects/archived/', views.archived_projects, name='archived_projects'),
    path('projects/<int:pk>/archive/', views.project_archive, name='project_archive'),
    path('projects/<int:pk>/unarchive/', views.project_unarchive, name='project_unarchive'),
]


