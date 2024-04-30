from odoo import http
from odoo.http import request

class InstructionsController(http.Controller):
    @http.route('/instructions', auth='user', website=True)
    def instructions(self):
        # Certifique-se que o template esteja correto
        return request.render('foundation_management.template_instructions', {})
