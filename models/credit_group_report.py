from odoo import models, api, fields
from datetime import datetime

class CreditGroupReport(models.AbstractModel):
    _name = 'report.sale_channel_management.credit_group_report_template'
    _description = 'Reporte de Grupo de Crédito'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        lang = self.env.user.lang or self.env.company.lang

        group = self.env['credit.group'].browse(data['group_id'])
        company = self.env.company

        # formateo de las monedas con el idioma
        def format_currency(amount, currency):
            return company.currency_id.symbol + " " + "{:,.2f}".format(amount).replace(',', 'X').replace('.', ',').replace('X', '.')

        # formateo de fechas a dd/mm/yyyy, respetando el idioma
        def format_date(date):
            date_obj = fields.Date.from_string(date)
            return datetime.strftime(date_obj, self.env['res.lang'].search([('code', '=', lang)]).date_format or "%d/%m/%Y")

        # Agrupar por cliente
        customer_data = []
        for partner in group.credit_group_ids:
            combined_data = []
            total_credit = 0.0 

            # ordenes confirmadas del cliente
            confirmed_orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('channel_id', '=', group.channel_id.id),
                ('state', '=', 'sale')
            ])

            #Añadir ordenes de venta a la lista combinada
            for order in confirmed_orders:
                order_total = 0.0
                if order.invoice_ids:
                    unpaid_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.payment_state != 'paid')
                    if unpaid_invoices:
                        for invoice in unpaid_invoices:
                            invoice_amount = invoice.currency_id._convert(invoice.amount_residual, company.currency_id, company, invoice.invoice_date)
                            combined_data.append({
                                'type': 'factura',  # para facturas bandera
                                'number': invoice.name,
                                'date': format_date(invoice.invoice_date),
                                'amount': format_currency(invoice_amount, company.currency_id),
                            })
                            order_total += invoice_amount
                else:
                    # si no tiene facturas, sumar el total de la orden
                    order_total = order.currency_id._convert(order.amount_total, company.currency_id, company, order.date_order)

                combined_data.append({
                    'type': 'orden',  # marcar como orden, bandera
                    'number': order.name,
                    'date': format_date(order.date_order),
                    'amount': format_currency(order_total, company.currency_id),
                })
                total_credit += order_total  #crédito total del cliente suma

            #  cliente con sus órdenes y facturas combinadas y el total de crédito
            customer_data.append({
                'partner': partner,
                'combined_data': combined_data,  # Lista combinada de órdenes y facturas
                'total_credit': format_currency(total_credit, company.currency_id),  
                'document': partner.vat,  
                'phone': partner.phone or '',  
                'email': partner.email or '' 
            })

        # datos finales de credito global, utilizado y disponible
        credit_data = {
            'credit_limit': format_currency(group.credit_limit, company.currency_id),
            'credit_used': format_currency(group.credit_used, company.currency_id),
            'credit_available': format_currency(group.credit_available, company.currency_id)
        }

        return {
            'group': group,
            'customers': customer_data,
            'credit_data': credit_data,  # Datos de credito global, utilizado y disponible
            'lang': lang  # Pasamos el idioma dinamico a la plantilla
        }
