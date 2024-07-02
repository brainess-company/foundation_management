from odoo import models, fields, api
import io
import base64
import xlsxwriter

class ReportWizard(models.TransientModel):
    _name = 'report.wizard'
    _description = 'Wizard para selecionar o período para o relatório'

    date_start = fields.Date(string="Data Inicial", required=True)
    date_end = fields.Date(string="Data Final", required=True)

    def generate_report(self):
        chamadas = self.env['foundation.chamada'].search([
            ('data', '>=', self.date_start),
            ('data', '<=', self.date_end)
        ])

        # Dicionário para armazenar a contagem de dias únicos de presença por funcionário, obra e empresa
        presence_count = {}

        for chamada in chamadas:
            for lista_presenca in chamada.lista_presenca_ids:
                funcionario_id = lista_presenca.funcionario_id.id
                obra_id = chamada.obra_id.id
                company_id = lista_presenca.company_id.id
                data_presenca = chamada.data

                key = (funcionario_id, obra_id, company_id)
                if key not in presence_count:
                    presence_count[key] = set()
                presence_count[key].add(data_presenca)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet()

        # Adicionar cabeçalhos
        headers = ['Funcionário', 'Obra', 'Empresa', 'Quantidade de Dias']
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header)

        row = 1
        for key, days in presence_count.items():
            funcionario_id, obra_id, company_id = key
            funcionario = self.env['hr.employee'].browse(funcionario_id)
            obra = self.env['foundation.obra'].browse(obra_id)
            company = self.env['res.company'].browse(company_id)
            sheet.write(row, 0, funcionario.name)
            sheet.write(row, 1, obra.nome_obra)
            sheet.write(row, 2, company.name)
            sheet.write(row, 3, len(days))
            row += 1

        workbook.close()
        output.seek(0)
        xls_data = output.read()
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'relatorio_presenca.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(xls_data),
            'store_fname': 'relatorio_presenca.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }
