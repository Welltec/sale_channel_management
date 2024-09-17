from odoo import models, fields, api

class CreditGroup(models.Model):
    _name = 'credit.group'
    _description = 'Grupo de Crédito'

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)
    channel_id = fields.Many2one('sale.channel', string="Canal de Venta", required=True)
    currency_id = fields.Many2one('res.currency', string="Moneda", required=True, default=lambda self: self.env.company.currency_id)
    credit_limit = fields.Monetary(string="Crédito Global", required=True, currency_field='currency_id')
    credit_used = fields.Monetary(string="Crédito Utilizado", compute='_compute_credit_used', currency_field='currency_id')
    credit_available = fields.Monetary(string="Crédito Disponible", compute='_compute_credit_available', currency_field='currency_id')
    
    # relacion Many2many entre credit.group y res.partner
    credit_group_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='partner_credit_group_rel',  # nombre de la tabla relacional
        column1='credit_group_id',  # columna que hace referencia al grupo de credito
        column2='partner_id',  # columna que hace referencia al socio (partner)
        string='Clientes Asociados'
    )

    @api.depends('channel_id')
    def _compute_credit_used(self):
        """
        Calcula el crédito utilizado basado en las órdenes de venta del canal asociado.
        Se suman:
        1. Órdenes confirmadas (estado 'sale') sin facturas.
        2. Órdenes confirmadas con facturas impagas.
        Si una orden tiene facturas pagadas, no se suma.
        """
        for group in self:
            total_credit_used = 0.0

            #todas las ordenes confirmadas (estado 'sale') para el canal asociado
            confirmed_orders = self.env['sale.order'].search([('channel_id', '=', group.channel_id.id), ('state', '=', 'sale')])

            for order in confirmed_orders:
                if order.invoice_ids:
                    # Si tiene facturas asociadas
                    unpaid_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state != 'paid')
                    if unpaid_invoices:
                        # Si hay facturas impagas sumar el monto pendiente de las facturas
                        for invoice in unpaid_invoices:
                            total_credit_used += invoice.currency_id._convert(invoice.amount_residual, group.currency_id, self.env.company, invoice.invoice_date)
                else:
                    # Si no tiene facturas sumar el monto total de la orden
                    total_credit_used += order.currency_id._convert(order.amount_total, group.currency_id, self.env.company, order.date_order)

            # asignar el credito utilizado al grupo
            group.credit_used = total_credit_used

    @api.depends('credit_limit', 'credit_used')
    def _compute_credit_available(self):
        """
        Calcula el crédito disponible restando el crédito utilizado del límite de crédito.
        """
        for group in self:
            group.credit_available = group.credit_limit - group.credit_used
