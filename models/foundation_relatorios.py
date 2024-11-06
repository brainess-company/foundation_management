"""Lançamento em lote de estacas"""
from odoo import models, fields, api
from odoo.exceptions import UserError


class FoundationRelatorios(models.Model):
    """FALTA CRIAR AS OUTRAS ACTIONS PARA OS STATUS E INCLUIR BOTOUS NO FORMULARIO"""
    _name = 'foundation.relatorios'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Relatórios de Fundação'
    _rec_name = 'display_relatorio_name'

    # CAMPOS PROPRIOS
    data = fields.Date("Data do Relatório",
                       default=fields.Date.context_today, required=True, store=True)
    estacas_ids = fields.One2many('foundation.estacas', 'relatorio_id',
                                  string="Estacas Incluídas")
    assinatura = fields.Binary("Assinatura do Responsável",
                               help="Assinatura digital do responsável pelo relatório")
    state = fields.Selection([
        ('rascunho', 'Rascunho'),
        ('conferencia', 'Aguardando Conferencia'),
        ('em_analise', 'Em Análise'),
        ('cancelado', 'Cancelado'),
        ('conferido', 'Conferido')
    ], default='rascunho', string="Status", required=True)
    # todo verificar as implicações disso

    # Campos adicionais relacionados ao serviço
    nome_servico = fields.Char(related='foundation_maquina_registro_id.nome_servico',
                               string="Nome do Serviço",
                               readonly=True, store=True)
    maquina_id = fields.Many2one('foundation.maquina',
                                 related='foundation_maquina_registro_id.maquina_id',
                                 string="Máquina Associada",
                                 readonly=True, store=True)
    nome_obra = fields.Char(related='foundation_maquina_registro_id.nome_obra',
                            string="Nome da Obra", readonly=True, store=True)
    endereco_obra = fields.Char(related='foundation_maquina_registro_id.endereco',
                                string="Endereço da Obra", readonly=True, store=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order",
                                    related='foundation_maquina_registro_id.sale_order_id',
                                    readonly=True, store=True)
    service_template_id = fields.Many2one('product.template',
                                          string="Template do Serviço",
                                          related='service_id.service_template_id',
                                          readonly=True, store=True, required=True)
    service_id = fields.Many2one('foundation.obra.service',
                                 related='foundation_maquina_registro_id.service_id',
                                 string="Serivice id", readonly=True, store=True)
    variante_id = fields.Many2one('product.product', string="Variante")
    foundation_maquina_registro_id = fields.Many2one(
        'foundation.maquina.registro', string='Registro de Máquina',
        required=True, help='Referência ao registro de máquina associado.')
    operador_id = fields.Many2one(related='foundation_maquina_registro_id.operador_id',
                                  string="Operador", readonly=True, store=True)
    # Campo related para vincular diretamente ao user_id do operador
    operador_user_id = fields.Many2one('res.users', string="Usuário do Operador",
                                       related='operador_id.user_id', readonly=True, store=True)

    relatorio_number = fields.Char(string="Nome do Relatório")
    display_relatorio_name = fields.Char(compute="_compute_display_relatorio_name",
                                         string="Nome de Exibição do Relatório", store=True)

    # Adicionar o campo relacionado requer_chamada
    requer_chamada_maquina = fields.Boolean(string="Requer Chamada?",
                                            related='maquina_id.requer_chamada',
                                            readonly=True, store=True)

    active = fields.Boolean(string="Ativo", default=True)

    has_assinatura = fields.Boolean(string="Tem Assinatura", compute="_compute_has_assinatura",
                                    store=True)
    total_estacas_price = fields.Float(
        string="Valor Produzido",
        compute="_compute_total_estacas_price",
        store=True
    )

    chamada_existente = fields.Boolean(string="Chamada Existente",
                                       compute="_compute_chamada_existente")
    display_chamada_existente = fields.Char(string="Chamada feita?",
                                         compute='_compute_display_chamada_existente',
                                         store=False)
    # Adicionando o campo activity_ids
    activity_ids = fields.One2many('mail.activity', 'res_id', string="Atividades",
                                   domain=[('res_model', '=', 'foundation.relatorios')])

    @api.depends('chamada_existente')
    def _compute_display_chamada_existente(self):
        for record in self:
            if record.chamada_existente:  # Verifica se a máquina requer chamada
                record.display_chamada_existente = "Sim"
            else:
                record.display_chamada_existente = "Não"

    @api.depends('data', 'maquina_id')
    def _compute_chamada_existente(self):
        """Computa se já existe uma chamada para a mesma data e máquina"""
        for record in self:
            chamada = self.env['foundation.chamada'].search([
                ('data', '=', record.data),
                ('maquina_id', '=', record.maquina_id.id)
            ], limit=1)
            record.chamada_existente = bool(chamada)


    @api.depends('estacas_ids.total_price')
    def _compute_total_estacas_price(self):
        """
        Calcula a soma dos total_price de todas as estacas associadas ao relatório.
        """
        for record in self:
            total = sum(estaca.total_price for estaca in record.estacas_ids)
            record.total_estacas_price = total

    def toggle_active(self):
        for record in self:
            record.active = not record.active

    @api.depends('assinatura')
    def _compute_has_assinatura(self):
        for record in self:
            record.has_assinatura = bool(record.assinatura)

    @api.depends('relatorio_number', 'service_id', 'nome_obra')
    def _compute_display_relatorio_name(self):
        """computa o nome do relatorio"""
        for record in self:
            if record.relatorio_number and record.service_id and record.nome_obra:
                record.display_relatorio_name = f"REL{record.relatorio_number} - \
                    {record.service_id.service_name} - {record.nome_obra}"

    @api.model
    def create(self, vals):
        #if not vals.get('assinatura'):
         #   raise UserError("A assinatura é obrigatória para a criação de um relatório.")
            #  Obter o service_id associado ao registro de máquina
        if vals.get('foundation_maquina_registro_id'):
            maquina_registro = self.env['foundation.maquina.registro'].browse(
                vals.get('foundation_maquina_registro_id'))
            service_id = maquina_registro.service_id.id if maquina_registro.service_id else None

            if service_id:
                # Verificar o último número de relatório para o service_id específico
                last_report = self.search([
                    ('foundation_maquina_registro_id.service_id', '=', service_id)
                ], order='id desc', limit=1)

                next_number = 1
                if last_report and last_report.relatorio_number.isdigit():
                    next_number = int(last_report.relatorio_number) + 1
                vals['relatorio_number'] = str(next_number)

        new_record = super(FoundationRelatorios, self).create(vals)

        # Obter o registro de máquina associado para verificar se chamada_automatica está ativado
        maquina_registro = new_record.foundation_maquina_registro_id

        # Verificação de 'chamada_automatica'
        if maquina_registro.maquina_id and maquina_registro.maquina_id.chamada_automatica:
            # Verificar se já existe uma chamada para a máquina na data de hoje
            hoje = fields.Date.today()
            chamada_existente = self.env['foundation.chamada'].search([
                ('maquina_id', '=', maquina_registro.maquina_id.id),
                ('data', '=', hoje)
            ], limit=1)

            if not chamada_existente:
                # Se não existe chamada para a máquina hoje, criar uma nova chamada
                chamada_vals = {
                    'foundation_maquina_registro_id': maquina_registro.id,
                    'data': hoje,
                    'foundation_obra_service_id': maquina_registro.service_id.id,
                    'maquina_id': maquina_registro.maquina_id.id,
                    'obra_id': maquina_registro.service_id.obra_id.id,
                    'nome_obra': maquina_registro.nome_obra,
                    'endereco': maquina_registro.endereco,
                }
                nova_chamada = self.env['foundation.chamada'].create(chamada_vals)

                # Adicionar o operador da máquina à chamada, se disponível
                if maquina_registro.maquina_id.operador_id:
                    self.env['foundation.lista.presenca'].create({
                        'chamada_id': nova_chamada.id,
                        'funcionario_id': maquina_registro.maquina_id.operador_id.id,
                        'data': hoje,
                    })

        return new_record

    def action_confirm(self):
        """Confirma o relatório se houver uma assinatura"""
        for record in self:
            if not record.has_assinatura:
                raise UserError("Um relatório sem assinatura não pode ser conferido.")
            record.write({'state': 'conferido'})

    def action_cancel(self):
        """Cancela o relatório e cancela as estacas associadas"""
        for record in self:
            for estaca in record.estacas_ids:
                if estaca.sale_order_line_id:
                    estaca.sale_order_line_id.qty_delivered -= estaca.profundidade
                estaca.write({'active': False})
            record.write({'state': 'cancelado'})

    def action_draft(self):
        """action draft relatorio"""
        self.write({'state': 'rascunho'})

    @api.constrains('estacas_ids')
    def _check_estacas(self):
        """verifica profundidade das estacas"""
        if any(not estaca.profundidade for estaca in self.estacas_ids):
            raise UserError("Todas as estacas devem ter a profundidade definida.")

    def action_save(self):
        """action save relatorio"""
        self.ensure_one()
        self.state = 'conferencia'
        # Supondo que haja um campo de estado para controlar a confirmação do relatório
        return {
            'type': 'ir.actions.act_window',  # ir.actions.act_window PARA ABRIR O RELATORIO ou ir.actions.act_window_close PARA FECHAR O RELATORIO
            'name': 'Relatório Confirmado',
            'view_mode': 'form',
            'res_model': 'foundation.relatorios',
            'res_id': self.id,
            'target': 'current'
        }

    def action_duplicate(self):
        """Duplica o relatório atual junto com as estacas associadas, exceto o campo assinatura e os IDs."""
        self.ensure_one()  # Garante que apenas um registro seja processado

        # Cria um dicionário com os campos do relatório, excluindo o 'id' e 'assinatura'
        vals = {
            'data': self.data,
            'foundation_maquina_registro_id': self.foundation_maquina_registro_id.id,
            'state': self.state,  # Substitua 'campo1' pelo nome real do campo
            'nome_servico': self.nome_servico,  # Adicione todos os outros campos relevantes
            'maquina_id': self.maquina_id.id,  # Adicione todos os outros campos relevantes
            'nome_obra': self.nome_obra,  # Adicione todos os outros campos relevantes
            'endereco_obra': self.endereco_obra,  # Adicione todos os outros campos relevantes'campo2': self.campo2,  # Adicione todos os outros campos relevantes
            'sale_order_id': self.sale_order_id.id,  # Adicione todos os outros campos relevantes
            'service_template_id': self.service_template_id.id,  # Adicione todos os outros campos relevantes
            'service_id': self.service_id.id,  # Adicione todos os outros campos relevantes
            'variante_id': self.variante_id.id,  # Adicione todos os outros campos relevantes
            'operador_id': self.operador_id.id,  # Adicione todos os outros campos relevantes
            'operador_user_id': self.operador_user_id.id,  # Adicione todos os outros campos relevantes
            'requer_chamada_maquina': self.requer_chamada_maquina
            # Adicione mais campos conforme necessário...
        }

        # Cria o novo relatório sem os campos de ID e assinatura
        new_report = self.create(vals)

        # Duplicando as estacas associadas ao relatório
        for estaca in self.estacas_ids:
            # Define o dicionário com os campos das estacas, sem 'id' e 'assinatura'
            estaca_vals = {
                'nome_estaca': estaca.nome_estaca,  # Substitua pelo nome real do campo
                'profundidade': estaca.profundidade,  # Adicione outros campos conforme necessário
                'data': estaca.data,  # Exemplo de campo adicional
                'relatorio_id': new_report.id,
                'service_id': estaca.service_id.id,  # Associa a nova estaca ao novo relatório
                'observacao': estaca.observacao,   # Associa a nova estaca ao novo relatório
                'sale_order_id': estaca.sale_order_id.id,   # Associa a nova estaca ao novo relatório
                'sale_order_line_id': estaca.sale_order_line_id.id,  # Associa a nova estaca ao novo relatório
                'variante_id': estaca.variante_id.id,   # Associa a nova estaca ao novo relatório
                'service_template_id': estaca.service_template_id.id,   # Associa a nova estaca ao novo relatório'foundation_relatario_id': new_report.id,  # Associa a nova estaca ao novo relatório
                'foundation_maquina_registro_id': estaca.foundation_maquina_registro_id.id

                # Continue adicionando campos específicos das estacas
            }

            # Cria a nova estaca associada ao novo relatório
            self.env['foundation.estacas'].create(estaca_vals)

        # Retorna uma ação para abrir o novo registro no modo de edição
        return {
            'type': 'ir.actions.act_window',
            'name': 'Relatório Duplicado',
            'view_mode': 'form',
            'res_model': 'foundation.relatorios',
            'res_id': new_report.id,
            'target': 'current',  # Abre o registro no modo de edição
            'flags': {'initial_mode': 'edit'}  # Abre diretamente no modo de edição
        }




