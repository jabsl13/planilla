from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class employee(models.Model):
    _inherit = 'hr.attendance.overtime'

    @api.depends('date')
    def _compute_day_week(self):
        for s in self:
            s.dia_semana = s.date.weekday()

    dia_semana = fields.Integer('Día de la semana', compute="_compute_day_week", store=True)
    horas_nocturno = fields.Float('Horas nocturna extra')
