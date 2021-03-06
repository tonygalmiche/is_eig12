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
        'base', 'mail', 'portal'
    ],
    'data' : [
        'data/sequence.xml',
        'data/is_ei_action_data.xml',
        'data/is_eig_action_data.xml',
        'data/type_evenement_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/is_access_ei_data.xml',
        'security/is_access_eig_data.xml',
        'wizard/is_motif_retour_view.xml',
        'wizard/is_motif_retour_view_eig.xml',
        'wizard/company_action_view.xml',
        'views/is_eig_view.xml',
        'views/is_ei_view.xml',
        'views/login_template_view.xml',
        'views/report_is_ei.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}

