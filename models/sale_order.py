from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    """
    Cria um registro na tabela foundation obra vinculado com a sale order
    Cria vários registros em foundation obra service, um para cada serviço
    """
    _inherit = 'sale.order'

    nome_obra = fields.Char("Nome da Obra", required=False)
    cei = fields.Char("CEI", required=False)
    cnpj_gfip = fields.Char("CNPJ GFIP", required=False)
    aos_cuidados = fields.Char("Aos Cuidados", required=False)

    def _create_foundation_obra_and_services(self):
        """
        Cria uma nova obra em foundation_obra com o nome na sale order
        """
        foundation_obra = self.env['foundation.obra']
        foundation_obra_service = self.env['foundation.obra.service']

        for order in self:
            # Verifica se já existe uma obra associada a esta ordem
            obra = foundation_obra.search([('sale_order_id', '=', order.id)], limit=1)
            if not obra:
                obra = foundation_obra.create({
                    'sale_order_id': order.id
                })

            # Cria um serviço para cada template de produto único
            template_lines = {}
            for line in order.order_line:
                # Verifica se a linha não está em branco
                if line.product_id:
                    template = line.product_id.product_tmpl_id
                    if template not in template_lines:
                        template_lines[template] = line

            for template, line in template_lines.items():
                if not foundation_obra_service.search([
                    ('variante_id', '=', line.product_id.id),
                    ('obra_id', '=', obra.id)
                ], limit=1):
                    foundation_obra_service.create({
                        'variante_id': line.product_id.id,
                        'obra_id': obra.id
                    })

    def write(self, vals):
        """
        Sobrescreve o método write para adicionar lógica personalizada ao atualizar registros.
        Cria novos registros em foundation.obra.service para produtos que podem não ter sido criados anteriormente.
        :param vals: Dicionário com os valores a serem atualizados.
        :return: Resultado da chamada ao método write original.
        """
        _logger.info(f"Atualizando sale.order com os valores: {vals}")

        # Chama o método write original para realizar a atualização no banco de dados
        result = super(SaleOrder, self).write(vals)

        foundation_obra = self.env['foundation.obra']
        foundation_obra_service = self.env['foundation.obra.service']

        for order in self:
            # Verifica se a ordem de venda já está confirmada
            if order.state == 'sale':
                # todo remover essa logica urgente
                # Verifica se já existe uma obra associada a esta ordem
                obra = foundation_obra.search([('sale_order_id', '=', order.id)], limit=1)

                # Cria um serviço para cada template de produto único
                template_lines = {}
                for line in order.order_line:
                    # Verifica se a linha não está em branco
                    if line.product_id:
                        template = line.product_id.product_tmpl_id
                        if template not in template_lines:
                            template_lines[template] = line

                for template, line in template_lines.items():
                    # Verifica se já existe um serviço para esta variante e obra
                    if not foundation_obra_service.search([
                        ('variante_id', '=', line.product_id.id),
                        ('obra_id', '=', obra.id)
                    ], limit=1):
                        # Se não existir, cria um novo serviço
                        foundation_obra_service.create({
                            'variante_id': line.product_id.id,
                            'obra_id': obra.id
                        })
                        _logger.info(f"Serviço criado para o produto {line.product_id.name} na obra {obra.id}")

        # Exemplo de pós-processamento: Log de sucesso
        _logger.info("Registro(s) atualizado(s) com sucesso e serviços criados/verificados.")

        return result

    def action_confirm(self):
        """
        Sobrescreve o método de confirmação para disparar a criação de obra e serviços
        """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order._create_foundation_obra_and_services()
        return res
