# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request
from datetime import datetime, timedelta
import json


class CamsAttendance(http.Controller):

    @http.route('/cams/biometric-api3.0/', method=["POST"], csrf=False, auth='public', type="http")
    def generate_attendance(self, **params):
        """
        Gets the params from the machine data and create
        record in attendance module.
        """
        try:
            db_name = params.get('db')
            if db_name:
                if (request.session.db != db_name):
                    request.session.db = db_name
                    return "Database changed"
        except:
            return "Not found!"

        try:
            machine_id = params.get('stgid')
            if (len(machine_id) == 0):
                return "enter service_tag_id"
        except:
            return "include service_tag_id!"

        try:
            data = json.loads(request.httprequest.data)
            json_object = json.dumps(data)
            real_time = json.loads(json_object)
        except ValueError as err:
            return "invalid json format!"

        try:
            employee_ref = real_time['RealTime']['PunchLog']['UserId']
            request.env.uid = SUPERUSER_ID
            employee = request.env['hr.employee'].sudo().search([('employee_ref', '=', employee_ref)])

            attendance_type = real_time['RealTime']['PunchLog']['Type']
            attendance_time = real_time['RealTime']['PunchLog']['LogTime']
            auth_token = real_time['RealTime']['AuthToken']
        except:
            return '{' \
                   '    "status": "done" ,' \
                   '    "error": "Invalid raw format"' \
                   '}'

        hdiff = '0'
        mdiff = '0'

        attendance_time = attendance_time.split(" GMT ")

        if attendance_time[1][0] == '-':
            hdiff = '+' + attendance_time[1][1:3]
        elif attendance_time[1][0] == '+':
            hdiff = '-' + attendance_time[1][1:3]

        if attendance_time[1][0] == '-':
            mdiff = '+' + attendance_time[1][3:5]
        elif attendance_time[1][0] == '+':
            mdiff = '-' + attendance_time[1][3:5]

        try:
            att_time_obj = datetime.strptime(attendance_time[0].rstrip(), "%Y-%m-%d %H:%M:%S") + timedelta(
                hours=int(hdiff), minutes=int(mdiff))
        except:
            return "Invalid Log Time"

        service_tag_id = request.env['device.service.tag'].sudo().search([('service_tag_id', '=', machine_id)])

        if service_tag_id:
            stg_auth_token = service_tag_id[0].auth_token
            if stg_auth_token != auth_token:
                return "Invalid Token!!"
        else:
            return "Invalid Service Tag ID"

        gmt_time = timedelta(hours=int(hdiff), minutes=int(mdiff))
        params = request.env['ir.config_parameter'].sudo()
        direction = params.get_param('cams-attendance.direction') or '2'
        if not direction:
            direction = '2'

        if employee:
            attendance = request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee.id), ('check_in', '=', att_time_obj)], limit=1)
            if attendance:
                return '{' \
                       '    "status": "done" ' \
                       '}'

            attendance = request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee.id), ('check_out', '=', att_time_obj)], limit=1)
            if attendance:
                return '{' \
                       '    "status": "done" ' \
                       '}'

            # Option 1
            if direction == '1':
                attendance = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)], limit=1)
                if attendance:
                    if attendance.check_in:
                        att_gmt_add = (attendance.check_in - (gmt_time)).date()
                        att_time_obj_gmt = (att_time_obj - (gmt_time)).date()

                        if att_gmt_add == att_time_obj_gmt:
                            attendance.check_out = att_time_obj
                        else:
                            vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                            attendance = request.env['hr.attendance'].create(vals)
                    else:
                        vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                        attendance = request.env['hr.attendance'].create(vals)
                else:
                    vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                    attendance = request.env['hr.attendance'].create(vals)

            # Option 2
            if direction == '2':
                if attendance_type == 'CheckIn':
                    attendance = request.env['hr.attendance'].search(
                        [('employee_id', '=', employee.id), ('check_out', '>', att_time_obj)], order='create_date asc',
                        limit=1)
                    if attendance:
                        attendance.check_in = att_time_obj
                    else:
                        vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                        attendance = request.env['hr.attendance'].create(vals)

                if attendance_type == 'CheckOut':
                    attendance = request.env['hr.attendance'].search([('employee_id', '=', employee.id)],
                                                                     order='create_date desc', limit=1)
                    if not attendance:
                        vals = {'employee_id': employee.id, 'check_out': att_time_obj, 'machine_id': machine_id}
                        attendance = request.env['hr.attendance'].create(vals)
                    else:
                        attendance = request.env['hr.attendance'].search(
                            [('employee_id', '=', employee.id), ('check_in', '<', att_time_obj)],
                            order='create_date desc', limit=1)
                        if not attendance.check_out:
                            attendance.check_out = att_time_obj
                        else:
                            vals = {'employee_id': employee.id, 'check_out': att_time_obj, 'machine_id': machine_id}
                            attendance = request.env['hr.attendance'].create(vals)
            # Option 3
            if direction == '3':
                attendance = request.env['hr.attendance'].search(
                    [('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)
                if not attendance:
                    vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                    attendance = request.env['hr.attendance'].create(vals)
                else:
                    attendance_date = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)],
                                                                                 limit=1)

                    att_gmt_add = (attendance_date.check_in - (gmt_time)).date()
                    att_time_obj_gmt = (att_time_obj - (gmt_time)).date()

                    if attendance.check_in and (att_gmt_add == att_time_obj_gmt):
                        attendance.check_out = att_time_obj
                    elif attendance.check_out:
                        vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                        attendance = request.env['hr.attendance'].create(vals)
                    else:
                        vals = {'employee_id': employee.id, 'check_in': att_time_obj, 'machine_id': machine_id}
                        attendance = request.env['hr.attendance'].create(vals)

            return '{' \
                   '    "status": "done" ' \
                   '}'

        else:
            return '{' \
                   '    "status": "done", ' \
                   '    "error": "Invalid Employee Id"' \
                   '}'





