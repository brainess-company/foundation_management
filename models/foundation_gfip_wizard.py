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

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet()

        # Adicionar cabeçalhos
        headers = ['Obra', 'Funcionário', 'Data', 'Presença']
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header)

        row = 1
        for chamada in chamadas:
            for lista_presenca in chamada.lista_presenca_ids:
                sheet.write(row, 0, chamada.nome_obra)
                sheet.write(row, 1, lista_presenca.funcionario_id.name)
                sheet.write(row, 2, chamada.data.strftime('%Y-%m-%d'))
                sheet.write(row, 3, 'Presente')
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
