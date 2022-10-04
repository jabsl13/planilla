# -*- coding: utf-8 -*-
import calendar
from odoo import models
from datetime import datetime, date
from odoo.exceptions import ValidationError


class PayrollBReportXls(models.AbstractModel):
    _name = 'report.l10n_bo_hr.payroll_b_xlsx.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, object):
        days = calendar.monthrange(int(object.year), int(object.month))
        date_init = date(year=int(object.year), month=int(object.month), day=1)
        date_end = date(year=int(object.year), month=int(object.month), day=int(days[1]))
        lines_afp = []
        payslips = self.env['hr.payslip'].search([('date_from', '>=', date_init),
                                                  ('date_to', '<=', date_end),
                                                  ('state', '!=', 'cancel')])

        for payslip in payslips:
            pays = payslip
            employee = payslip.employee_id
            contract = payslip.contract_id
            day = 0
            for day_line in pays.worked_days_line_ids:
                day += day_line.number_of_days

            activo = 0
            asegurado = 0
            if contract.retiree:
                tipo_aseg = 'DEPENDIENTE'
            else:
                tipo_aseg = 'JUBILADO'

            # Navegar las lineas
            monto_neto = 0
            dos_sala = 0
            impuesto_rciva = 0
            form210 = 0
            impue_3 = 0
            rc_fisco = 0
            rc_favor = 0
            saldo_anterior = 0
            total_pagar = 0
            valid = 0
            for lines in payslip.line_ids:
                if lines.code == 'TOT_NETO':
                    if lines.total < (object.company_id.sueldo_min * 4):
                        valid = 1
                if lines.code == 'GROSSBO':
                    monto_neto = lines.total
                if lines.code == 'rciva_inf1':
                    dos_sala = lines.total
                if lines.code == 'rciva_inf2':
                    impuesto_rciva = lines.total
                if lines.code == 'rciva_inf4':
                    form210 = lines.total
                if lines.code == 'rciva_inf3':
                    impue_3 = lines.total
                if lines.code == 'RCIVA_TOTAL':
                    if lines.total >= 0:
                        rc_fisco = lines.total
                        total_pagar = lines.total
                    else:
                        rc_favor = lines.total * -1
                        total_pagar = 0
                if lines.code == 'rciva_inf3':
                    impue_3 = lines.total
                if lines.code == 'rciva_inf5':
                    saldo_anterior = lines.total
            if valid == 1:
                continue
            name_complete = employee.all_name
            if employee.all_name_two:
                name_complete = employee.all_name + ' ' + employee.all_name_two

            vals = {
                'b7': object.year,
                'c7': object.month,
                'd7': employee.registration_number,
                'e7': name_complete,
                'f7': employee.paternal_surname,
                'g7': employee.maternal_surname,
                'h7': employee.identification_id,
                'i7': employee.expedido,
                'j7': 'V',
                'k7': monto_neto,
                'l7': dos_sala,
                'm7': monto_neto + dos_sala,
                'n7': impuesto_rciva,
                'o7': form210,
                'p7': impue_3,
                'q7': rc_fisco,
                'r7': rc_favor,
                's7': saldo_anterior,
                't7': 0,
                'u7': total_pagar
            }
            lines_afp.append(vals)
        return lines_afp

    def generate_xlsx_report(self, workbook, data, object):
        i = 8
        j = 1
        sheet = workbook.add_worksheet()
        sheet.set_column('A:A', 2)
        sheet.set_column('B:B', 5)
        sheet.set_column('C:W', 15)
        sheet.set_row(6, 30)
        first_line_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 12,
        })
        first_line_format_left = workbook.add_format({
            'bold': 1,
            'align': 'left',
            'font_size': 11,
        })
        first_line_format_left2 = workbook.add_format({
            'bold': 0,
            'align': 'left',
            'font_size': 11,
        })
        first_line_format_2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'font_size': 15,
        })

        blue_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'font_size': 9,
            'num_format': '0',
        })
        blue_format_b = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'center',
            'font_size': 9,
        })

        blue_format_num = workbook.add_format({
            'border': 1,
            'align': 'right',
            'font_size': 9,
            'num_format': '#,##0.00',
        })
        blue_format_num_b = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'right',
            'font_size': 9,
            'num_format': '#,##0.00',
        })

        border_format = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E1F2',
            'font_size': 9,
            'text_wrap': True,
        })
        mes = dict(object._fields['month'].selection).get(object.month)
        sheet.write('B2', 'NOMBRE O RAZÓN SOCIAL', border_format)
        sheet.write('B3', 'CÓDIGO DE EMPLEADOR', border_format)
        sheet.merge_range('H2:M2', 'PLANILLA DE RC-IVA', first_line_format_2)
        sheet.merge_range('H3:M3', 'Correspondiente al mes de ' + mes, first_line_format)
        sheet.merge_range('H4:M4', '(Expresado en Bolivianos)', first_line_format)

        sheet.write('B7', 'AÑO', border_format)
        sheet.write('C7', 'PERIODO', border_format)
        sheet.write('D7', 'CÓDIGO\n DEPENDIENTE', border_format)
        sheet.write('E7', 'NOMBRES', border_format)
        sheet.write('F7', 'APELLIDO \nPATERNO', border_format)
        sheet.write('G7', 'APELLIDO \nMATERNO', border_format)
        sheet.write('H7', 'N° DE\nDOCUMENTO', border_format)
        sheet.write('I7', 'TIPO DE \nDOCUMENTO', border_format)
        sheet.write('J7', 'NOVEDADES', border_format)
        sheet.write('K7', 'MONTO INGRESO\nNETO', border_format)
        sheet.write('L7', 'DOS(2)\nS.M.N', border_format)
        sheet.write('M7', 'IMPORTE SUJETO\nA IMPUESTO', border_format)
        sheet.write('N7', 'IMPUESTO\nRC-IVA', border_format)
        sheet.write('O7', 'FORM 110', border_format)
        sheet.write('P7', '13% DE DOS(2)\nS.M.N.', border_format)
        sheet.write('Q7', 'SALDO A FAVOR\nFISCO', border_format)
        sheet.write('R7', 'SALDO A FAVOR\nDEPENDIENTE', border_format)
        sheet.write('S7', 'SALDO ANTERIOR', border_format)
        sheet.write('T7', 'SALDO ANTERIOR\nU.F.V,', border_format)
        sheet.write('U7', 'LIQUIDACIÓN EN LAS\nRETENCIONES', border_format)
        kt = lt = mt = nt = ot = pt = rt = st = tt = ut = 0
        for each in self.get_lines(object):
            sheet.write('B' + str(i), str(each['b7']), blue_format)
            sheet.write('C' + str(i), str(each['c7']), blue_format)
            sheet.write('D' + str(i), str(each['d7']), blue_format)
            sheet.write('E' + str(i), str(each['e7']), blue_format)
            sheet.write('F' + str(i), str(each['f7']), blue_format)
            sheet.write('G' + str(i), str(each['g7']), blue_format)
            sheet.write('H' + str(i), str(each['h7']), blue_format)
            sheet.write('I' + str(i), str(each['i7']), blue_format)
            sheet.write('J' + str(i), str(each['j7']), blue_format)
            sheet.write('K' + str(i), each['k7'], blue_format_num)
            sheet.write('L' + str(i), each['l7'], blue_format_num)
            sheet.write('M' + str(i), each['m7'], blue_format_num)
            sheet.write('N' + str(i), each['n7'], blue_format_num)
            sheet.write('O' + str(i), each['o7'], blue_format_num)
            sheet.write('P' + str(i), each['p7'], blue_format_num)
            sheet.write('Q' + str(i), each['q7'], blue_format_num)
            sheet.write('R' + str(i), each['r7'], blue_format_num)
            sheet.write('S' + str(i), each['s7'], blue_format_num)
            sheet.write('T' + str(i), each['t7'], blue_format_num)
            sheet.write('U' + str(i), each['u7'], blue_format_num)
            kt += each['k7']
            lt += each['l7']
            mt += each['m7']
            nt += each['n7']
            ot += each['o7']
            pt += each['p7']
            rt += each['r7']
            st += each['s7']
            tt += each['t7']
            ut += each['u7']
            i += 1
            j += 1
        sheet.write('J' + str(i), 'TOTALES:', blue_format_b)
        sheet.write('K' + str(i), kt, blue_format_num_b)
        sheet.write('L' + str(i), lt, blue_format_num_b)
        sheet.write('M' + str(i), mt, blue_format_num_b)
        sheet.write('N' + str(i), nt, blue_format_num_b)
        sheet.write('O' + str(i), ot, blue_format_num_b)
        sheet.write('P' + str(i), pt, blue_format_num_b)
        sheet.write('Q' + str(i), 0, blue_format_num_b)
        sheet.write('R' + str(i), rt, blue_format_num_b)
        sheet.write('S' + str(i), st, blue_format_num_b)
        sheet.write('T' + str(i), tt, blue_format_num_b)
        sheet.write('U' + str(i), ut, blue_format_num_b)
