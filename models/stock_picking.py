from odoo import models, fields, api
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    channel_id = fields.Many2one('sale.channel', compute='_compute_channel_sale_order', string="Canal de Venta", store=True, readonly=True)

    @api.depends('sale_id')
    def _compute_channel_sale_order(self):
        for record in self:
            if record.sale_id:
                record.channel_id = record.sale_id.channel_id
            else:
                record.channel_id = False
