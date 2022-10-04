from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class employee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('date_entry')
    def _compute_antiquity(self):
        for s in self:
            date = fields.Date.from_string(fields.Date.context_today(self))
            if s.date_finiquito:
                date_finiquito = fields.Date.from_string(s.date_finiquito)
                days_finiquito = (date - date_finiquito).days
                s.antiquity_days = days_finiquito / 365
            elif s.date_entry:
                date_entry = fields.Date.from_string(s.date_entry)
                days_entry = (date - date_entry).days
                s.antiquity_days = days_entry / 365
            if s.date_entry:
                date_entry = fields.Date.from_string(s.date_entry)
                s.antiquity = relativedelta(date, date_entry).years
                s.antiquity_days = 0
            else:
                s.antiquity = 0
                s.antiquity_days = 0

    def _compute_average_wage(self):
        payslip_obj = self.env['hr.payslip']
        for s in self:
            payslip_ids = payslip_obj.search([('employee_id', '=', s.employee_id.id), ('state', '=', 'done')],
                                             order="date desc", limit=2)
            total = 0
            if payslip_ids:
                for p in payslip_ids:
                    for lines in p.line_ids.filtered(lambda x: x.code == 'GROSSBO'):
                        total += lines.total
                total = total
            s.average_wage = total

    expedido = fields.Selection(string='Expedido en',
                                selection=[('LP', 'La Paz'),
                                           ('CB', 'Cochabamba'),
                                           ('SC', 'Santa Cruz'),
                                           ('CH', 'Chuquisaca'),
                                           ('PD', 'Pando'),
                                           ('BN', 'Beni'),
                                           ('TJ', 'Tarija'),
                                           ('OR', 'Oruro'),
                                           ('PT', 'Potosí'),
                                           ],
                                default='LP')
    all_name = fields.Char(string='Primer Nombre', required=True, default='')
    all_name_two = fields.Char(string='Segundo Nombre', required=False, default='')
    paternal_surname = fields.Char(
        string='Apellido Paterno', required=True, default='')
    maternal_surname = fields.Char(
        string='Apellido Materno', required=False, default='')
    maried_surname = fields.Char(
        string='Apellido de Casada', required=False, default='')
    blood_type = fields.Char(string='Tipo de Sangre',
                             required=True, default='')
    cod_laboral = fields.Char(string='Cod. Laboral', required=True, default='')
    nua = fields.Char(string='NUA', help="NUA: Número Único Asignado por parte de la AFP")
    partner_afp_id = fields.Many2one(string='Empresa AFP de empleado')
    date_entry = fields.Date('Fecha de Ingreso',
                             help="Esta fecha sera tomada para el calculo de Antiguedad en caso de estar en blanco se tomara la fecha del contrato.")
    date_finiquito = fields.Date('Fecha de última Indemnización')
    antiquity = fields.Integer('Años de Antigüedad', compute="_compute_antiquity", store=True)
    antiquity_days = fields.Float('Antigüedad Exacta', compute="_compute_antiquity", store=True)
    saldo_rciva = fields.Float(string="Saldo Rc-IVA", default=0)
    bono_antiquity_id = fields.Many2one('hr.bono.antiguedad', 'Bono de Antigüedad')
    average_wage = fields.Float('Sueldo Promedio', compute="_compute_average_wage")

    @api.onchange('all_name')
    def _onchange_allname(self):
        complete_name = ''
        if self.all_name:
            complete_name += self.all_name
        if self.all_name_two:
            complete_name += ' ' + self.all_name_two
        if self.paternal_surname:
            complete_name += ' ' + self.paternal_surname
        if self.maternal_surname:
            complete_name += ' ' + self.maternal_surname
        self.name = complete_name

    @api.onchange('all_name_two')
    def _onchange_allname_two(self):
        complete_name = ''
        if self.all_name:
            complete_name += self.all_name
        if self.all_name_two:
            complete_name += ' ' + self.all_name_two
        if self.paternal_surname:
            complete_name += ' ' + self.paternal_surname
        if self.maternal_surname:
            complete_name += ' ' + self.maternal_surname
        self.name = complete_name

    @api.onchange('paternal_surname')
    def _onchange_pat(self):
        complete_name = ''
        if self.all_name:
            complete_name += self.all_name
        if self.all_name_two:
            complete_name += ' ' + self.all_name_two
        if self.paternal_surname:
            complete_name += ' ' + self.paternal_surname
        if self.maternal_surname:
            complete_name += ' ' + self.maternal_surname
        self.name = complete_name

    @api.onchange('maternal_surname')
    def _onchange_mat(self):
        complete_name = ''
        if self.all_name:
            complete_name += self.all_name
        if self.all_name_two:
            complete_name += ' ' + self.all_name_two
        if self.paternal_surname:
            complete_name += ' ' + self.paternal_surname
        if self.maternal_surname:
            complete_name += ' ' + self.maternal_surname
        self.name = complete_name
