import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sueldo_min = fields.Float(string='Sueldo mínimo', related='company_id.sueldo_min', readonly=False)
