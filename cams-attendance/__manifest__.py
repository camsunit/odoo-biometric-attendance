# -*- coding: utf-8 -*-
{
    'name': "CAMS Realtime Biometric Attendance",

    'summary': """
        Receives the realtime biometric attendance through CAMS API and updates in hr.attendance module.
        """,

    'description': """
        The module is developed based on the CAMS API as documented at http://camsunit.com/application/biometric-web-api.html. It receives the biometric attendance on realtime and integrates with hr.attendance module
    """,

    'author': "Dheeram Innovations",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['hr','hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/config.xml',
        'views/inherited_employee_view.xml',
    ]
}