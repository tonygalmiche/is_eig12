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
        'base', 'mail'
    ],
    'data' : [
        'data/sequence.xml',
        'data/is_ei_action_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/is_motif_retour_view.xml',
        'views/is_eig_view.xml',
        'views/is_ei_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}

