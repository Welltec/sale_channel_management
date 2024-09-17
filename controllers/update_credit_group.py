# controllers/controllers.py
from odoo import http
from odoo.http import request
import json

class CreditGroupController(http.Controller):
    @http.route('/credit_group/update', type='json', auth='public', methods=['POST'], csrf=False)
    def update_credit_groups(self, **kwargs):
        try:
            #datos del JSON recibido
            json_data = request.jsonrequest
            
            # recorrer los grupos de crédito del JSON
            for group_data in json_data.get('grupo_creditos', []):
                codigo = group_data.get('codigo')
                canal_codigo = group_data.get('canal')
                nombre = group_data.get('name')
                credito_global = group_data.get('credito_global')
                
                # existe el canal exista
                canal = request.env['sale.channel'].search([('code', '=', canal_codigo)], limit=1)
                if not canal:
                    return json.dumps({
                        "status": 400,
                        "message": f"No se encontró el canal {canal_codigo}"
                    })
                
                # buscar si el grupo de crédito ya existe por el código
                credit_group = request.env['credit.group'].search([('code', '=', codigo)], limit=1)
                
                if credit_group:
                    credit_group.write({
                        'name': nombre,
                        'channel_id': canal.id,
                        'credit_limit': credito_global
                    })
                else:
                    request.env['credit.group'].create({
                        'name': nombre,
                        'code': codigo,
                        'channel_id': canal.id,
                        'credit_limit': credito_global
                    })
            
            #esta correcto, devolver una respuesta con éxito
            return json.dumps({
                "status": 200,
                "message": "OK"
            })

        except Exception as e:
            return json.dumps({
                "status": 500,
                "message": f"Error interno del servidor: {str(e)}"
            })
