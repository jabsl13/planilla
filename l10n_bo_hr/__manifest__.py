# -*- coding: utf-8 -*-
{
    'name': "Bolivia HHRR",
    'summary': """
        Bolivian HR Localization
        """,
    'description': """
        Bolivian HR Localizacion Boliviana
    """,
    'author': "sapex.miguel@gmail.com",
    'category': 'Human Resources/Payroll',
    'version': '15.0.0.1',
    'depends': ['base',
                'hr',
                'hr_payroll',
                'hr_contract',
                'hr_work_entry_contract_enterprise',
                'hr_holidays',
                'hr_attendance',
                'account',
                'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'data/data_payroll_bo.xml',
        'data/data_bono_antiguedad.xml',
        'views/hr_bono_view.xml',
        'views/res_company_view_inherit.xml',
        'views/res_config_settings_views.xml',
        'views/hr_employee_views_inherit.xml',
        'views/hr_contract_views_inherit.xml',
        'views/hr_payslip_view_inherit.xml',
        'views/template_report_xlsx.xml',
        'views/hr_attendance_overtime_view.xml',
        'views/hr_rciva_view.xml',
        'views/hr_finiquito_view.xml',
        'views/hr_adelantos_view.xml',
        'views/hr_prestamos_view.xml',
        'wizard/payroll_ministry.xml',
        'wizard/payroll_afp.xml',
        'wizard/payroll_rciva.xml',
        'reports/graphic_representation.xml',
        'reports/graphic_representation_templates.xml',
    ],
}
