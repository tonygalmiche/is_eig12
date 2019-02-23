# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


AutoriteControle = [
    ('ars', 'ARS'),
    ('cd', 'CD'),
    ('ars_cd', 'ARS+CD'),
]


class is_departement(models.Model):
    _name = 'is.departement'
    _description = u"Département"
    _order = "name"

    name     = fields.Char(string='Nom du département' , required=True)
    code     = fields.Char(string='Code du département', required=True)
    mail_ars = fields.Char(string='Mail ARS')
    mail_cg  = fields.Char(string='Mail CD', help="Mail du Conseil Départemental")
    mail_ase = fields.Char(string='Mail ASE')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u"Le code du département doit être unique !"),
        ('name_uniq', 'unique(name)', u"Le nom du département doit être unique !"),
    ]


class is_etablissement(models.Model):
    _name = 'is.etablissement'
    _description = u"Établissement"
    _order = "name"

    name              = fields.Char(string='Nom', required=True)
    identifiant       = fields.Char(string='Identifiant', required=True)
    departement_id    = fields.Many2one('is.departement', string='Département', required=True)
    director_id       = fields.Many2one('res.users', 'Directeur', readonly=False, required=True, default=lambda self: self.env.uid)
    responsible_id    = fields.Many2one('res.users', 'Responsable', required=True)
    responsable_ids   = fields.Many2many('res.users', 'is_etablissement_responsables_rel', 'etablissement_id', 'user_id', string='Autres responsables')
    traiteur_ids      = fields.Many2many('res.users', 'is_etablissement_users_rel', 'user_id', 'etablissement_id', string='Traiteurs')
    membre_ids        = fields.Many2many('res.users', 'is_etablissement_membres_rel', 'etablissement_id', 'user_id', string='Membres')
    autorite_controle = fields.Selection(AutoriteControle, string='Autorité de Contrôle')
    adresse1          = fields.Char(string='Adresse', required=False)
    adresse2          = fields.Char(string='Adresse (suite)', required=False)
    cp                = fields.Char(string='CP', required=False)
    ville             = fields.Char(string='Ville', required=False)
    finess            = fields.Char(string='Finess', required=False)
    telephone         = fields.Char(string='Téléphone', required=False)
    fax               = fields.Char(string='Fax', required=False)

    _sql_constraints = [
        ('identifiant_uniq', 'unique(identifiant)', u"L'identifiant de l'établissement doit être unique !"),
    ]
