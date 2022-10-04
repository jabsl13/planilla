from odoo import fields, models, api, exceptions, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar


class HrRciva(models.Model):
    _name = 'hr.rciva'

    def _prev_month_m(self):
        today = date.today()
        first = today.replace(day=1)
        lastMonth = first - timedelta(days=1)
        return lastMonth.strftime("%m")

    def _default_year(self):
        date = datetime.now()
        return date.year

    date_from = fields.Date(string='Desde Fecha')
    date_to = fields.Date(string='Hasta Fecha')
    month = fields.Selection(
        [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'),
         ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'),
         ('12', 'Diciembre')],
        string='Mes', required=True, default=_prev_month_m)
    year = fields.Char(u'Año', size=4, required=True, default=_default_year)
    employee_id = fields.Many2one('hr.employee', string='Empleado', tracking=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', readonly=False, default=lambda self: self.env.company, required=True)
    amount_total = fields.Float(string='Monto Total', help='Según Registro Form 110')
    amount_iva = fields.Float(string='Importe IVA')
    amount_saldo = fields.Float(string='Saldo Anterior', help='Una vez Procesado la planilla se calcula')
    ufv_inicial_val = fields.Char(string=u'UFV Inicial')
    ufv_final_val = fields.Char(string=u'UFV Final')
    payslip_id = fields.Many2one('hr.payslip', string='Planilla de Sueldos', index=True)

    @api.onchange('month', 'year')
    def _onchange_year_month(self):
        if self.month and self.year:
            val_days = calendar.monthrange(int(self.year), int(self.month))
            date_init_ufv = datetime(int(self.year), int(self.month), 1) - relativedelta(days=1)
            date_end_ufv = datetime(int(self.year), int(self.month), val_days[1])
            self.date_from = date_init_ufv
            self.date_to = date_end_ufv
            ufv = self.env['res.currency'].search(
                [('name', '=', 'UFV'), ('active', '=', True)])
            ufv_id = ufv[0].id
            date_str_init_ufv = date_init_ufv.strftime('%Y-%m-%d')
            date_str_end_ufv = date_end_ufv.strftime('%Y-%m-%d')
            ufv_ini = 0.0
            ufv_fin = 0.0
            self._cr.execute("""SELECT rate FROM res_currency_rate WHERE currency_id = %s and to_char(name,'YYYY-MM-dd') = %s
                                       """, (ufv_id, date_str_init_ufv,))
            res = self._cr.fetchall()
            for line in res:
                ufv_ini = line[0]

            self._cr.execute("""SELECT rate FROM res_currency_rate WHERE currency_id = %s and to_char(name,'YYYY-MM-dd') = %s
                                       """, (ufv_id, date_str_end_ufv,))
            res = self._cr.fetchall()
            for line in res:
                ufv_fin = line[0]

            if not ufv_ini or ufv_fin == 0:
                raise exceptions.ValidationError(
                    _('No se ha configurado el tipo de cambio de la Moneda UFV para la periodo seleccionado'))

            self.ufv_inicial_val = str(ufv_ini)
            self.ufv_final_val = str(ufv_fin)

    @api.onchange('amount_total')
    def _onchange_rciva(self):
        if self.amount_total:
            self.amount_iva = self.amount_total * 0.13

    @api.constrains('date_from', 'date_to')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for rciva in self:
            if rciva.date_from and rciva.date_to:
                if rciva.date_to < rciva.date_from:
                    raise exceptions.ValidationError(_('Fecha Desde tiene que ser mayor a fecha Hasta'))
