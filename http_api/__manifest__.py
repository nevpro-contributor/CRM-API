# -*- coding: utf-8 -*-
{
    'name': "WebX API",
    'summary': """Update or POST method of RESTfull API.""",
    'author': "Nevpro Business Solution",
    'website': "http://www.nevprobusiness.com",
    'category': 'API',
    'version': '13.0.0',
    'depends': ['base','web','crm'],
    'data': [
        'view/http_api_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        ],
    'images':['static/description/banner-1.png'],
    # 'license': 'LGPL-3',
    'installable':True,
    'auto_install':False,
}
