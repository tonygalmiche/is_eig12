# -*- coding: utf-8 -*-
{
    'name'     : 'Modules Odoo 12 pour OVE pour la gestion des EIG et des EI',
    'version'  : '0.1',
    'author'   : 'InfoSaône',
    'category' : 'InfoSaône',
    'description': """
Modules Odoo 12 pour OVE pour la gestion des EIG et des EI
===================================================
""",
    'maintainer' : 'InfoSaône',
    'website'    : 'http://www.infosaone.com',
    'depends'    : [
        'base',
    ],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/is_eig_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}

