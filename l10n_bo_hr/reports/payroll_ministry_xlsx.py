# -*- coding: utf-8 -*-
import calendar
from odoo import models
from datetime import datetime, date
from odoo.exceptions import ValidationError


class PayrollAReportXls(models.AbstractModel):
    _name = 'report.l10n_bo_hr.payroll_a_xlsx.xlsx'
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
            hour = 0
            for day_line in pays.worked_days_line_ids:
                day += day_line.number_of_days
                hour += day_line.number_of_hours

            activo = 0
            asegurado = 0
            if contract.retiree:
                tipo_aseg = 'DEPENDIENTE'
            else:
                tipo_aseg = 'JUBILADO'

            # Navegar las lineas
            basicbo = 0
            bono_ant = 0
            bono_dom = 0
            horas_ext = 0
            otros_bonos = 0
            total_ganado = 0
            afp = 0
            aporte_solidario = 0
            rciva = 0
            otros_desc = 0
            total_desc = 0
            liquido_pag = 0
            for lines in payslip.line_ids:
                if lines.code == 'BONO_A':
                    bono_ant = lines.total
                if lines.code == 'BONO_HEX_DOM':
                    bono_dom = lines.total
                if lines.code in ('BONO_F', 'BONO_HEX', 'BONO_HEX_NOCT', 'BONO_O'):
                    otros_bonos += lines.total
                if lines.code == 'GROSSBO':
                    total_ganado = lines.total
                if lines.code == 'AFP':
                    afp = lines.total
                if lines.code == 'SOL':
                    aporte_solidario = lines.total
                if lines.code == 'RCIVA_TOTAL':
                    if lines.total > 0:
                        rciva = lines.total
                if lines.code in ('ADE', 'PRE'):
                    otros_desc += lines.total
                if lines.code == 'TOTAL_D':
                    total_desc = lines.total
                if lines.code == 'NETBO':
                    liquido_pag = lines.total

            name_complete = employee.all_name
            if employee.all_name_two:
                name_complete = employee.all_name + ' ' + employee.all_name_two

            genero = 'M'
            if employee.gender == 'female':
                genero = 'F'
            vals = {
                'c7': employee.identification_id,
                'd7': employee.expedido,
                'e7': employee.paternal_surname,
                'f7': employee.maternal_surname,
                'g7': name_complete,
                'h7': employee.country_id.name,
                'i7': employee.birthday,
                'j7': genero,
                'k7': contract.job_id.name,
                'l7': contract.date_start,
                'm7': day,
                'n7': round(hour / day),
                'o7': contract.wage,
                'p7': bono_ant,
                'r7': bono_dom,
                's7': otros_bonos,
                't7': total_ganado,
                'u7': afp,
                'v7': aporte_solidario,
                'w7': rciva,
                'x7': otros_desc,
                'y7': total_desc,
                'z7': liquido_pag,
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
        sheet.set_column('D:D', 5)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 5)
        sheet.set_column('K:Z', 12)
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
        sheet.merge_range('B2:D2', 'NOMBRE O RAZÓN SOCIAL', first_line_format_left)
        sheet.write('E2', object.company_id.name, first_line_format_left2)
        sheet.merge_range('B3:D3', 'CÓDIGO DE EMPLEADOR', first_line_format_left)
        sheet.write('E3', object.company_id.cod_empleador, first_line_format_left2)
        sheet.merge_range('H2:M2', 'PLANILLA DE SUELDOS Y SALARIOS', first_line_format_2)
        sheet.merge_range('H3:M3', 'Correspondiente al mes de ' + mes, first_line_format)
        sheet.merge_range('H4:M4', '(Expresado en Bolivianos)', first_line_format)

        sheet.write('E6', 'N° PATRONAL', first_line_format_left)
        sheet.write('F6', object.company_id.caja_salud, first_line_format_left2)
        sheet.write('B7', 'N°', border_format)
        sheet.write('C7', 'CARNET DE\n IDENTIDAD', border_format)
        sheet.write('D7', 'EXP', border_format)
        sheet.write('E7', 'APELLIDO \nPATERNO', border_format)
        sheet.write('F7', 'APELLIDO \nMATERNO', border_format)
        sheet.write('G7', 'NOMBRES', border_format)
        sheet.write('H7', 'NACIONALIDAD', border_format)
        sheet.write('I7', 'FECHA DE \nNACIMIENTO', border_format)
        sheet.write('J7', 'SEXO(F/M)', border_format)
        sheet.write('K7', 'OCUPACIÓN QUE \nDESEMPEÑA', border_format)
        sheet.write('L7', 'FECHA DE INGRESO', border_format)
        sheet.write('M7', 'DIAS PAG. MES', border_format)
        sheet.write('N7', 'HRS/DIA\nPAGADO', border_format)
        sheet.write('O7', 'HABER\nBASICO', border_format)
        sheet.write('P7', 'BONO DE\nANTIGUEDAD', border_format)
        sheet.write('Q7', 'BONO\nPRODUCCIÓN', border_format)
        sheet.write('R7', 'BONO\nDOMINICAL', border_format)
        sheet.write('S7', 'OTROS\nBONOS', border_format)
        sheet.write('T7', 'TOTAL\nGANADO', border_format)
        sheet.write('U7', 'AFP', border_format)
        sheet.write('V7', 'APORTE\nSOLIDARIO', border_format)
        sheet.write('W7', 'RC-IVA', border_format)
        sheet.write('X7', 'ANTICIPIOS\nOTROS DESC.', border_format)
        sheet.write('Y7', 'TOTAL\nDESCUENTOS', border_format)
        sheet.write('Z7', 'LIQUIDO\nPAGABLE', border_format)
        mt = nt = ot = pt = rt = st = tt = ut = vt = wt = xt = yt = zt = 0
        for each in self.get_lines(object):
            sheet.write('B' + str(i), j, blue_format)
            sheet.write('C' + str(i), str(each['c7']), blue_format)
            sheet.write('D' + str(i), str(each['d7']), blue_format)
            sheet.write('E' + str(i), str(each['e7']), blue_format)
            sheet.write('F' + str(i), str(each['f7']), blue_format)
            sheet.write('G' + str(i), str(each['g7']), blue_format)
            sheet.write('H' + str(i), str(each['h7']), blue_format)
            sheet.write('I' + str(i), str(each['i7']), blue_format)
            sheet.write('J' + str(i), str(each['j7']), blue_format)
            sheet.write('K' + str(i), str(each['k7']), blue_format)
            sheet.write('L' + str(i), str(each['l7']), blue_format)
            sheet.write('M' + str(i), each['m7'], blue_format)
            sheet.write('N' + str(i), each['n7'], blue_format)
            sheet.write('O' + str(i), each['o7'], blue_format_num)
            sheet.write('P' + str(i), each['p7'], blue_format_num)
            sheet.write('Q' + str(i), 0, blue_format_num)
            sheet.write('R' + str(i), each['r7'], blue_format_num)
            sheet.write('S' + str(i), each['s7'], blue_format_num)
            sheet.write('T' + str(i), each['t7'], blue_format_num)
            sheet.write('U' + str(i), each['u7'], blue_format_num)
            sheet.write('V' + str(i), each['v7'], blue_format_num)
            sheet.write('W' + str(i), each['w7'], blue_format_num)
            sheet.write('X' + str(i), each['x7'], blue_format_num)
            sheet.write('Y' + str(i), each['y7'], blue_format_num)
            sheet.write('Z' + str(i), each['z7'], blue_format_num)
            mt += each['m7']
            nt += each['n7']
            ot += each['o7']
            pt += each['p7']
            rt += each['r7']
            st += each['s7']
            tt += each['t7']
            ut += each['u7']
            vt += each['v7']
            wt += each['w7']
            xt += each['x7']
            yt += each['y7']
            zt += each['z7']
            i += 1
            j += 1
        sheet.write('L' + str(i), 'TOTALES:', blue_format_b)
        sheet.write('M' + str(i), mt, blue_format_num_b)
        sheet.write('N' + str(i), nt, blue_format_num_b)
        sheet.write('O' + str(i), ot, blue_format_num_b)
        sheet.write('P' + str(i), pt, blue_format_num_b)
        sheet.write('Q' + str(i), 0, blue_format_num_b)
        sheet.write('R' + str(i), rt, blue_format_num_b)
        sheet.write('S' + str(i), st, blue_format_num_b)
        sheet.write('T' + str(i), tt, blue_format_num_b)
        sheet.write('U' + str(i), ut, blue_format_num_b)
        sheet.write('V' + str(i), vt, blue_format_num_b)
        sheet.write('W' + str(i), wt, blue_format_num_b)
        sheet.write('X' + str(i), xt, blue_format_num_b)
        sheet.write('Y' + str(i), yt, blue_format_num_b)
        sheet.write('Z' + str(i), zt, blue_format_num_b)
