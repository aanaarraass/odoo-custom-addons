# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://devintellecs.com>).
#
##############################################################################
{
    "name": "HR Employee Advance Salary, Advance Employee Salary",
    "category": 'Generic Modules/Human Resources',
    "summary": """
                  employee advance salary employee, advance salary mail notification, Integrated with accounting for payment, employee advance salary Integrated with payroll, deducts salary in payslip, hr payroll, manager approval mail notification, hr advance salary
        """,
    "description": """
         odoo app will manage Employee Advance Salary whole process, approvals and intregrated with Accouting & Payroll.
        Hr  Advance Salary,Employee Advance Salary ,  Advance Salary Request 
        
HR Employee Advance Salary
Odoo HR Employee Advance Salary
Employee advance salary
Odoo employee advance salary
Employee advance salary request
Odoo Employee advance salary request
Employee Create Own Advance Salary
Odoo Employee Create Own Advance Salary
Advance Salary User can approve the request
Odoo Advance Salary User can approve the request
Employee advance salary notification
Odoo Employee advance salary notification
Advance Salary Request
Odoo Advance Salary Request
Advance salary
Odoo advance salary
Salary structure
Odoo salary structure
Set salary limit on job position
Odoo Set salary limit on job position
HR Officer/Manager Approval
Odoo HR Officer/Manager Approval
Employees/Advance Salary
Odoo Employees/Advance Salary
Employees/Advance Salary/Advance Salary Requests
Odoo Employees/Advance Salary/Advance Salary Requests

employees/Advance Salary/Department Approvals
Employees/Advance Salary/Director Approvals
Employees/Advance Salary/HR Approvals
Invoicing/Purchases/Advance Salary Requests
HR advance salary report
Odoo HR advance salary report
employee advance salary employee, advance salary mail notification, Integrated with accounting for payment, employee advance salary Integrated with payroll, deducts salary in payslip, hr payroll, manager approval mail notification, hr advance salary

    """,
    "sequence": 1.0,
    "author": "DevIntelle Consulting Service Pvt.Ltd",
    "website": "http://www.devintellecs.com",
    "version": '15.0.1.0',
    "depends": ['hr_payroll'],
    "data": [
        'security/advance_salary_security.xml',
        'security/ir.model.access.csv',
        'views/ir_sequence_data.xml',
        'views/dev_advance_salary.xml',
        'views/pay_slip_view.xml',
        'views/hr_employee_view.xml',
        'views/demo_data.xml',
        'report/dev_advanced_salary_template.xml',
        'report/dev_advanced_salary_menu.xml',
        
    ],
    "installable": True,
    "application": True,
    'images': ['images/main_screenshot.png'],
    "auto_install": False,
    'price':19.0,
    'currency':'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
