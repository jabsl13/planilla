import datetime
from odoo import fields, models, _
from datetime import datetime, timedelta, date


class PayrollAfp(models.TransientModel):
    _name = "payroll.afp"
    _description = "Payroll to AFP"

    def _prev_month_m(self):
        today = date.today()
        first = today.replace(day=1)
        lastMonth = first - timedelta(days=1)
        return lastMonth.strftime("%m")

    def _default_year(self):
        date = datetime.now()
        return date.year

    month = fields.Selection(
        [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'),
         ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')],
        string='Mes', required=True, default=_prev_month_m)
    year = fields.Char(u'Año', size=4, required=True, default=_default_year)
    company_id = fields.Many2one('res.company', string='Compañía', readonly=False,
                                 default=lambda self: self.env.company, required=True)

    def print_xlsx(self):
        report_name = 'l10n_bo_hr.payroll_afp_xlsx.xlsx'
        return self.env['ir.actions.report'].search(
            [('report_name', '=', report_name),
             ('report_type', '=', 'xlsx')], limit=1).report_action(self)
