from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    channel_id = fields.Many2one('sale.channel', string="Canal de Venta", compute='_compute_channel_id', store=True, readonly=True)

    @api.depends('invoice_line_ids')
    def _compute_channel_id(self):
        for move in self:
            sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
            if sale_orders:
                move.channel_id = sale_orders[0].channel_id
            else:
                move.channel_id = False
                
                
    @api.model
    def create(self, vals):
        
        move = super(AccountMove, self).create(vals)

        # recorrer las líneas de la factura y verificar el canal de venta
        sale_orders = move.invoice_line_ids.mapped('sale_line_ids.order_id')
        channels = sale_orders.mapped('channel_id')

        # si hay más de un canal de venta
        if len(set(channels)) > 1:
            raise UserError("Las órdenes a facturar deben ser del mismo canal de venta.")

        return move
