from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class CreditGroupReportWizard(models.TransientModel):
    _name = 'credit.group.report.wizard'
    _description = 'Wizard para Generar Reporte de Crédito Utilizado'

    group_id = fields.Many2one('credit.group', string='Grupo de Crédito', required=True)
    # llamo al reporte
    def generate_report(self):
        data = {
            'group_id': self.group_id.id,
        }
        return self.env.ref('sale_channel_management.credit_group_report_action').report_action(self, data=data)
