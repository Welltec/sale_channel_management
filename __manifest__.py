{
    'name': 'Sale Channel Management',
    'description': 'Gestión de Canales de Venta, Grupos de Credito y Reglas de Credito. Prueba para Calyx',
    'author': 'Willian Matiello',
    'depends': ['sale', 'sale_management', 'account', 'stock'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/sale_channel_views.xml',
        'views/sale_order_views.xml',
        'views/credit_group_views.xml',
        'views/res_partner_views.xml',
        'views/picking_views.xml',
        'views/account_move_views.xml',
        'data/sequence_data.xml',
        'views/menu_views.xml',
        'wizard/report_credit_group_wizard.xml',
        'report/credit_group_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_channel_management/static/src/css/styles.css',
        ],
    },
}
