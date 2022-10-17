# -*- coding: utf-8 -*-
{
    'name': "Zkteco, eSSL, Cams Biometrics Attendance Integration Module",

    'summary': """
        Receives the attendanc/punches from the biometric devices and updates in hr.attendance module of odoo server.
        """,

    'description': """
        The module is developed based on the Cams biometric web api as documented at http://camsunit.com/application/biometric-web-api.html. It receives the biometric attendance on realtime and integrates with hr.attendance module. 
        
	It supports all the cams biometrics machines listed at https://camsunit.com/product/home.html
        It alos supports 
        	ZKTeco, 
        	eSSL, 
        	Identix, 
        	BioMax 
        	and more biometric machines provided they are verified at https://developer.camsunit.com/
        
        Module requires valid API license as listed at https://camsunit.com/application/biometric-web-api.html#api_cost
        
    """,

    'author': "Cams Biometrics",
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
