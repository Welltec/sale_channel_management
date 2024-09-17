from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    channel_id = fields.Many2one('sale.channel', string="Canal de Venta", required=True)
    credit_status = fields.Selection([
    ('no_limit', 'Sin límite de crédito'),
    ('available', 'Crédito Disponible'),
    ('blocked', 'Crédito Bloqueado')], string="Estado del Crédito", compute='_compute_credit_status', store=False)
    
    @api.onchange('channel_id')
    def _onchange_channel_id(self):
        
        if self.channel_id:
            #actualiza el almacén de la orden de venta con el almacén del canal seleccionado
            self.warehouse_id = self.channel_id.warehouse_id.id
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        # Llamar al método nativo para obtener los valores originales
        super(SaleOrder, self).onchange_partner_id()

        channel_id = False
        domain = []

        # Si el cliente tiene grupos de credito
        if self.partner_id and self.partner_id.credit_group_ids:
            #obtener los canales asociados a los grupos de credito
            channels = self.partner_id.credit_group_ids.mapped('channel_id')

            # Si solo hay un canal lo asignamos automaticamente
            if len(channels) == 1:
                channel_id = channels[0].id
                self.channel_id = channel_id
                domain = [('id', '=', channel_id)]
            
            else:
                # si hay más de un canal mostrar solo los asociados
                domain = [('id', 'in', channels.ids)]
                # Limpiar el campo de canal para que el usuario seleccione uno
                self.channel_id = False #a eleccion
        else:
            # Si no tiene canales, mostramos vacio
            domain = [('id', '=', False)]
            self.channel_id = False

        # Retornar el dominio para 'channel_id'
        return {
            'domain': {
                'channel_id': domain
            }
        }

    
    @api.model
    def _prepare_invoice(self):
        
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        
        #verificar si la orden tiene un canal asociado y si el canal tiene un diario de facturación
        if self.channel_id and self.channel_id.journal_id:
            invoice_vals['journal_id'] = self.channel_id.journal_id.id
        return invoice_vals
            
    def action_confirm(self):
        if self.credit_status == 'blocked':
            raise UserError("El crédito está bloqueado. No se puede confirmar la venta.")
        return super(SaleOrder, self).action_confirm()

    @api.depends('amount_total', 'partner_id', 'channel_id')
    def _compute_credit_status(self):
        for order in self:
            if order.partner_id and order.partner_id.credit_group_ids:
                # Obtener el grupo de credito asociado al canal de la venta
                group = order.partner_id.credit_group_ids.filtered(lambda g: g.channel_id == order.channel_id)
                if group:
                    # Compara el importe total de la venta con el credito disponible
                    if order.amount_total > group.credit_available:
                        order.credit_status = 'blocked'
                    else:
                        order.credit_status = 'available'
                else:
                    order.credit_status = 'no_limit'
            else:
                order.credit_status = 'no_limit'
                
                
                
