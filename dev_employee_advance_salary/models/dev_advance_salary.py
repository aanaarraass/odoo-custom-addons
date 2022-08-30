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
import sys
from datetime import datetime,date
from time import mktime, strptime


class advance_salary(models.Model):
    _name = 'dev.advance.salary'
    _inherit = 'mail.thread'
    _order='name desc'
    
    name = fields.Char('Name', default='/', copy=False)
    employee_id = fields.Many2one('hr.employee','Employee',required="1")
    date = fields.Date('Request Date', required="1",default=date.today(), copy=False)
    amount = fields.Float('Request Amount', required="1",copy=False)
    confirm_date = fields.Date('Confirm Date',)
    comfirm_manager = fields.Many2one('res.users','Confirm Manager',track_visibility='onchange')
    dept_id = fields.Many2one('hr.department','Department')
    manager_id = fields.Many2one('hr.employee','Department Manager',required="1")
    partner_id = fields.Many2one('res.partner','Employee Partner', copy=False)
    payment_method = fields.Many2one('account.journal','Payment Method', copy=False)
    paid_amount = fields.Float('Paid Amount')
    reason = fields.Text('Reason', placeholder='Reason')
    
    user_id = fields.Many2one('res.users','User',default=lambda self: self.env.user,copy=False)
    state= fields.Selection([('draft','Draft'),('request','Request'),('approval','Approval'),('hr_confirm','HR Confirm'),('reject','Rejected'),('paid','Paid'),('cancel','Cancel')], string='State', default='draft',track_visibility='onchange')
    
    paid_id = fields.Many2one("account.payment", 'Payment',copy=False)
    is_assign = fields.Boolean('Is Assign to payslip', copy=False)
    payment_id = fields.Many2one('account.payment',string="Payment")
    
    
    @api.onchange('employee_id')
    def onchage_emp(self):
        if self.employee_id:
            self.dept_id = self.employee_id.department_id and self.employee_id.department_id.id or False
            self.manager_id = self.employee_id.parent_id and self.employee_id.parent_id.id or False
            
    
    
    @api.onchange('amount')
    def onchage_request_amount(self):
        if self.employee_id and self.amount:
            self.paid_amount = self.amount
            if self.employee_id.adv_salary_amount<=0:
                raise ValidationError(_('Please Define %s Advance Salary Limit Amount') %
                (self.employee_id.name))
                
            if self.employee_id.adv_salary_amount < self.amount:
                raise ValidationError(_('Advace Salary Request Amount Must be less then %s') %
                (self.employee_id.adv_salary_amount))
            
    def unlink(self):
        for obj in self:
            if obj.state != 'draft':
                raise ValidationError(_('Advance Salary Request Delete in Draft State !!!'))
        return super(advance_salary,self).unlink()
        
    
    @api.onchange('paid_amount')
    def onchage_paid_amount(self):
        if self.amount and self.paid_amount:
            if self.amount < self.paid_amount:
                raise ValidationError(_('Paid Amount must be less or Equal to Request Amount'))
                
    
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = '/'
        return super(advance_salary, self).copy(default=default)

    def write(self, vals):
        res= super(advance_salary, self).write(vals)
        if self.employee_id.adv_salary_amount<=0:
            raise ValidationError(_('Please Define %s Advance Salary Limit Amount') %
                (self.employee_id.name))
                
        if self.employee_id.adv_salary_amount < self.amount:
            raise ValidationError(_('Advace Salary Request Amount Must be less then %s') %
            (self.employee_id.adv_salary_amount))
            
        if self.amount < self.paid_amount:
            raise ValidationError(_('Paid Amount must be less or Equal to Request Amount'))
        
        return res
            
            
    
    @api.model
    def create(self, vals):
        employee_pool=self.env['hr.employee']
        employee_ids = employee_pool.browse(vals.get('employee_id'))
        if employee_ids:
            start_date = datetime.now().date().replace(month=1, day=1)    
            end_date = datetime.now().date().replace(month=12, day=31)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")
            start_date=datetime.strptime(start_date,"%Y-%m-%d")
            end_date=datetime.strptime(end_date,"%Y-%m-%d")
            yearling_req_ids = self.search([('state','not in',['reject','cancel']),('employee_id','=',vals.get('employee_id')),('date','<=',end_date),('date','>=',start_date)])
            if employee_ids.max_adv_salary <= 0:
                raise ValidationError(_('Plase Define the How Many Advance Salary Request is create per year.'))
                
            if len(yearling_req_ids) >= employee_ids.max_adv_salary:
                raise ValidationError(_('You can create maximum  %s Advance Salary request Per Year.') %
                (employee_ids.max_adv_salary))
                
        if employee_ids:
            if employee_ids.adv_salary_amount <= 0:
                raise ValidationError(_('Please Define %s Advance Salary Limit Amount') %
                (employee_ids.name))
            if employee_ids.adv_salary_amount < vals.get('amount'):
                raise ValidationError(_('Advace Salary Request Amount Must be less then %s') %
                (employee_ids.adv_salary_amount))
            
        request_ids = self.search([('state','in',['draft','request','approval','hr_confirm']),('employee_id','=',vals.get('employee_id'))],limit=1)
        if request_ids:
            raise ValidationError(_('You have All Ready Create %s Salary Request which is in %s.') %
                (request_ids.name, request_ids.state))
                
        
        paid_req_ids = self.search([('state','=','paid'),('is_assign','!=',True),('employee_id','=',vals.get('employee_id'))],limit=1)
        if paid_req_ids:
            raise ValidationError(_('Advance Salary allready process for this month.'))
            
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'dev.advance.salary') or '/'
        return super(advance_salary, self).create(vals)
    
    def _make_url(self,model='dev.advance.salary'):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url', default='http://localhost:8069')
        if base_url:
            base_url += '/web/login?db=%s&login=%s&key=%s#id=%s&model=%s' % (self._cr.dbname, '', '',self.id, model)
        return base_url
    
    def send_advance_salary_request(self):
        if self.amount <= 0:
            raise ValidationError('Advance Salary Amount Must be Greater then 0.')
        mail_mail = self.env['mail.mail']
        partner_pool = self.env['res.partner']
        
        subject  =  self.employee_id.name + '-' + 'Advance Salary Request'
        if self.manager_id and self.manager_id.work_email:
            url = self._make_url()  
            body = '''
                Dear ''' " <b>%s</b>," % (self.manager_id.name) + '''
                <p></p>
                <p> Employee ''' "<b>%s</b>" % self.employee_id.name + '''  require your Approval for Advance Salary.</p> 
                <p></p>
                <p><b>Reason:</b> '''"%s" % self.reason+'''</p>
                <p></p>
                <p>Please action it accordingly</p> 
                <p> </p>
                <p>You can access Advance Salary Request  from  below url </p>
                <p>''' "%s" % url +''' </p> 
                
                <p>Regards, </p> 
                <p>''' "<b>%s</b>" % self.user_id.name +''' </p> 
                ''' 
            mail_values = {
                'email_from': self.user_id.email,
                'email_to': self.manager_id.work_email,
                'subject': subject,
                'body_html': body,
                'state': 'outgoing',
            }
            mail_id = mail_mail.create(mail_values)
            mail_id.send(True)
        self.state = 'request'
        return True
    
    def reject_salary_request(self):
        mail_mail = self.env['mail.mail']
        subject  =  'Advance Salary Request is reject'
        partner= self.user_id.partner_id
        if partner:
            url = self._make_url()  
            if partner.email:
                body = '''
                    Dear ''' " <b>%s</b>," % (partner.name) + '''
                    <p></p>
                    <p> Your Advance Salary Request ''' "<b>%s</b>" % self.name + ''' is Reject.</p> 
                    <p></p>
                    <p>Please action it accordingly</p> 
                    <p> </p>
                    <p>You can access Advance Salary Request  from  below url </p>
                    <p>''' "%s" % url +''' </p> 
                    
                    <p>Regards, </p> 
                    <p>''' "<b>%s</b>" % self.env.user.name +''' </p> 
                    ''' 
                mail_values = {
                    'email_from': self.env.user.partner_id.email,
                    'email_to': partner.email,
                    'subject': subject,
                    'body_html': body,
                    'state': 'outgoing',
                }
                mail_id = mail_mail.create(mail_values)
                mail_id.send(True)
        self.state = 'reject'
        return True
    def set_to_draft(self):
        self.state = 'draft'
    
    def set_to_cancel(self):
        self.state = 'cancel'
    
    
    
    def approve_request(self):
        mail_mail = self.env['mail.mail']    
        group_id = self.env['ir.model.data']._xmlid_lookup('hr_payroll.group_hr_payroll_manager')[2]
        group_ids = self.env['res.groups'].browse(group_id)
        partner_pool = self.env['res.partner']
        partner_ids=[]
        for user in group_ids.users:
            partner_ids.append(user.partner_id.id)
        subject  =  self.employee_id.name + '-' + 'Advance Salary Confirmation'
        if partner_ids:
            url = self._make_url()  
            for partner in partner_pool.browse(partner_ids):
                if partner.email:
                    body = '''
                        Dear ''' " <b>%s</b>," % (partner.name) + '''
                        <p></p>
                        <p> Employee ''' "<b>%s</b>" % self.employee_id.name + '''  require your Confirmation for Advance Salary.</p> 
                        <p></p>
                        <p><b>Reason:</b> '''"%s" % self.reason+'''</p>
                        <p></p>
                        <p>Please action it accordingly</p> 
                        <p> </p>
                        <p>You can access Advance Salary Request  from  below url </p>
                        <p>''' "%s" % url +''' </p> 
                        
                        <p>Regards, </p> 
                        <p>''' "<b>%s</b>" % self.env.user.name +''' </p> 
                        ''' 
                    mail_values = {
                        'email_from': self.env.user.email,
                        'email_to': partner.email,
                        'subject': subject,
                        'body_html': body,
                        'state': 'outgoing',
                    }
                    mail_id = mail_mail.create(mail_values)
                    mail_id.send(True)
        self.state = 'approval'
        return True
    
    def confirm_request(self):
        import datetime
        mail_mail = self.env['mail.mail']
        partner_id = False
        if self.employee_id:
            if self.employee_id.user_id and self.employee_id.user_id.partner_id:
                partner_id = self.employee_id.user_id.partner_id or False
        subject  =  self.employee_id.name + '-' + 'Advance Salary Confirm'
        if partner_id:
            url = self._make_url()  
            if partner_id.email:
                body = '''
                    Dear ''' " <b>%s</b>," % (partner_id.name) + '''
                    <p></p>
                    <p> Your Advance Salary Request ''' "<b>%s</b>" % self.name + ''' is confirmed.</p> 
                    <p></p>
                    <p>Please action it accordingly</p> 
                    <p> </p>
                    <p>You can access Advance Salary Request  from  below url </p>
                    <p>''' "%s" % url +''' </p> 
                    
                    <p>Regards, </p> 
                    <p>''' "<b>%s</b>" % self.env.user.name +''' </p> 
                    ''' 
                mail_values = {
                    'email_from': self.env.user.partner_id.email,
                    'email_to': partner_id.email,
                    'subject': subject,
                    'body_html': body,
                    'state': 'outgoing',
                }
                mail_id = mail_mail.create(mail_values)
                mail_id.send(True)
        self.state = 'hr_confirm'
        self.confirm_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.comfirm_manager = self.env.user.id
        return True
        
    def salary_paid(self):
        if self.paid_amount <= 0:
            raise ValidationError('Advance Salary Paid Amount Must be Greater then 0.')
        paid_obj = self.env['account.payment']
        pay_fileds = paid_obj.fields_get()
        default_value = paid_obj.default_get(pay_fileds)
        pay_up = default_value.copy()
        pay_up.update({'partner_id': self.partner_id.id,
                           'payment_type': 'outbound',
                           'partner_type': 'supplier',
                           'journal_id': self.payment_method.id,
                           'amount': self.paid_amount,
                           'ref':self.name or '',
                           'date': self.confirm_date,
                           'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                           })
        pay_id = paid_obj.create(pay_up)
        self.paid_id = pay_id.id
        self.state = 'paid'   
        view_ref = self.env['ir.model.data']._xmlid_lookup('account.view_account_payment_form')[2]
        view_id = view_ref if view_ref else False
        
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Account Payment'),
            'res_model': 'account.payment',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': self.paid_id.id,
            'target': 'current'
            }

        return res
        
class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    
    advance_salary_id = fields.Many2one("dev.advance.salary",string="Salary Request")
    
    def action_payslip_done(self):
        res=super(hr_payslip,self).action_payslip_done()
        if self.advance_salary_id:
            self.advance_salary_id.is_assign = True
            
    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            salary_request_ids= self.env['dev.advance.salary'].search([('employee_id','=',self.employee_id.id),('state','=','paid'),('is_assign','=',False)],limit=1)
            self.advance_salary_id = salary_request_ids.id
            
        
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
    
        
