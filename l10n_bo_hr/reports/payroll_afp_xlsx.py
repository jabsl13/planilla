# -*- coding: utf-8 -*-
from datetime import datetime, date
import calendar
from odoo import models


class PayrollReportXls(models.AbstractModel):
    _name = 'report.l10n_bo_hr.payroll_afp_xlsx.xlsx'
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
            ap_laboral = 0
            ap_solidario = 0
            ap_may_13 = 0
            ap_patronal = 0
            ap_sol2 = 0
            ap_provi = 0
            for lines in payslip.line_ids:
                if lines.code == 'GROSSBO':
                    if not contract.retiree:
                        activo = lines.total
                    else:
                        asegurado = lines.total
                if lines.code == 'afp_inf_0':
                    ap_laboral = lines.total
                if lines.code == 'afp_inf_1':
                    ap_solidario = lines.total
                if lines.code in ('afp_inf_4', 'afp_inf_5', 'afp_inf_6'):
                    ap_may_13 = lines.total
                if lines.code == 'afp_inf_2':
                    ap_patronal = lines.total
                if lines.code == 'afp_inf_3':
                    ap_sol2 = lines.total
                if lines.code == 'afp_inf_7':
                    ap_provi = lines.total

            vals = {
                'c7': employee.identification_id,
                'd7': employee.expedido,
                'e7': contract.nua_cua,
                'f7': contract.afp_manager_id.name,
                'g7': employee.paternal_surname,
                'h7': employee.maternal_surname,
                'i7': employee.all_name,
                'j7': employee.all_name_two,
                'k7': employee.address_id.city,
                'n7': day,
                'o7': tipo_aseg,
                'p7': activo,
                'q7': asegurado,
                'r7': ap_laboral,
                's7': ap_solidario,
                't7': ap_may_13,
                'u7': ap_patronal,
                'v7': ap_sol2,
                'w7': ap_provi
            }
            lines_afp.append(vals)
        return lines_afp

    def generate_xlsx_report(self, workbook, data, object):
        i = 8
        j = 1
        sheet = workbook.add_worksheet()
        sheet.set_column('A:A', 2)
        sheet.set_column('B:B', 5)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:O', 15)
        sheet.set_column('P:Z', 10)
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

        get_line = self.get_lines(object)
        mes = dict(object._fields['month'].selection).get(object.month)
        sheet.merge_range('B2:D2', 'NOMBRE O RAZÓN SOCIAL', first_line_format_left)
        sheet.write('E2', object.company_id.name, first_line_format_left2)
        sheet.merge_range('B3:D3', 'CÓDIGO DE EMPLEADOR', first_line_format_left)
        sheet.write('E3', object.company_id.cod_empleador, first_line_format_left2)
        sheet.merge_range('H2:M2', 'PLANILLA DE SUELDOS Y SERVICIOS', first_line_format)
        sheet.merge_range('H3:M3', 'ADMINISTRADORAS DE FONDOS DE PENSIONES', first_line_format_2)
        sheet.merge_range('H4:M4', 'Correspondiente al mes de ' + mes, first_line_format)

        sheet.write('B7', 'ITEM', border_format)
        sheet.write('C7', 'DOC. IDENTIDAD', border_format)
        sheet.write('D7', 'EXP', border_format)
        sheet.write('E7', 'NUA', border_format)
        sheet.write('F7', 'AFP', border_format)
        sheet.write('G7', 'APELLIDO \nPATERNO', border_format)
        sheet.write('H7', 'APELLIDO \nMATERNO', border_format)
        sheet.write('I7', 'PRIMER NOMBRE', border_format)
        sheet.write('J7', 'SEGUNDO NOMBRE', border_format)
        sheet.write('K7', 'DPTO.', border_format)
        sheet.write('L7', 'NOVEDAD', border_format)
        sheet.write('M7', 'FECHA NOVEDAD', border_format)
        sheet.write('N7', 'DIAS COTIZ.', border_format)
        sheet.write('O7', 'TIPO \nASEGURADO', border_format)
        sheet.write('P7', 'ACTIVO', border_format)
        sheet.write('Q7', 'JUBILADO', border_format)
        sheet.write('R7', 'AP. LABORAL \n12.21%', border_format)
        sheet.write('S7', 'AP. SOLIDARIO \n0.50%', border_format)
        sheet.write('T7', 'AP. > 13000\n1%-5%-10%', border_format)
        sheet.write('U7', 'AP. PATRONAL\n 1.71%', border_format)
        sheet.write('V7', 'AP. SOLIDARIO\n 3%', border_format)
        sheet.write('W7', 'PROVIVIENDA\n 2%', border_format)
        nt = pt = qt = rt = st = tt = ut = vt = wt = 0
        for each in get_line:
            sheet.write('B' + str(i), j, blue_format)
            sheet.write('C' + str(i), each['c7'], blue_format)
            sheet.write('D' + str(i), each['d7'], blue_format)
            sheet.write('E' + str(i), each['e7'], blue_format)
            sheet.write('F' + str(i), each['f7'], blue_format)
            sheet.write('G' + str(i), each['g7'], blue_format)
            sheet.write('H' + str(i), each['h7'], blue_format)
            sheet.write('I' + str(i), each['i7'], blue_format)
            sheet.write('J' + str(i), each['j7'], blue_format)
            sheet.write('K' + str(i), each['k7'], blue_format)
            sheet.write('L' + str(i), '', blue_format)
            sheet.write('M' + str(i), '', blue_format)
            sheet.write('N' + str(i), each['n7'], blue_format)
            sheet.write('O' + str(i), each['o7'], blue_format)
            sheet.write('P' + str(i), each['p7'], blue_format_num)
            sheet.write('Q' + str(i), each['q7'], blue_format_num)
            sheet.write('R' + str(i), each['r7'], blue_format_num)
            sheet.write('S' + str(i), each['s7'], blue_format_num)
            sheet.write('T' + str(i), each['t7'], blue_format_num)
            sheet.write('U' + str(i), each['u7'], blue_format_num)
            sheet.write('V' + str(i), each['v7'], blue_format_num)
            sheet.write('W' + str(i), each['w7'], blue_format_num)
            nt += each['n7']
            pt += each['p7']
            qt += each['q7']
            rt += each['r7']
            st += each['s7']
            tt += each['t7']
            ut += each['u7']
            vt += each['v7']
            wt += each['w7']
            i = i + 1
            j = j + 1
        sheet.write('M' + str(i), 'TOTALES:', blue_format_b)
        sheet.write('N' + str(i), nt, blue_format_num_b)
        sheet.write('P' + str(i), pt, blue_format_num_b)
        sheet.write('Q' + str(i), qt, blue_format_num_b)
        sheet.write('R' + str(i), rt, blue_format_num_b)
        sheet.write('S' + str(i), st, blue_format_num_b)
        sheet.write('T' + str(i), tt, blue_format_num_b)
        sheet.write('U' + str(i), ut, blue_format_num_b)
        sheet.write('V' + str(i), vt, blue_format_num_b)
        sheet.write('W' + str(i), wt, blue_format_num_b)
