{
    'name': 'Foundation Tiago',
    'version': '16.0.1.0.0',  # Formato correto1
    'summary': 'Manages foundations, machines, services, and measurements.',
    'sequence': 10,
    'description': """Long description""",
    'category': 'Construction',
    'website': 'https://www.yourcompany.com',
    'images': [],
    'depends': [
        'base',
        'sale',
        'mail',
        'product',
        'account',  # Para usar contas analíticas
        'hr',       # Se você estiver usando funcionalidades relacionadas a empregados
    ],
    'data': [
        'security/ir.model.access.csv',  # Load security and access rules first

        'views/freports.xml',  # Load other reports or final views
        'views/foundation_maquina_view.xml',  # Load views for the Maquina model
        'views/foundation_obra_view.xml',  # Load views for the Obra model
        #'views/foundation_obra_service_with_estacas_view.xml',
        # Load views for the Obra Service model
        'views/foundation_medicao_view.xml',  # Load views for the Medicao model
        'views/foundation_obra_service_simples_view.xml',  # Load views for the Obra Service model
        'views/foundation_estacas_view.xml',  # Load views for the Estacas model
        #'views/foundation_relatorios_view.xml',  # Load views for the Estacas model
        'views/foundation_relatorios_lista_view.xml',
        #'views/foundation_chamada_view.xml',

        'views/foundation_maquina_registro_estacas.xml',
        'views/foundation_team_view.xml',
        'views/BACKUP.xml',  # Load menu definitions
        #'views/foundation_chamada_maquina_registro.xml',  # Load menu definitions
        'views/foundation_chamada_maquina_registro.xml',
        'views/foundation_menus.xml',  # Load menu definitions
        'views/foundation_actions.xml',  # Load actions (this should come early, before other views)

        'views/sale_order_obra_extension.xml',

        #'views/sale_order_obra_extension_link_order.xml',
        #'views/sale_order_obra_extension_link_invoice.xml',
        #'views/sale_order_obra_extension.xml',
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',  # This is the line you need to add
}
