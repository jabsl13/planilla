from odoo import models, fields, api
import pytz
from odoo.osv.expression import AND, OR
from datetime import datetime, timedelta
from collections import defaultdict
from operator import itemgetter
from odoo.tools.float_utils import float_is_zero


class HrAttendace(models.Model):
    _inherit = 'hr.attendance'

    def _update_overtime(self, employee_attendance_dates=None):
        if employee_attendance_dates is None:
            employee_attendance_dates = self._get_attendances_dates()

        overtime_to_unlink = self.env['hr.attendance.overtime']
        overtime_vals_list = []

        for emp, attendance_dates in employee_attendance_dates.items():
            # get_attendances_dates devuelve la fecha traducida de la zona horaria local sin tzinfo,
            # y contiene toda la fecha que necesitamos para verificar las horas extra
            emp_tz = pytz.timezone(emp._get_tz())
            attendance_domain = []
            for attendance_date in attendance_dates:
                attendance_domain = OR([attendance_domain, [
                    ('check_in', '>=', attendance_date[0]), ('check_in', '<', attendance_date[0] + timedelta(hours=24)),
                ]])
            attendance_domain = AND([[('employee_id', '=', emp.id)], attendance_domain])

            # Asistencias por día LOCAL
            attendances_per_day = defaultdict(lambda: self.env['hr.attendance'])
            all_attendances = self.env['hr.attendance'].search(attendance_domain)
            for attendance in all_attendances:
                check_in_day_start = attendance._get_day_start_and_day(attendance.employee_id, attendance.check_in)
                attendances_per_day[check_in_day_start[1]] += attendance

            # Como _attendance_intervals_batch y _leave_intervals_batch toman fechas localizadas, necesitamos localizar esas fechas
            start = pytz.utc.localize(min(attendance_dates, key=itemgetter(0))[0])
            stop = pytz.utc.localize(max(attendance_dates, key=itemgetter(0))[0] + timedelta(hours=24))

            # Recuperar intervalos de asistencia esperados
            expected_attendances = emp.resource_calendar_id._attendance_intervals_batch(
                start, stop, emp.resource_id
            )[emp.resource_id.id]
            # Reste las licencias globales y las licencias de los empleados
            leave_intervals = emp.resource_calendar_id._leave_intervals_batch(start, stop, emp.resource_id)
            expected_attendances -= leave_intervals[False] | leave_intervals[emp.resource_id.id]

            # working_times = {date: [(start, stop)]}
            working_times = defaultdict(lambda: [])
            for expected_attendance in expected_attendances:
                # Excluir resource.calendar.attendance
                working_times[expected_attendance[0].date()].append(expected_attendance[:2])

            overtimes = self.env['hr.attendance.overtime'].sudo().search([
                ('employee_id', '=', emp.id),
                ('date', 'in', [day_data[1] for day_data in attendance_dates]),
                ('adjustment', '=', False),
            ])

            company_threshold = emp.company_id.overtime_company_threshold / 60.0
            employee_threshold = emp.company_id.overtime_employee_threshold / 60.0

            for day_data in attendance_dates:
                attendance_date = day_data[1]
                attendances = attendances_per_day.get(attendance_date, self.browse())
                unfinished_shifts = attendances.filtered(lambda a: not a.check_out)
                overtime_duration = 0
                overtime_duration_real = 0
                # Las horas extras no se cuentan si algún turno no está cerrado o si no hay asistencia para ese día,
                # esto podria pasar al borrar asistencias.
                if not unfinished_shifts and attendances:
                    # La empleada generalmente no trabaja ese día
                    if not working_times[attendance_date]:
                        # El usuario no tiene ningún resource_calendar_attendance para ese día (fin de semana, por ejemplo)
                        overtime_duration = sum(attendances.mapped('worked_hours'))
                        overtime_duration_real = overtime_duration
                    # El empleado generalmente trabaja ese día
                    else:
                        # Compute start and end time for that day
                        planned_start_dt, planned_end_dt = False, False
                        planned_work_duration = 0
                        for calendar_attendance in working_times[attendance_date]:
                            planned_start_dt = min(planned_start_dt, calendar_attendance[0]) if planned_start_dt else \
                                calendar_attendance[0]
                            planned_end_dt = max(planned_end_dt, calendar_attendance[1]) if planned_end_dt else \
                                calendar_attendance[1]
                            planned_work_duration += (calendar_attendance[1] - calendar_attendance[
                                0]).total_seconds() / 3600.0
                        # Count time before, during and after 'working hours'
                        pre_work_time, work_duration, post_work_time = 0, 0, 0

                        for attendance in attendances:
                            # consider check_in as planned_start_dt if within threshold
                            # if delta_in < 0: Checked in after supposed start of the day
                            # if delta_in > 0: Checked in before supposed start of the day
                            local_check_in = pytz.utc.localize(attendance.check_in)
                            delta_in = (planned_start_dt - local_check_in).total_seconds() / 3600.0

                            # Started before or after planned date within the threshold interval
                            if (delta_in > 0 and delta_in <= company_threshold) or \
                                    (delta_in < 0 and abs(delta_in) <= employee_threshold):
                                local_check_in = planned_start_dt
                            local_check_out = pytz.utc.localize(attendance.check_out)

                            # same for check_out as planned_end_dt
                            delta_out = (local_check_out - planned_end_dt).total_seconds() / 3600.0
                            # if delta_out < 0: Checked out before supposed start of the day
                            # if delta_out > 0: Checked out after supposed start of the day

                            # Finised before or after planned date within the threshold interval
                            if (delta_out > 0 and delta_out <= company_threshold) or \
                                    (delta_out < 0 and abs(delta_out) <= employee_threshold):
                                local_check_out = planned_end_dt

                            # There is an overtime at the start of the day
                            if local_check_in < planned_start_dt:
                                pre_work_time += (min(planned_start_dt,
                                                      local_check_out) - local_check_in).total_seconds() / 3600.0
                            # Interval inside the working hours -> Considered as working time
                            if local_check_in <= planned_end_dt and local_check_out >= planned_start_dt:
                                work_duration += (min(planned_end_dt, local_check_out) - max(planned_start_dt,
                                                                                             local_check_in)).total_seconds() / 3600.0
                            # There is an overtime at the end of the day
                            if local_check_out > planned_end_dt:
                                post_work_time += (local_check_out - max(planned_end_dt,
                                                                         local_check_in)).total_seconds() / 3600.0

                        # Overtime within the planned work hours + overtime before/after work hours is > company threshold
                        overtime_duration = work_duration - planned_work_duration
                        if pre_work_time > company_threshold:
                            overtime_duration += pre_work_time
                        if post_work_time > company_threshold:
                            overtime_duration += post_work_time
                        # Global overtime including the thresholds
                        overtime_duration_real = sum(attendances.mapped('worked_hours')) - planned_work_duration

                overtime = overtimes.filtered(lambda o: o.date == attendance_date)
                if not float_is_zero(overtime_duration, 2) or unfinished_shifts:
                    # Do not create if any attendance doesn't have a check_out, update if exists
                    if unfinished_shifts:
                        overtime_duration = 0
                    # Validamos si hay horas extra nocturno
                    user_tz = self.env.context.get('tz')
                    for line_s in self:
                        start_ini = pytz.utc.localize(line_s.check_in)
                        start_ini = start_ini.astimezone(pytz.timezone(user_tz))
                        stop_ini = pytz.utc.localize(line_s.check_out)
                        stop_ini = stop_ini.astimezone(pytz.timezone(user_tz))
                        horas = 0
                        if start_ini.hour >= 20:
                            if stop_ini.hour > 20:
                                horas = stop_ini.hour - start_ini.hour
                            elif stop_ini.hour > 0:
                                horas = 24 - start_ini.hour + stop_ini.hour
                        elif 0 < start_ini.hour < 6:
                            if stop_ini.hour <= 6:
                                horas = stop_ini.hour - start_ini.hour
                            else:
                                horas = 6 - start_ini.hour
                        else:
                            if stop_ini.hour >= 20:
                                horas = stop_ini.hour - 20
                            elif stop_ini.hour > 0:
                                horas = 4 + stop_ini.hour

                    if not overtime and overtime_duration:
                        overtime_vals_list.append({
                            'employee_id': emp.id,
                            'date': attendance_date,
                            'duration': overtime_duration,
                            'horas_nocturno': horas,
                            'duration_real': overtime_duration_real,
                        })
                    elif overtime:
                        overtime.sudo().write({
                            'duration': overtime_duration,
                            'duration_real': overtime_duration,
                            'horas_nocturno': horas,
                        })
                elif overtime:
                    overtime_to_unlink |= overtime
        self.env['hr.attendance.overtime'].sudo().create(overtime_vals_list)
        overtime_to_unlink.sudo().unlink()
