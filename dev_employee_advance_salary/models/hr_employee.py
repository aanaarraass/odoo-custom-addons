# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################
#
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import datetime


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    adv_salary_amount = fields.Float('Advance Salary Limit',copy=False)
    max_adv_salary = fields.Integer('Advance Salary Request',help="Per year how many time employee make Advance Salary Request")
    
    def count_advance_salary_request(self):
        for emp in self:
            adv_salary_ids = self.env['dev.advance.salary'].search([('employee_id','=',emp.id)])
            if adv_salary_ids:
                emp.request_count = len(adv_salary_ids)
            else:
                emp.request_count = 0
                
    request_count = fields.Integer(compute='count_advance_salary_request',string='Salary Request')
    
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
