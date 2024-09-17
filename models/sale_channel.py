from odoo import models, fields, api

class SaleChannel(models.Model):
    _name = 'sale.channel'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _description = 'Canal de Venta'
    
    name = fields.Char(string="Nombre", tracking=True, required=True)
    code = fields.Char(string="Código", readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('sale.channel.code'))
    warehouse_id = fields.Many2one('stock.warehouse', string="Depósito", required=True)
    journal_id = fields.Many2one(
        'account.journal', 
        string="Diario de Facturación", 
        required=True, 
        domain=[('type', '=', 'sale')])

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('sale.channel.code')
        return super(SaleChannel, self).create(vals)
