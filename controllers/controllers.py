from odoo import http


class HelpController(http.Controller):
    @http.route('/tiago_fundacao/help', auth='user', website=True)
    def help_page(self):
        return http.request.render('tiago_fundacao.help_page_template', {})
