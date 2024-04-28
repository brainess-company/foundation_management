"""
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
import logging
from odoo import models, fields, api


_logger = logging.getLogger(__name__)  # Configuração do logger


class FoundationObra(models.Model):
    """
    OBRAS RELACIONADAS COM ORDEM DE VENDAS

    """
    _name = 'foundation.obra'
    _description = 'Informações sobre a obra'
    _rec_name = 'nome_obra'

    # CAMPOS PRÓPRIOS
    nome_obra = fields.Char(related='sale_order_id.nome_obra',
                            store=True, readonly=True, string="Nome da Obra")
    endereco = fields.Char("Endereço")

    # RELACIONA ESSA TABELA FOUNDATION OBRA COM  UMA SALE ORDER
    sale_order_id = fields.Many2one('sale.order',
                                    string="Ordem de Venda", required=True)
    partner_id = fields.Many2one('res.partner', string="Cliente",
                                 related='sale_order_id.partner_id', readonly=True,
                                 store=True)
    cliente_id = fields.Many2one('res.partner',
                                 string="Cliente 2", related='sale_order_id.partner_id',
                                 readonly=True, store=True)
    valor_total = fields.Monetary("Valor Total", related='sale_order_id.amount_total', readonly=True)
    invoice_address = fields.Char("Endereço de Faturamento",
                                  related='sale_order_id.partner_invoice_id.street',
                                  readonly=True)
    currency_id = fields.Many2one('res.currency',
                                  related='sale_order_id.currency_id',
                                  readonly=True, store=True)

    # CAMPOS CALCULADOS
    valor_faturado = fields.Monetary(compute="_compute_valor_faturado",
                                     string="Valor Faturado", readonly=True)
    valor_a_faturar = fields.Monetary(compute="_compute_valor_a_faturar",
                                      string="Valor a Faturar", eadonly=True)

    @api.depends('sale_order_id.invoice_ids', 'sale_order_id.invoice_ids.state')
    def _compute_valor_faturado(self):
        """
        CALCULA O VALOR DE FORMA DINÂMICA
        """
        for record in self:
            valor_faturado = sum(
                invoice.amount_untaxed for invoice in record.sale_order_id.invoice_ids
                if invoice.state == 'posted')
            record.valor_faturado = valor_faturado
            _logger.info(f"Computed 'valor_faturado' "
                         f"for FoundationObra {record.id}: {valor_faturado}")

    @api.depends('sale_order_id.order_line.qty_delivered',
                 'sale_order_id.order_line.qty_invoiced',
                 'sale_order_id.order_line.product_id.type')
    def _compute_valor_a_faturar(self):
        """
        CALCULA VALOR A FATURAR MAS ESTÁ COM ERRO
        """
        for record in self:
            valor_a_faturar = sum((line.qty_delivered - line.qty_invoiced) * line.price_unit
                                  for line in record.sale_order_id.order_line
                                  if line.product_id.type == 'product'
                                  and (line.qty_delivered - line.qty_invoiced) > 0)
            record.valor_a_faturar = valor_a_faturar
            _logger.info(
                f"Computed 'valor_a_faturar' for FoundationObra {record.id}: {valor_a_faturar}")
