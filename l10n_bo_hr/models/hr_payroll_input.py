from odoo import models, fields, api, _, tools

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    others_id = fields.Many2one('hr.others', 'Otras Entradas')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done','Confirmado'),
        ('cancel', 'Cancelado'),
        ], string='Estado', readonly=True)
    advance_id = fields.Many2one('hr.advance', 'Pagos adelantados')
    loan_line_id = fields.Many2one('hr.loan.line', 'Prestamos')
    form110_id = fields.Many2one('hr.form110', 'Formulario 110')
    date = fields.Date('Fecha', compute='_compute_date', store=True)
    freeze = fields.Boolean('Valor Congelado')