from odoo import models, fields, api


class custom_contract(models.Model):
    _inherit = 'hr.contract'

    salary_advance = fields.Monetary(string='Adelanto de sueldo')
    # transport_assignment = fields.Monetary(string='Asignación Transporte')
    # allowance_periods = fields.Monetary(string='Asignación Viaticos')
    # premium_bonus = fields.Monetary(string='Prima')
    bonus = fields.Monetary(string='Aguinaldo')
    health_manager_id = fields.Many2one(comodel_name='res.partner', string='Caja Salud',
                                        ondelete='cascade',
                                        required=False,
                                        default=False,
                                        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    avc_number = fields.Char(string='Matricula caja de salud')
    insured_code = fields.Char(string='Codigo Asegurado')
    nua_cua = fields.Char(string='NUA/CUA')
    contributes_afp = fields.Boolean(
        string='Aporta AFP', required=False, default=False)
    disabled_person = fields.Boolean(
        string='Persona con Discapacidad', required=False, default=False)
    disabled_person_tutor = fields.Boolean(
        string='Tutor Persona con Discapacidad', required=False, default=False)
    retiree = fields.Boolean(
        string='Es Jubilado', required=False, default=False)

    afp_manager_id = fields.Many2one(comodel_name='res.partner', string='Gestora AFP',
                                     ondelete='cascade',
                                     required=False,
                                     default=False,
                                     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    contract_modality = fields.Selection(string='Modalidad Contrato', selection=[('tiempoindef', 'Tiempo indefinido'),
                                                                                 ('plazofijo', 'A plazo fijo'),
                                                                                 ('eventual', 'Condicional o Eventual'),
                                                                                 ('temporada', 'Por Temporada'),
                                                                                 ('servicio',
                                                                                  'Por realizacion de Servicio')],
                                         copy=False, default='tiempoindef')

    recar_nocturno = fields.Selection(string='Recargo Nocturno', selection=[('25', 'Oficina'),
                                                                            ('30', 'Obreros'),
                                                                            ('40', 'Mujeres o Menores de 18 años'),
                                                                            ('50', 'Alto Riesgo'), ],
                                      copy=False, default='25')
    contract_type_expiration = fields.Date(
        string='Vencimiento tipo de contratacion')
    calculate_overtime = fields.Boolean(
        string='Calcula Horas Extras', default=False)
    bono_front = fields.Boolean(
        string='Bono Frontera', default=False)
    dominical = fields.Boolean(
        string='Bono Dominical',
        help='Active esta opción se requiere calcular bono domincal para el trabajador(Aplicable solo a trabjadores '
             'Obreros)',
        default=False)
    cbu = fields.Integer(string='CBU')
    settlement_start_date = fields.Date('Fecha Inicio Finiquito')
    dismissal_date = fields.Date('Fecha retiro')
    dismissal_reason = fields.Text('Motivo Retiro')
    bank_company = fields.Many2one(comodel_name='res.bank', string='Banco')
    cta_bank = fields.Many2one(comodel_name='res.partner.bank', string='Cuenta Banco',
                               domain="[('bank_id','=',bank_company)]")
    divisa_id = fields.Many2one('res.currency', string='Moneda Cta.', copy=False)
    bono_ids = fields.One2many(
        'hr.bono.contract', 'contract_id', string='Contratos')
