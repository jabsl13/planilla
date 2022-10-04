# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Company(models.Model):
    _inherit = "res.company"

    cod_empleador = fields.Char(string='Código Empleador')
    caja_salud = fields.Char(string='Número patronal caja de salud')
    sueldo_min = fields.Float(string='Sueldo mínimo')
    recargo_noc = fields.Selection([
        ('25', '25%'),
        ('30', '30%'),
        ('40', '40%'),
        ('50', '50%'),
    ], defautl='25', string='Porcentaje recargo nocturno')
