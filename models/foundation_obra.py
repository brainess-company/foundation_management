from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)  # Configuração do logger


class FoundationObra(models.Model):
    _name = 'foundation.obra'
    _description = 'Informações sobre a obra'

    sale_order_id = fields.Many2one('sale.order', string="Ordem de Venda", required=True)
    nome_obra = fields.Char("Nome da Obra")
    endereco = fields.Char("Endereço")
    cliente_id = fields.Many2one('res.partner', string="Cliente", related='sale_order_id.partner_id', readonly=True,
                                 store=True)
    valor_total = fields.Monetary("Valor Total", related='sale_order_id.amount_total', readonly=True, store=True)

    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', readonly=True, store=True)
    valor_faturado = fields.Monetary(compute="_compute_valor_faturado", string="Valor Faturado", store=True,
                                     readonly=True)
    valor_a_faturar = fields.Monetary(compute="_compute_valor_a_faturar", string="Valor a Faturar", store=True,
                                      readonly=True)

    @api.depends('sale_order_id.invoice_ids', 'sale_order_id.invoice_ids.state')
    def _compute_valor_faturado(self):
        for record in self:
            valor_faturado = sum(
                invoice.amount_untaxed for invoice in record.sale_order_id.invoice_ids if invoice.state == 'posted')
            record.valor_faturado = valor_faturado
            _logger.info(f"Computed 'valor_faturado' for FoundationObra {record.id}: {valor_faturado}")

    @api.depends('sale_order_id.order_line.qty_delivered', 'sale_order_id.order_line.qty_invoiced',
                 'sale_order_id.order_line.product_id.type')
    def _compute_valor_a_faturar(self):
        for record in self:
            valor_a_faturar = sum((line.qty_delivered - line.qty_invoiced) * line.price_unit
                                  for line in record.sale_order_id.order_line
                                  if line.product_id.type == 'product' and (line.qty_delivered - line.qty_invoiced) > 0)
            record.valor_a_faturar = valor_a_faturar
            _logger.info(f"Computed 'valor_a_faturar' for FoundationObra {record.id}: {valor_a_faturar}")