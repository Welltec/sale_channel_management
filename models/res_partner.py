from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_group_ids = fields.Many2many(
        comodel_name='credit.group',
        relation='partner_credit_group_rel',
        column1='partner_id',
        column2='credit_group_id',
        string='Grupos de Crédito'
    )
