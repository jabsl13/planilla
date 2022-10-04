from odoo import fields, models, api, _


class HrBonoAntiguedad(models.Model):
    _name = 'hr.bono.antiguedad'

    name = fields.Char(string='Referencia')
    anio_min = fields.Float(string='Año Minimo')
    anio_max = fields.Float(string='Año Máximo')
    porcentaje = fields.Float(string='Porcentaje')


class HrBonoPlantilla(models.Model):
    _name = 'hr.bono.plantilla'

    name = fields.Char(string='Bono')
    amount = fields.Float(string='Monto')


class HrBonoContract(models.Model):
    _name = 'hr.bono.contract'

    contract_id = fields.Many2one('hr.contract', string='Contrato')
    bono_id = fields.Many2one('hr.bono.plantilla', string='Bono')
    amount = fields.Float(string='Monto Bs.')

    @api.onchange('bono_id')
    def _onchange_bono(self):
        if self.bono_id:
            self.amount = self.bono_id.amount
