# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
import uuid
import os
import codecs
from py3o.template import Template
import base64
from datetime import datetime, timedelta
import time
from pytz import timezone
import pytz


# SUPERUSER_ID = 2

AutoriteControle = [
    ('ars', 'ARS'),
    ('cd', 'CD'),
    ('ars_cd', 'ARS+CD'),
]

OuiNon=[
    ('oui', 'Oui'),
    ('non', 'Non'),
]

class is_departement(models.Model):
    _name = 'is.departement'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = u"Département"
    _order = "name"

    name     = fields.Char(string='Nom du département' , required=True)
    code     = fields.Char(string='Code du département', required=True)
    mail_ars = fields.Char(string='Mail ARS')
    mail_cg  = fields.Char(string='Mail CD', help="Mail du Conseil Départemental")
    mail_ase = fields.Char(string='Mail ASE')
    input_attach_ids = fields.Many2many('ir.attachment', string='Input File')
    trame_id         = fields.Many2one('is.trame', string=u'Modèle ODT Situation Exceptionnelle (SE)')

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


class is_type_evenement_mail(models.Model):
    _name = 'is.type.evenement.mail'
    _description = 'is.type.evenement.mail'

    autorite_controle = fields.Selection(AutoriteControle  , u'Autorité de Contrôle')
    mail_destination  = fields.Selection(AutoriteControle  , u'Mail de destination du département')
    type_evenement_id = fields.Many2one('is.type.evenement', u'Type d’événement')


class is_manip_fields(models.Model):
    _name = 'is.manip.fields'
    _description = u"Caractéristiques des champs"
    _order = "sequence"

    name            = fields.Char('Field Name', related='fields_id.field_description', store=True)
    sequence        = fields.Integer('Sequence')
    fields_id       = fields.Many2one('ir.model.fields', 'Champs', ondelete='cascade', required=True)
    field_visible   = fields.Boolean('Visible')
    field_required  = fields.Boolean('Obligatoire')
    type_event_id   = fields.Many2one('is.type.evenement', 'Type evenement')
    is_eig          = fields.Boolean('EIG', default=False)
    is_eig_auteur   = fields.Boolean('Auteur', default=False)
    is_eig_temoin   = fields.Boolean('Temoin', default=False)
    is_eig_victim   = fields.Boolean('Victim', default=False)
    is_eig_infos    = fields.Boolean('Infos', default=False)
    is_eig_infos2   = fields.Boolean('Infos2', default=False)
    is_eig_mesures  = fields.Boolean('Mesures', default=False)
    is_eig_elements = fields.Boolean(u'Eléments', default=False)
    is_eig_group    = fields.Boolean('Group', default=False)
    is_eig_entete   = fields.Boolean(u'Entête', default=False)
    is_eig_autre_personne = fields.Boolean(u'Autre(s) personne(s) concernée(s)', default=False)


class is_nature_evenement(models.Model):
    _name = 'is.nature.evenement'
    _description = u"Nature d'événement"

    name = fields.Char('Nature', required=True)
    code = fields.Char('Code')


# class is_type_risque(models.Model):
#     _name = 'is.type.risque'
#     _description = "Type de risque"
# 
#     name = fields.Char('Type', required=True)
# 
# 
# class is_nature_risque(models.Model):
#     _name = 'is.nature.risque'
#     _description = "Nature de risque"
# 
#     name = fields.Char('Nature', required=True)


class is_disposition_prise(models.Model):
    _name = 'is.disposition.prise'
    _description = 'disposition prises'

    name = fields.Char('Nom de dispostion', required=True)


class is_consequence(models.Model):
    _name = 'is.consequence'
    _description = u"Conséquences"

    name = fields.Char(u'Conséquence', required=True)


class is_destinataire(models.Model):
    _name = 'is.destinataire'
    _description = u"Destinataire"

    name = fields.Char('Nom' , required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_auteur(models.Model):
    _name = 'is.auteur'
    _description = u"Auteur"

    name = fields.Char('Nom' , required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_motif_retour_eig(models.Model):
    _name = 'is.motif.retour.eig'
    _description = u"Motifs de retour EIG"

    date        = fields.Datetime('Date/Heure')
    user_id     = fields.Many2one('res.users', 'Auteur')
    action      = fields.Char('Action')
    description = fields.Text('Motif')
    eig_id1     = fields.Many2one('is.eig', 'EIG', readonly=True)


class is_criteres_generaux(models.Model):
    _name = 'is.criteres.generaux'
    _description = 'Criteres Generaux'

    name = fields.Char('Nom' , required=True)
    code = fields.Char('Code')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_demande_intervention_secours(models.Model):
    _name = 'is.demande.intervention.secours'
    _description = 'Intervention Secours'

    name = fields.Char('Nom' , required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_consequence_personne_prise_en_charge(models.Model):
    _name = 'is.consequence.personne.prise.en.charge'
    _description = 'Consequence Charge'

    name = fields.Char('Nom' , required=True)
    code = fields.Char('Code')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_consequence_personnel(models.Model):
    _name = 'is.consequence.personnel'
    _description = 'Consequence Personnel'

    name = fields.Char('Nom' , required=True)
    code = fields.Char('Code')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_consequence_fonctionnement_stucture(models.Model):
    _name = 'is.consequence.fonctionnement.stucture'
    _description = 'Consequence Fonctionnement Stucture'

    name = fields.Char('Nom' , required=True)
    code = fields.Char('Code')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_qualite_autre(models.Model):
    _name = 'is.qualite.autre'
    _description = u"Qualité (autre)"

    name = fields.Char('Nom' , required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
    ]


class is_eig_auteur(models.Model):
    _name = 'is.eig.auteur'
    _description = 'Auteur'

    identifie                   = fields.Boolean(u'Identifié')
    related_vsb_identifie       = fields.Boolean(u'Champs related_vsb_identifie - Visibilité')
    related_rqr_identifie       = fields.Boolean(u'Champs related_rqr_identifie - Obligation')
    name                        = fields.Char('Nom')
    related_vsb_name            = fields.Boolean(u'Champs related_vsb_name - Visibilité')
    related_rqr_name            = fields.Boolean(u'Champs related_rqr_name - Obligation')
    prenom                      = fields.Char('Prénom')
    related_vsb_prenom          = fields.Boolean(u'Champs related_vsb_prenom - Visibilité')
    related_rqr_prenom          = fields.Boolean(u'Champs related_rqr_prenom - Obligation')
    birthdate                   = fields.Date('Date de naissance')
    related_vsb_birthdate       = fields.Boolean(u'Champs related_vsb_birthdate - Visibilité')
    related_rqr_birthdate       = fields.Boolean(u'Champs related_rqr_birthdate - Obligation')
    qualite_id                  = fields.Many2one('is.qualite', u'Qualité')
    related_vsb_qualite_id      = fields.Boolean(u'Champs related_vsb_qualite_id - Visibilité')
    related_rqr_qualite_id      = fields.Boolean(u'Champs related_rqr_qualite_id - Obligation')
    sexe_id                     = fields.Many2one('is.sexe', 'Sexe')
    related_vsb_sexe_id         = fields.Boolean(u'Champs related_vsb_sexe_id - Visibilité')
    related_rqr_sexe_id         = fields.Boolean(u'Champs related_rqr_sexe_id - Obligation')
    disposition_id              = fields.Many2one('is.disposition.prise', 'Disposition prises')
    related_vsb_disposition_id  = fields.Boolean(u'Champs related_vsb_disposition_id - Visibilité')
    related_rqr_disposition_id  = fields.Boolean(u'Champs related_rqr_disposition_id - Obligation')
    adresse                     = fields.Char('Adresse')
    related_vsb_adresse         = fields.Boolean(u'Champs related_vsb_adresse - Visibilité')
    related_rqr_adresse         = fields.Boolean(u'Champs related_rqr_adresse - Obligation')
    is_eig_id                   = fields.Many2one('is.eig', 'EIG')


class is_eig_temoin(models.Model):
    _name = 'is.eig.temoin'
    _description = u'Témoins'

    identifie                   = fields.Boolean(u'Identifié')
    related_vsb_identifie       = fields.Boolean(u'Champs related_vsb_identifie - Visibilité')
    related_rqr_identifie       = fields.Boolean(u'Champs related_rqr_identifie - Obligation')
    name                        = fields.Char('Nom')
    related_vsb_name            = fields.Boolean(u'Champs related_vsb_name - Visibilité')
    related_rqr_name            = fields.Boolean(u'Champs related_rqr_name - Obligation')
    prenom                      = fields.Char('Prénom')
    related_vsb_prenom          = fields.Boolean(u'Champs related_vsb_prenom - Visibilité')
    related_rqr_prenom          = fields.Boolean(u'Champs related_rqr_prenom - Obligation')
    sexe_id                     = fields.Many2one('is.sexe', 'Sexe')
    related_vsb_sexe_id         = fields.Boolean(u'Champs related_vsb_sexe_id - Visibilité')
    related_rqr_sexe_id         = fields.Boolean(u'Champs related_rqr_sexe_id - Obligation')
    address                     = fields.Char('Adresse')
    related_vsb_address         = fields.Boolean(u'Champs related_vsb_address - Visibilité')
    related_rqr_address         = fields.Boolean(u'Champs related_rqr_address - Obligation')
    birthdate                   = fields.Date('Date de naissance')
    related_vsb_birthdate       = fields.Boolean(u'Champs related_vsb_birthdate - Visibilité')
    related_rqr_birthdate       = fields.Boolean(u'Champs related_rqr_birthdate - Obligation')
    qualite_id                  = fields.Many2one('is.qualite', u'Qualité')
    related_vsb_qualite_id      = fields.Boolean(u'Champs related_vsb_qualite_id - Visibilité')
    related_rqr_qualite_id      = fields.Boolean(u'Champs related_rqr_qualite_id - Obligation')
    disposition_id              = fields.Many2one('is.disposition.prise', 'Disposition prises')
    related_vsb_disposition_id  = fields.Boolean(u'Champs related_vsb_disposition_id - Visibilité')
    related_rqr_disposition_id  = fields.Boolean(u'Champs related_rqr_disposition_id - Obligation')
    is_eig_id                   = fields.Many2one('is.eig', 'EIG')


class is_eig_victime(models.Model):
    _name = 'is.eig.victime'
    _description = 'Victime'

    identifie                  = fields.Boolean(u'Identifié')
    related_vsb_identifie      = fields.Boolean(u'Champs related_vsb_identifie - Visibilité')
    related_rqr_identifie      = fields.Boolean(u'Champs related_rqr_identifie - Obligation')
    name                       = fields.Char('Nom')
    related_vsb_name           = fields.Boolean(u'Champs related_vsb_name - Visibilité')
    related_rqr_name           = fields.Boolean(u'Champs related_rqr_name - Obligation')
    prenom                     = fields.Char(u'Prénom')
    related_vsb_prenom         = fields.Boolean(u'Champs related_vsb_prenom - Visibilité')
    related_rqr_prenom         = fields.Boolean(u'Champs related_rqr_prenom - Obligation')
    sexe_id                    = fields.Many2one('is.sexe', 'Sexe')
    related_vsb_sexe_id        = fields.Boolean(u'Champs related_vsb_sexe_id - Visibilité')
    related_rqr_sexe_id        = fields.Boolean(u'Champs related_rqr_sexe_id - Obligation')
    address                    = fields.Char('Adresse')
    related_vsb_address        = fields.Boolean(u'Champs related_vsb_address - Visibilité')
    related_rqr_address        = fields.Boolean(u'Champs related_rqr_address - Obligation')
    birthdate                  = fields.Date('Date de naissance')
    related_vsb_birthdate      = fields.Boolean(u'Champs related_vsb_birthdate - Visibilité')
    related_rqr_birthdate      = fields.Boolean(u'Champs related_rqr_birthdate - Obligation')
    ecole                      = fields.Char(u'École fréquentée')
    related_vsb_ecole          = fields.Boolean(u'Champs related_vsb_ecole - Visibilité')
    related_rqr_ecole          = fields.Boolean(u'Champs related_rqr_ecole - Obligation')
    qualite_id                 = fields.Many2one('is.qualite', u'Qualité')
    related_vsb_qualite_id     = fields.Boolean(u'Champs related_vsb_qualite_id - Visibilité')
    related_rqr_qualite_id     = fields.Boolean(u'Champs related_rqr_qualite_id - Obligation')
    disposition_id             = fields.Many2one('is.disposition.prise', 'Disposition prises')
    related_vsb_disposition_id = fields.Boolean(u'Champs related_vsb_disposition_id - Visibilité')
    related_rqr_disposition_id = fields.Boolean(u'Champs related_rqr_disposition_id - Obligation')
    auteur_victime             = fields.Selection([('auteur', 'Auteur'), ('victime', 'Victime')], "Auteur / Victime")
    related_vsb_auteur_victime = fields.Boolean(u'Champs related_vsb_auteur_victime - Visibilité')
    related_rqr_auteur_victime = fields.Boolean(u'Champs related_rqr_auteur_victime - Obligation')
    consequence_id             = fields.Many2one('is.consequence', u'Conséquences')
    related_vsb_consequence_id = fields.Boolean(u'Champs related_vsb_consequence_id - Visibilité')
    related_rqr_consequence_id = fields.Boolean(u'Champs related_rqr_consequence_id - Obligation')
    nom_pere                   = fields.Char(u'Nom Père')
    related_vsb_nom_pere       = fields.Boolean(u'Champs related_vsb_nom_pere - Visibilité')
    related_rqr_nom_pere       = fields.Boolean(u'Champs related_rqr_nom_pere - Obligation')
    prenom_pere                = fields.Char(u'Prénom Père')
    related_vsb_prenom_pere    = fields.Boolean(u'Champs related_vsb_prenom_pere - Visibilité')
    related_rqr_prenom_pere    = fields.Boolean(u'Champs related_rqr_prenom_pere - Obligation')
    address_pere               = fields.Char(u'Adresse Père')
    related_vsb_address_pere   = fields.Boolean(u'Champs related_vsb_address_pere - Visibilité')
    related_rqr_address_pere   = fields.Boolean(u'Champs related_rqr_address_pere - Obligation')
    nom_mere                   = fields.Char(u'Nom Mère')
    related_vsb_nom_mere       = fields.Boolean(u'Champs related_vsb_nom_mere - Visibilité')
    related_rqr_nom_mere       = fields.Boolean(u'Champs related_rqr_nom_mere - Obligation')
    prenom_mere                = fields.Char(u'Prénom Mère')
    related_vsb_prenom_mere    = fields.Boolean(u'Champs related_vsb_prenom_mere - Visibilité')
    related_rqr_prenom_mere    = fields.Boolean(u'Champs related_rqr_prenom_mere - Obligation')
    address_mere               = fields.Char(u'Adresse Mère')
    related_vsb_address_mere   = fields.Boolean(u'Champs related_vsb_address_mere - Visibilité')
    related_rqr_address_mere   = fields.Boolean(u'Champs related_rqr_address_mere - Obligation')
    tuteur_nom                 = fields.Char('Nom')
    related_vsb_tuteur_nom     = fields.Boolean(u'Champs related_vsb_tuteur_nom - Visibilité')
    related_rqr_tuteur_nom     = fields.Boolean(u'Champs related_rqr_tuteur_nom - Obligation')
    tuteur_prenom              = fields.Char(u"Prénom")
    related_vsb_tuteur_prenom  = fields.Boolean(u'Champs related_vsb_tuteur_prenom - Visibilité')
    related_rqr_tuteur_prenom  = fields.Boolean(u'Champs related_rqr_tuteur_prenom - Obligation')
    tuteur_adresse             = fields.Char('Adresse')
    related_vsb_tuteur_adresse = fields.Boolean(u'Champs related_vsb_tuteur_adresse - Visibilité')
    related_rqr_tuteur_adresse = fields.Boolean(u'Champs related_rqr_tuteur_adresse - Obligation')
    is_eig_id                  = fields.Many2one('is.eig', 'EIG')


class is_infos_communication(models.Model):
    _name = 'is.infos.communication'
    _description = "Information communication"

    date                       = fields.Datetime('Date heure')
    related_vsb_date           = fields.Boolean(u'Champs related_vsb_date - Visibilité')
    related_rqr_date           = fields.Boolean(u'Champs related_rqr_date - Obligation')
    user_id                    = fields.Many2one('is.destinataire', 'Destinataire', help=u"Indiquer qui a été saisi par une information concernant l'EIG (exemple : la presse a été saisie par un personnel de la structure)")
    related_vsb_user_id        = fields.Boolean(u'Champs related_vsb_user_id - Visibilité')
    related_rqr_user_id        = fields.Boolean(u'Champs related_rqr_user_id - Obligation')
    responsible_id             = fields.Many2one('is.auteur', 'Auteur', help=u"Indiquer qui est à l'origine de cette information (par exemple : la famille d'un usager a informé le procureur)")
    related_vsb_responsible_id = fields.Boolean(u'Champs related_vsb_responsible_id - Visibilité')
    related_rqr_responsible_id = fields.Boolean(u'Champs related_rqr_responsible_id - Obligation')
    support                    = fields.Char('Support', help=u"Permet d'indiquer le support de communication (courrier, presse écrite, internet, journal interne)")
    related_vsb_support        = fields.Boolean(u'Champs related_vsb_support - Visibilité')
    related_rqr_support        = fields.Boolean(u'Champs related_rqr_support - Obligation')
    info_cible                 = fields.Char('Information cible', help=u"Indiquer la nature des événements communiqués")
    related_vsb_info_cible     = fields.Boolean(u'Champs related_vsb_info_cible - Visibilité')
    related_rqr_info_cible     = fields.Boolean(u'Champs related_rqr_info_cible - Obligation')
    impact                     = fields.Boolean(u'Impact médiatique', help=u"A cocher si l'événement est susceptible d'avoir un impact médiatique")
    related_vsb_impact         = fields.Boolean(u'Champs related_vsb_impact - Visibilité')
    related_rqr_impact         = fields.Boolean(u'Champs related_rqr_impact - Obligation')
    is_eig_id                  = fields.Many2one('is.eig', 'EIG')


class is_eig_autre_personne(models.Model):
    _name = 'is.eig.autre.personne'
    _description = u"Autre(s) personne(s) concernée(s) par l’IP"

    identifie                  = fields.Boolean(u"Identifié")
    related_vsb_identifie      = fields.Boolean(u'Champs related_vsb_identifie - Visibilité')
    related_rqr_identifie      = fields.Boolean(u'Champs related_rqr_identifie - Obligation')
    nom                        = fields.Char('Nom')
    related_vsb_nom            = fields.Boolean(u'Champs related_vsb_nom - Visibilité')
    related_rqr_nom            = fields.Boolean(u'Champs related_rqr_nom - Obligation')
    prenom                     = fields.Char(u'Prénom')
    related_vsb_prenom         = fields.Boolean(u'Champs related_vsb_prenom - Visibilité')
    related_rqr_prenom         = fields.Boolean(u'Champs related_rqr_prenom - Obligation')
    qualite_id                 = fields.Many2one('is.qualite.autre', u'Qualité')
    related_vsb_qualite_id     = fields.Boolean(u'Champs related_vsb_qualite_id - Visibilité')
    related_rqr_qualite_id     = fields.Boolean(u'Champs related_rqr_qualite_id - Obligation')
    consequence_id             = fields.Many2one('is.consequence', u'Conséquences')
    related_vsb_consequence_id = fields.Boolean(u'Champs related_vsb_consequence_id - Visibilité')
    related_rqr_consequence_id = fields.Boolean(u'Champs related_rqr_consequence_id - Obligation')
    disposition_id             = fields.Many2one('is.disposition.prise', 'Disposition prises')
    related_vsb_disposition_id = fields.Boolean(u'Champs related_vsb_disposition_id - Visibilité')
    related_rqr_disposition_id = fields.Boolean(u'Champs related_rqr_disposition_id - Obligation')
    auteur_victime             = fields.Selection([('auteur', 'Auteur'), ('victime', 'Victime')], "Auteur / Victime")
    related_vsb_auteur_victime = fields.Boolean(u'Champs related_vsb_auteur_victime - Visibilité')
    related_rqr_auteur_victime = fields.Boolean(u'Champs related_rqr_auteur_victime - Obligation')
    is_eig_id                   = fields.Many2one('is.eig', 'EIG')


class is_eig(models.Model):
    _name = 'is.eig'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = u"Événements Indésirables Graves"
    _order = "name desc"

    @api.depends('state','etablissement_id','redacteur_id')
    def _btn_rediger_eig(self):
        for obj in self:
            r = False
            if obj.state == "draft":
                if self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig.group_is_traiteur') \
                    or self._uid == obj.etablissement_id.director_id.id \
                    or self._uid == obj.etablissement_id.responsible_id.id \
                    or self._uid == obj.redacteur_id.id:
                    r = True
            obj.btn_rediger_eig = r

    @api.depends('state', 'etablissement_id')
    def _btn_valider_eig(self):
        for obj in self:
            r=False
            if obj.state=="redige":
                if  self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_traiteur') \
                    or self._uid == obj.etablissement_id.director_id.id:
                    r=True
            obj.btn_valider_eig = r

    @api.depends('state', 'redacteur_id', 'etablissement_id')
    def _btn_retour_redaction(self):
        for obj in self:
            r = False
            if obj.state == "redige":
                if  self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_traiteur') \
                    or self._uid == obj.redacteur_id.id \
                    or self._uid == obj.etablissement_id.director_id.id:
                    r = True
            obj.btn_retour_redaction = r

    @api.depends('state')
    def _btn_completer_eig(self):
        for obj in self:
            r = False
            if obj.state == "valide":
                if self._uid == SUPERUSER_ID or self.env.user.has_group('is_eig12.group_is_traiteur'):
                    r = True
            obj.btn_completer_eig = r

    @api.depends('state', 'etablissement_id')
    def _btn_completer_vers_valider_eig(self):
        for obj in self:
            r = False
            if obj.state == "complet":
                if  self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_traiteur') \
                    or self._uid == obj.etablissement_id.director_id.id:
                    r = True
            obj.btn_completer_vers_valider_eig = r

    @api.onchange('etablissement_id')
    def onchange_etablissement_id(self):
        if self.etablissement_id:
            self.valideur_id = self.etablissement_id.director_id.id or False

    @api.onchange('type_event_id')
    def onchange_type_event_id(self):
        if self.type_event_id:
            vals = {}
            vals.update({
                'related_onglet_faits':  False,
                'related_onglet_auteurs':  False,
                'related_onglet_temoins':  False,
                'related_onglet_victimes':  False,
                'related_onglet_mesures':  False,
                'related_onglet_infos':  False,
                'related_onglet_element_complementaire':  False,
                'related_group_motif_retour':  False,
                'related_vsb_si_autre_presumees':  False,
                'related_rqr_si_autre_presumees':  False,
                'related_vsb_si_autre_personees':  False,
                'related_rqr_si_autre_personees':  False,
                'related_vsb_en_case_suspectees':  False,
                'related_rqr_en_case_suspectees':  False,
                'related_vsb_en_case_lesquelles':  False,
                'related_rqr_en_case_lesquelles':  False,
                'related_vsb_nature_precision':  False,
                'related_rqr_nature_precision':  False,
                'related_vsb_start_date':  False,
                'related_rqr_start_date':  False,
                'related_vsb_consequence_personne_prise_en_charge_ids': False,
                'related_rqr_consequence_personne_prise_en_charge_ids': False,
                'related_vsb_consequence_personnel_ids': False,
                'related_rqr_consequence_personnel_ids': False,
                'related_vsb_consequence_fonctionnement_stucture_ids': False,
                'related_rqr_consequence_fonctionnement_stucture_ids': False,
                'related_vsb_si_autre_pour_personnel': False,
                'related_rqr_si_autre_pour_personnel': False,
                'related_vsb_si_autre_pour_organisation': False,
                'related_rqr_si_autre_pour_organisation': False,
                'related_vsb_nb_jours_interuption_travail': False,
                'related_rqr_nb_jours_interuption_travail': False,
                'related_vsb_fait_deja_produit': False,
                'related_rqr_fait_deja_produit': False,
                'related_vsb_eig_deja_declare': False,
                'related_rqr_eig_deja_declare': False,
                'related_vsb_risque_reproductibilite': False,
                'related_rqr_risque_reproductibilite': False,
                'related_vsb_risque_extension': False,
                'related_rqr_risque_extension': False,
                'related_vsb_risque_contentieux': False,
                'related_rqr_risque_contentieux': False,
                'related_vsb_evenement_semble_maitrise': False,
                'related_rqr_evenement_semble_maitrise': False,
                'related_vsb_si_non_maitrise_precisez': False,
                'related_rqr_si_non_maitrise_precisez': False,
                'related_vsb_date_heure_constatation_faits': False,
                'related_rqr_date_heure_constatation_faits': False,
                'related_vsb_end_date':  False,
                'related_vsb_description_faits':  False,
                'related_rqr_description_faits':  False,
                'related_vsb_criteres_generaux_ids': False,
                'related_rqr_criteres_generaux_ids': False,
                'related_vsb_risque_reproductivite':  False,
                'related_rqr_risque_reproductivite':  False,
                'related_vsb_solution_prise_en_charge':  False,
                'related_rqr_solution_prise_en_charge':  False,
                'related_vsb_demande_intervention_secours_ids': False,
                'related_rqr_demande_intervention_secours_ids': False,
                'related_vsb_risque_extension':  False,
                'related_rqr_risque_extension':  False,
                'related_vsb_risque_contentieux':  False,
                'related_rqr_risque_contentieux':  False,
                'related_vsb_evenement_maitrise':  False,
                'related_rqr_evenement_maitrise':  False,
                'related_vsb_si_non_maitrise':  False,
                'related_rqr_si_non_maitrise':  False,
                'related_vsb_lieu_faits':  False,
                'related_rqr_lieu_faits':  False,
                'related_vsb_element_faits':  False,
                'related_rqr_element_faits':  False,
                'related_vsb_cause_faits':  False,
                'related_rqr_cause_faits':  False,
                'related_vsb_reunion_debriefing':  False,
                'related_rqr_reunion_debriefing':  False,
                'related_vsb_si_reunion_debriefing':  False,
                'related_rqr_si_reunion_debriefing':  False,
                'related_vsb_causes_profondes':  False,
                'related_rqr_causes_profondes':  False,
                'related_vsb_premiere_cause_identifiee':  False,
                'related_rqr_premiere_cause_identifiee':  False,
                'related_vsb_evolution_previsible':  False,
                'related_rqr_evolution_previsible':  False,
                'related_vsb_mesure_pour_proteger_accompagner':  False,
                'related_rqr_mesure_pour_proteger_accompagner':  False,
                'related_vsb_mesure_pour_assurer_continuite':  False,
                'related_rqr_mesure_pour_assurer_continuite':  False,
                'related_vsb_mesure_egard_autres_personnes':  False,
                'related_rqr_mesure_egard_autres_personnes':  False,
                'related_vsb_mesure_structure':  False,
                'related_rqr_mesure_structure':  False,
                'related_vsb_si_causes_profondes':  False,
                'related_rqr_si_causes_profondes':  False,
                'related_vsb_enseignements_a_tirer':  False,
                'related_rqr_enseignements_a_tirer':  False,
                'related_vsb_si_enseignements_a_tirer':  False,
                'related_rqr_si_enseignements_a_tirer':  False,
                'related_vsb_mesure_organisation':  False,
                'related_rqr_mesure_organisation':  False,
                'related_vsb_mesure_personnel':  False,
                'related_rqr_mesure_personnel':  False,
                'related_vsb_mesure_usagers':  False,
                'related_rqr_mesure_usagers': False,
                'related_vsb_mesure_autres': False,
                'related_rqr_mesure_autres': False,
                'related_vsb_note': False,
                'related_rqr_note': False,
                'related_vsb_attachment_ids': False,
                'related_rqr_attachment_ids': False,
                'related_vsb_intervention_police':  False,
                'related_rqr_intervention_police':  False,
                'related_vsb_depot_plainte':  False,
                'related_rqr_depot_plainte':  False,
                'related_vsb_enquete_police':  False,
                'related_rqr_enquete_police':  False,
                'related_vsb_depot_plainte_famille':  False,
                'related_rqr_depot_plainte_famille':  False,
                'related_vsb_communication_prevue':  False,
                'related_rqr_communication_prevue':  False,
                'related_vsb_communication_prevue_oui':  False,
                'related_rqr_communication_prevue_oui':  False,
                'related_aut_vsb_identifie': False,
                'related_aut_rqr_identifie': False,
                'related_aut_vsb_name': False,
                'related_aut_rqr_name': False,
                'related_aut_vsb_prenom': False,
                'related_aut_rqr_prenom': False,
                'related_aut_vsb_birthdate': False,
                'related_aut_rqr_birthdate': False,
                'related_aut_vsb_qualite_id': False,
                'related_aut_rqr_qualite_id': False,
                'related_aut_vsb_sexe_id': False,
                'related_aut_rqr_sexe_id': False,
                'related_aut_vsb_disposition_id': False,
                'related_aut_rqr_disposition_id': False,
                'related_aut_vsb_adresse': False,
                'related_aut_rqr_adresse': False,
                'related_tem_vsb_identifie': False,
                'related_tem_rqr_identifie': False,
                'related_tem_vsb_name': False,
                'related_tem_rqr_name': False,
                'related_tem_vsb_prenom': False,
                'related_tem_rqr_prenom': False,
                'related_tem_vsb_sexe_id': False,
                'related_tem_rqr_sexe_id': False,
                'related_tem_vsb_address': False,
                'related_tem_rqr_address': False,
                'related_tem_vsb_birthdate': False,
                'related_tem_rqr_birthdate': False,
                'related_tem_vsb_qualite_id': False,
                'related_tem_rqr_qualite_id': False,
                'related_tem_vsb_disposition_id': False,
                'related_tem_rqr_disposition_id': False,
                'related_vict_vsb_identifie': False,
                'related_vict_rqr_identifie': False,
                'related_vict_vsb_name': False,
                'related_vict_rqr_name': False,
                'related_vict_vsb_prenom': False,
                'related_vict_rqr_prenom': False,
                'related_vict_vsb_sexe_id': False,
                'related_vict_rqr_sexe_id': False,
                'related_vict_vsb_address': False,
                'related_vict_rqr_address': False,
                'related_vict_vsb_ecole': False,
                'related_vict_rqr_ecole': False,
                'related_vict_vsb_birthdate': False,
                'related_vict_rqr_birthdate': False,
                'related_vict_vsb_qualite_id': False,
                'related_vict_rqr_qualite_id': False,
                'related_vict_vsb_disposition_id': False,
                'related_vict_rqr_disposition_id': False,
                'related_vict_vsb_consequence_id': False,
                'related_vict_rqr_consequence_id': False,
                'related_vict_vsb_nom_pere': False,
                'related_vict_rqr_nom_pere': False,
                'related_vict_vsb_prenom_pere': False,
                'related_vict_rqr_prenom_pere': False,
                'related_vict_vsb_address_pere': False,
                'related_vict_rqr_address_pere': False,
                'related_vict_vsb_nom_mere': False,
                'related_vict_rqr_nom_mere': False,
                'related_vict_vsb_prenom_mere': False,
                'related_vict_rqr_prenom_mere': False,
                'related_vict_vsb_address_mere': False,
                'related_vict_rqr_address_mere': False,
                'related_vict_vsb_auteur_victime': False,
                'related_vict_rqr_auteur_victime': False,
                'related_vict_vsb_tuteur_nom': False,
                'related_vict_rqr_tuteur_nom': False,
                'related_vict_vsb_tuteur_prenom': False,
                'related_vict_rqr_tuteur_prenom': False,
                'related_vict_vsb_tuteur_adresse': False,
                'related_vict_rqr_tuteur_adresse': False,
                'related_inf_vsb_date': False,
                'related_inf_rqr_date': False,
                'related_inf_vsb_user_id': False,
                'related_inf_rqr_user_id': False,
                'related_inf_vsb_responsible_id': False,
                'related_inf_rqr_responsible_id': False,
                'related_inf_vsb_support': False,
                'related_inf_rqr_support': False,
                'related_inf_vsb_info_cible': False,
                'related_inf_rqr_info_cible': False,
                'related_inf_vsb_impact': False,
                'related_inf_rqr_impact': False,
                'related_vsb_signalement_autorites': False,
                'related_rqr_signalement_autorites': False,
                'related_autre_personne_vsb_identifie': False,
                'related_autre_personne_rqr_identifie': False,
                'related_autre_personne_vsb_nom': False,
                'related_autre_personne_rqr_nom': False,
                'related_autre_personne_vsb_prenom': False,
                'related_autre_personne_rqr_prenom': False,
                'related_autre_personne_vsb_qualite_id': False,
                'related_autre_personne_rqr_qualite_id': False,
                'related_autre_personne_vsb_consequence_id': False,
                'related_autre_personne_rqr_consequence_id': False,
                'related_autre_personne_vsb_disposition_id': False,
                'related_autre_personne_rqr_disposition_id': False,
                'related_autre_personne_vsb_auteur_victime': False,
                'related_autre_personne_rqr_auteur_victime': False,
            })
            vals.update({
                'related_onglet_faits': self.type_event_id.onglet_faits,
                'related_onglet_auteurs': self.type_event_id.onglet_auteurs,
                'related_onglet_temoins': self.type_event_id.onglet_temoins,
                'related_onglet_victimes': self.type_event_id.onglet_victimes,
                'related_onglet_mesures': self.type_event_id.onglet_mesures,
                'related_onglet_infos': self.type_event_id.onglet_infos,
                'related_onglet_element_complementaire': self.type_event_id.onglet_element_complementaire,
            })
            for item in self.type_event_id.fields_eig_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_auteur_id:
                if item.field_visible :
                    field = str('related_aut_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_aut_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_temoin_id:
                if item.field_visible :
                    field = str('related_tem_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_tem_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_victim_id:
                if item.field_visible :
                    field = str('related_vict_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_vict_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_info_id:
                if item.field_visible :
                    field = str('related_inf_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_inf_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_info2_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_mesures_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_elements_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_group_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_entete_id:
                if item.field_visible :
                    field = str('related_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            for item in self.type_event_id.fields_autre_personne_id:
                if item.field_visible :
                    field = str('related_autre_personne_vsb_'+item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_autre_personne_rqr_'+item.fields_id.name)
                        vals.update({field: True})
            return {'value': vals}

    @api.multi
    def get_signup_url(self):
        url = False
        for data in self:
            url = "https://eig.fondation-ove.fr/web#id=" + str(data.id) + "&view_type=form&model=is.eig"
        return url

    @api.multi
    def action_rediger_eig(self):
        for data in self:
            data.write({'state': 'redige'})
            template = self.env.ref('is_eig12.email_template_redaction_vers_redige', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)

    @api.multi
    def key2val(self, key, liste):
        for l in liste:
            if key == l[0]:
                return l[1]

    @api.multi
    def get_mail(self, doc, key):
        mail = False
        if key == "ars":
            mail = doc.etablissement_id.departement_id.mail_ars
        if key == "cd":
            mail = doc.etablissement_id.departement_id.mail_cg
        if not mail:
            val = self.key2val(key, AutoriteControle)
            raise UserError(_("Mail %s non trouvé pour le département de cet établissement !") % str(val))
        return mail

    @api.multi
    def get_traiteurs(self):
        obj = self.env['ir.model.data']
        data_ids = obj.search([('module', '=', 'is_eig'), ('name', '=', 'group_is_traiteur')])
        mail = ""
        resid = 0
        for data in data_ids:
            for o in data.read(['res_id','name']):
                resid = o["res_id"]
        if resid:
            ctx = self.env['res.groups']
            for g in ctx.browse(resid):
                l = []
                for u in g.users:
                    l.append(u.email)
                mail = ",".join(l)
        return mail

    @api.multi
    def action_valider_eig(self):
        for doc in self:
#             if not doc.type_risq_id:
#                 raise UserError(_("Champ 'Type de risque' obligatoire !"))
            autorite_controle = doc.etablissement_id.autorite_controle
            if not autorite_controle:
                raise UserError(_("Autorité de contôle non renseigné pour cet établissement !"))
            mail_destination_ids = doc.type_event_id.mail_destination_ids
            if not mail_destination_ids:
                raise UserError(_("Destinataires des mails (ARS ou CD) non renseignés pour ce type d'évènement !"))
            test = False
            mail = []
            for lig in doc.type_event_id.mail_destination_ids:
                if lig.autorite_controle == autorite_controle:
                    if not lig.mail_destination:
                        val = self.key2val(autorite_controle, AutoriteControle)
                        raise UserError(_("Mail de destination non renseigné pour ce type d'évènement et pour l'autorité de contrôle %s !") % str(val))
                    if lig.mail_destination == "ars" or lig.mail_destination == "ars_cd":
                        mail.append(self.get_mail(doc, "ars"))
                    if lig.mail_destination == "cd" or lig.mail_destination == "ars_cd":
                        mail.append(self.get_mail(doc, "cd"))
                    test = True
                    break
            if not test:
                val = self.key2val(autorite_controle, AutoriteControle)
                raise UserError(_("Autorité de contrôle de l'établissement ( %s ) non trouvée pour ce type d'évènement !") % str(val))
            mail_ars_cd = ",".join(mail)
            # Enregistrement de la date de validation car celle-ci est utilisée dans le modèle
            vals = {
                'date_validation': fields.datetime.now(),
            }
            doc.write(vals)
            
#             # Generation du PDF
#             self.generation_pdf(cr, uid, ids)
            
            # Mail au traiteur
            template = self.env.ref('is_eig12.email_template_redige_vers_valide_traiteur', False)
            if template:
                template.send_mail(doc.id, force_send=True, raise_exception=True)
            # Mais ARS avec pièce jointe
            template_id = self.env.ref('is_eig12.email_template_redige_vers_valide_ars', False)
            if template_id:
                obj = self.env['ir.attachment']
                # Recherche des fichiers PDF attachés à l'EIG
                attachment_ids = obj.search([('res_model', '=', 'is.eig'),('res_id', '=', doc.id),('name','like','%pdf'),('name','not ilike','%signalement%')])
                #print "Pieces jointes à envoyer par mail", attachment_ids
                #Enregistrement des destinataires du mail
                template_id.email_to = mail_ars_cd
                # Ajout des pieces jointes de l'onglet 'Elements complémentaire'
                if doc.attachment_ids:
                    for x in doc.attachment_ids:
                        attachment_ids.append(x.id)
                #Ajout des pièces jointes au modèle
                template_id.write({'attachment_ids': [(6, 0, attachment_ids)]})
                # Envoi du mail (avec les pièces jointes)
                template_id.send_mail(doc.id, force_send=True, raise_exception=True)
                # Suppression des pièces jointes du modèle
                template_id.write({'attachment_ids': [(6, 0, [])]})
            doc.write({
                'state': 'valide',
            })

    @api.multi
    def action_non_declarable(self):
        for obj in self:
            obj.write({'state': 'non_declarable'})
            vals = {
                'etablissement_id'   : obj.etablissement_id.id,
                'type_event_id'      : 15,
                'destinataire_id'    : 4,
                'nature_event_id'    : 46,
                'date_faits'         : obj.start_date,
                'mesure_amelioration': ' ',
                'mesure_immediat'    : ' ',
                'mesure_autre'       : ' ',
                'consequence_faits'  : ' ',
                'lieu_faits'         : ' ',
                'description_faits'  : ' ',
            }
            ei_id = self.env['is.ei'].create(vals)
            return {
                'name': "Incident",
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'is.ei',
                'type': 'ir.actions.act_window',
                'res_id': ei_id,
                'domain': '[]',
            }

    @api.multi
    def action_terminer_eig(self):
        for data in self:
            data.write({'state': 'done'})

    @api.multi
    def action_completer_vers_valider_eig(self):
        for data in self:
            data.write({'state': 'valide', 'date_validation': fields.Datetime.now()})
            template = self.env.ref('is_eig12.email_template_a_completer_vers_valide', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('eig.number') or ''
        if 'etablissement_id' in vals and vals['etablissement_id']:
            etablissement_obj = self.env['is.etablissement']
            etablissement = etablissement_obj.browse(vals['etablissement_id'])
            vals.update({'valideur_id': etablissement.director_id and etablissement.director_id.id or False})
        return super(is_eig, self).create(vals)

    @api.multi
    def generation_odt(self):
        for data in self:
            data.generation_document("ODT")
        return True

    @api.multi
    def nature(self, val):
        r="□"
        for data in self:
            nature_ids = self.env['is.nature.evenement'].search([('id','in',data.nature_event_id.ids), ('code','=',str(val))])
            for ne in nature_ids:
                if ne.code == str(val):
                    return "☑"
                else:
                    r="□"
        return r

    @api.multi
    def consequence(self, val):
        r="□"
        for data in self:
            data_ids = self.env['is.consequence.fonctionnement.stucture'].search([('id','in',data.consequence_fonctionnement_stucture_ids.ids), ('code','=',str(val))])
            for ne in data_ids:
                if ne.code == str(val):
                    return "☑"
                else:
                    r="□"
        return r

    @api.multi
    def criteres(self, val):
        r="□"
        for data in self:
            data_ids = self.env['is.criteres.generaux'].search([('id','in',data.criteres_generaux_ids.ids), ('code','=',str(val))])
            for ne in data_ids:
                if ne.code == str(val):
                    return "☑"
                else:
                    r="□"
        return r

    @api.multi
    def prise(self, val):
        r="□"
        for data in self:
            data_ids = self.env['is.consequence.personne.prise.en.charge'].search([('id','in',data.consequence_personne_prise_en_charge_ids.ids), ('code','=',str(val))])
            for ne in data_ids:
                if ne.code == str(val):
                    return "☑"
                else:
                    r="□"
        return r

    @api.multi
    def personnel(self, val):
        r="□"
        for data in self:
            data_ids = self.env['is.consequence.personnel'].search([('id','in',data.consequence_personnel_ids.ids), ('code','=',str(val))])
            for ne in data_ids:
                if ne.code == str(val):
                    return "☑"
                else:
                    r="□"
        return r

    @api.multi
    def f1(self, val):
        val=str(val)
        if (val=="1" or val=="t" or val=="True" or val=="true"):
            r="☑"
        else:
            r="□"
        return r

    @api.multi
    def f2(self,val):
        if (self.nature_event_id.id == val):
            r="☑"
        else:
            r="□"
        return r

    @api.multi
    def f3(self,val):
        r=0
        for lig in self.infos_ids:
            if lig.user_id.id == val:
                r=1
        return r

    @api.multi
    def f4(self,val):
        for lig in self.infos_ids:
            if(lig.user_id.id == val):
                #print "=> date=",lig.date
                return str(lig.date)
        return False

    @api.multi
    def f5(self,val):
        for lig in self.infos_ids:
            if(lig.user_id.id == val):
                return lig.support or ''
        return ""

    @api.multi
    def attach_length(self,val):
        return len(val)

    @api.multi
    def h(self, date):
        if date==False:
            return ""
        utc = pytz.utc
        utc_dt  = datetime.strptime(str(date)[:19], '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)
        europe = timezone('Europe/Paris')
        loc_dt = utc_dt.astimezone(europe)
        return loc_dt.strftime('%d/%m/%Y %H:%M')

    @api.multi
    def d(self, date):
        if date==False:
            return ""
        utc = pytz.utc
        utc_dt  = datetime.strptime(str(date)[:19], '%Y-%m-%d').replace(tzinfo=utc)
        europe = timezone('Europe/Paris')
        loc_dt = utc_dt.astimezone(europe)
        return loc_dt.strftime('%d/%m/%Y')

    @api.multi
    def t(self, txt):
        if not txt:
            return ""
        return txt

    @api.multi
    def t1(self, txt):
        if not txt:
            return ""
        return txt.name

    @api.multi
    def generation_document_par_nom(self, type="ODT", v=[], contenu="", nom=""):
        for data in self:
            name=nom[:-4]
            name=name+".odt"
            path = "/tmp/py3o_template.odt"
            dest = "/tmp/"+name
            f = open(path,'wb')
            f.write(base64.b64decode(contenu))
#             f.close()
            t = Template(path, dest, escape_false=' ')
            items = list()
            item1 = Item()
            items.append(item1)
            o = Item()
            data1 = dict(items=items, document=o,test01="toto",o=data)
            t.render(data1)
            r = base64.b64encode(open(dest,'rb').read())
            if type=="PDF":
                cde="soffice --headless   --convert-to pdf:writer_pdf_Export "+dest+" --outdir /tmp"
                os.system(cde)
                r = base64.b64encode(open(dest,'rb').read())
            name1=nom[:-4]
            if type=="PDF":
                name=name1+".pdf"
                read_pdf = "/tmp/"+name
                r = base64.b64encode(open(read_pdf,'rb').read())
            else:
                name=name1+".odt"
            vals = {
                'name':        name,
                'datas_fname': name,
                'type':        'binary',
                'res_model':   'is.eig',
                'res_id':      data.id,
                'datas':       r,
            }
            obj = self.env['ir.attachment']
            ids = obj.search([('res_model','=', 'is.eig'),('res_id','=', data.id),('name','=',name)])
            if ids:
                ids[0].write(vals)
                vals1={
                    'attachment_ids': [(4,ids[0].id)],
                }
                print ("Modification ir.attachment id="+str(ids[0]),ids)
            else:
                id = obj.create(vals)
                print ("Création ir.attachment id="+str(id))
                vals1={
                    'attachment_ids': [(4, id.id)],
                }
            data.with_context(stop_write_recursion=1).write(vals1)

    def generation_pdf(self):
        self.generation_document("PDF")
        return True

    @api.multi
    def generation_document(self, type="ODT"):
        v = {}
        for rec in self:
            if rec.type_event_id.code == "SE":
                v["o"] = rec
                if rec.signalement_autorites:
                    company_obj = self.env['res.company']
                    company_ids = company_obj.search([('id', '=', 1)])
                    for company in company_ids:
                        for attachment in company.attachment_ids:
                            for l in attachment.read(['name','datas']):
                                rec.generation_document_par_nom(type, v, l["datas"], l["name"])
    #             ** Recherche des modeles associés au département *****************
                for attch in rec.etablissement_id.departement_id.trame_id.attachment_ids:
                    for l in attch.read(['name','datas']):
                        rec.generation_document_par_nom(type, v, l["datas"], l["name"])
        return True



    btn_rediger_eig                       = fields.Boolean('Rediger EIG', compute='_btn_rediger_eig')
    btn_valider_eig                       = fields.Boolean('Valider EIG', compute='_btn_valider_eig')
    btn_retour_redaction                  = fields.Boolean('Ertour Redaction', compute='_btn_retour_redaction')
    btn_completer_eig                     = fields.Boolean('Completer EIG', compute='_btn_completer_eig')
    btn_completer_vers_valider_eig        = fields.Boolean('Completer Vers Valider', compute='_btn_completer_vers_valider_eig')
    state = fields.Selection([
        ('draft', u'Rédaction'),
        ('redige', u'Rédigé'),
        ('valide', u'Validé'),
        ('complet', u'A compléter'),
        ('done', u'Traité'),
        ('non_declarable', u'Non déclarable'),
    ], 'Statut', readonly=True, default='draft')
    name = fields.Char(u'N°')
    etablissement_id                      = fields.Many2one('is.etablissement', u'Établissement', required=True, help=u'ESMS concerné par un EIG. Ce choix détermine le formulaire départemental qui sera généré et envoyé aux autorités de tutelles.')
    redacteur_id                          = fields.Many2one('res.users', u'Rédacteur', readonly=True, default=lambda self: self.env.uid)
    valideur_id                           = fields.Many2one('res.users', 'Valideur', readonly=True)
    date_validation                       = fields.Datetime(u'Date de validation')
    type_event_id                         = fields.Many2one('is.type.evenement', u"Type d'événement", required=True, help=u"Grandes catégories d'EIG. Pour tout EIG concernant un ou plusieurs mineurs relevant de l'ASE, il est nécessaire de sélectionner « Mineur relevant de l'ASE ». Ce choix détermine également le formulaire départemental qui sera généré et envoyé aux autorités de tutelles.")
    event_description                     = fields.Text('Description', related='type_event_id.description')
    event_information_speciale            = fields.Text(u'Information spéciale', related='type_event_id.information_speciale')
    nature_event_id                       = fields.Many2many('is.nature.evenement', string=u"Nature d'événement", required=True, help=u"Préciser le type d'événement à déclarer.")
    type_nature_event_ids                 = fields.Many2many(related="type_event_id.is_nature_ids")
    related_vsb_si_autre_presumees        = fields.Boolean(u'Champs related_vsb_si_autre_presumees - Visibilité')
    related_rqr_si_autre_presumees        = fields.Boolean(u'Champs related_rqr_si_autre_presumees - Obligation')
    si_autre_presumees                    = fields.Char(u'Si « Autre (évènements relatifs aux victimes présumées) », à préciser (en 1 ou 2 mots)')
    related_vsb_si_autre_personees        = fields.Boolean(u'Champs related_vsb_si_autre_personees - Visibilité')
    related_rqr_si_autre_personees        = fields.Boolean(u'Champs related_rqr_si_autre_personees - Obligation')
    si_autre_personees                    = fields.Char(u'Si « Autre (évènements relatifs à la sécurité des biens et des personnes) », à préciser (en 1 ou 2 mots)')
    related_vsb_en_case_suspectees        = fields.Boolean(u'Champs related_vsb_en_case_suspectees - Visibilité')
    related_rqr_en_case_suspectees        = fields.Boolean(u'Champs related_rqr_en_case_suspectees - Obligation')
    en_case_suspectees                    = fields.Char(u'En cas de décès, quelles sont les causes suspectées ? (en 1 ou 2 mots)')
    related_vsb_en_case_lesquelles        = fields.Boolean(u'Champs related_vsb_en_case_lesquelles - Visibilité')
    related_rqr_en_case_lesquelles        = fields.Boolean(u'Champs related_rqr_en_case_lesquelles - Obligation')
    en_case_lesquelles                    = fields.Char(u'En cas de défaillances techniques graves, lesquelles ? (en 1 ou 2 mots)')
    nature_precision                      = fields.Char('Précision nature évènement')
    related_vsb_nature_precision          = fields.Boolean(u'Champs related_vsb_nature_precision - Visibilité')
    related_rqr_nature_precision          = fields.Boolean(u'Champs related_rqr_nature_precision - Obligation')
#     type_risq_id                          = fields.Many2one('is.type.risque', "Type de risque", required=False, help=u"Permet de préciser sur quel temps du parcours de l'usager est apparu l'EIG.")
#     nature_risq_id                        = fields.Many2one('is.nature.risque', "Nature de risque", required=True, help=u"Permet d'identifier la nature du risque afin d'alimenter la cartographie des risques de la fondation OVE")
    signalement_autorites                 = fields.Boolean(u'Signalement aux autorités judiciaires')
    related_vsb_signalement_autorites     = fields.Boolean(u'Champs related_vsb_signalement_autorites - Visibilité')
    related_rqr_signalement_autorites     = fields.Boolean(u'Champs related_rqr_signalement_autorites - Obligation')
    consequence_personne_prise_en_charge_ids             = fields.Many2many('is.consequence.personne.prise.en.charge', 'is_type_event_prise_charge_rel', 'type_event_id', 'price_charge_id', string=u'Pour la ou les personnes prises en charge')
    related_vsb_consequence_personne_prise_en_charge_ids = fields.Boolean(u'Champs related_vsb_consequence_personne_prise_en_charge_ids - Visibilité')
    related_rqr_consequence_personne_prise_en_charge_ids = fields.Boolean(u'Champs related_rqr_consequence_personne_prise_en_charge_ids - Obligation')
    consequence_personnel_ids                            = fields.Many2many('is.consequence.personnel', 'is_type_event_personnel_rel', 'type_event_id', 'personnel_id', string=u'Pour les personnels')
    related_vsb_consequence_personnel_ids                = fields.Boolean(u'Champs related_vsb_consequence_personnel_ids - Visibilité')
    related_rqr_consequence_personnel_ids                = fields.Boolean(u'Champs related_rqr_consequence_personnel_ids - Obligation')
    consequence_fonctionnement_stucture_ids              = fields.Many2many('is.consequence.fonctionnement.stucture', 'is_type_event_stucture_rel', 'type_event_id', 'stucture_id', string=u'Pour l’organisation et le fonctionnement de la structure')
    related_vsb_consequence_fonctionnement_stucture_ids  = fields.Boolean(u'Champs related_vsb_consequence_fonctionnement_stucture_ids - Visibilité')
    related_rqr_consequence_fonctionnement_stucture_ids  = fields.Boolean(u'Champs related_rqr_consequence_fonctionnement_stucture_ids - Obligation')
    si_autre_pour_personnel                              = fields.Char(u'Si « autre (pour les personnels) », veuillez préciser')
    related_vsb_si_autre_pour_personnel                  = fields.Boolean(u'Champs related_vsb_si_autre_pour_personnel - Visibilité')
    related_rqr_si_autre_pour_personnel                  = fields.Boolean(u'Champs related_rqr_si_autre_pour_personnel - Obligation')
    si_autre_pour_organisation                           = fields.Char(u'Si « autre (pour l’organisation et le fonctionnement de la structure) », veuillez préciser')
    related_vsb_si_autre_pour_organisation               = fields.Boolean(u'Champs related_vsb_si_autre_pour_organisation - Visibilité')
    related_rqr_si_autre_pour_organisation               = fields.Boolean(u'Champs related_rqr_si_autre_pour_organisation - Obligation')
    nb_jours_interuption_travail                         = fields.Float(u'En cas d’interruption temporaire de travail, précisez le nombre de jours', digits=(12, 2))
    related_vsb_nb_jours_interuption_travail             = fields.Boolean(u'Champs related_vsb_nb_jours_interuption_travail - Visibilité')
    related_rqr_nb_jours_interuption_travail             = fields.Boolean(u'Champs related_rqr_nb_jours_interuption_travail - Obligation')
    fait_deja_produit                               = fields.Selection(OuiNon, u"Ces faits se sont-ils déjà produits en ce qui concerne la (les) personne(s) victime(s) ou auteur(s) ?")
    related_vsb_fait_deja_produit               = fields.Boolean(u'Champs related_vsb_fait_deja_produit - Visibilité')
    related_rqr_fait_deja_produit             = fields.Boolean(u'Champs related_rqr_fait_deja_produit - Obligation')
    eig_deja_declare                    = fields.Selection(OuiNon, u"Un EIG a-t-il déjà été déclaré pour des faits similaires ?")
    related_vsb_eig_deja_declare             = fields.Boolean(u'Champs related_vsb_eig_deja_declare - Visibilité')
    related_rqr_eig_deja_declare             = fields.Boolean(u'Champs related_rqr_eig_deja_declare - Obligation')
    risque_reproductibilite                    = fields.Selection(OuiNon, u"Risque de reproductivité ?")
    related_vsb_risque_reproductibilite             = fields.Boolean(u'Champs related_vsb_risque_reproductibilite - Visibilité')
    related_rqr_risque_reproductibilite             = fields.Boolean(u'Champs related_rqr_risque_reproductibilite - Obligation')
    risque_extension                    = fields.Selection(OuiNon, u"Risque d’extension ?")
    related_vsb_risque_extension             = fields.Boolean(u'Champs related_vsb_risque_extension - Visibilité')
    related_rqr_risque_extension             = fields.Boolean(u'Champs related_rqr_risque_extension - Obligation')
    risque_contentieux                    = fields.Selection(OuiNon, u"Risque de contentieux immédiat ?")
    related_vsb_risque_contentieux             = fields.Boolean(u'Champs related_vsb_risque_contentieux - Visibilité')
    related_rqr_risque_contentieux             = fields.Boolean(u'Champs related_rqr_risque_contentieux - Obligation')
    evenement_semble_maitrise                    = fields.Selection(OuiNon, u"L’évènement semble-t-il maîtrisé ?")
    related_vsb_evenement_semble_maitrise             = fields.Boolean(u'Champs related_vsb_evenement_semble_maitrise - Visibilité')
    related_rqr_evenement_semble_maitrise             = fields.Boolean(u'Champs related_rqr_evenement_semble_maitrise - Obligation')
    si_non_maitrise_precisez                    = fields.Char(u"Si non maîtrisé, précisez pourquoi")
    related_vsb_si_non_maitrise_precisez             = fields.Boolean(u'Champs related_vsb_si_non_maitrise_precisez - Visibilité')
    related_rqr_si_non_maitrise_precisez             = fields.Boolean(u'Champs related_rqr_si_non_maitrise_precisez - Obligation')
    start_date                            = fields.Datetime(u'Date heure de début', help=u"Date connue de début de l'événement. En cas de maladie il s'agit de la date connue de déclaration des symptômes chez le premier malade.")
    related_vsb_start_date                = fields.Boolean(u'Champs related_vsb_start_date - Visibilité')
    related_rqr_start_date                = fields.Boolean(u'Champs related_rqr_start_date - Obligation')
    date_heure_constatation_faits             = fields.Datetime('Date et heure de la constatation des faits')
    related_vsb_date_heure_constatation_faits = fields.Boolean(u'Champs related_vsb_date_heure_constatation_faits - Visibilité')
    related_rqr_date_heure_constatation_faits = fields.Boolean(u'Champs related_rqr_date_heure_constatation_faits - Obligation')
    end_date                              = fields.Datetime('Date heure de fin', help=u"Date connue de fin de l'événement. En cas de maladie il s'agit de la date connue de déclaration des symptômes chez le dernier malade.")
    related_vsb_end_date                  = fields.Boolean(u'Champs related_vsb_end_date - Visibilité')
    related_rqr_end_date                  = fields.Boolean(u'Champs related_rqr_end_date - Obligation')
    description_faits                     = fields.Text('Description des faits', help=u"Permet de décrire de manière exhaustive et détaillée les faits survenus dans votre établissement. En cas de maladie il est nécessaire de préciser de quelle maladie ou contamination il s'agit en l'espèce.")
    related_vsb_description_faits         = fields.Boolean(u'Champs related_vsb_description_faits - Visibilité')
    related_rqr_description_faits         = fields.Boolean(u'Champs related_rqr_description_faits - Obligation')
    criteres_generaux_ids                 = fields.Many2many('is.criteres.generaux', 'is_type_event_generaux_rel', 'type_event_id', 'generaux_id', string=u'Critères généraux')
    related_vsb_criteres_generaux_ids     = fields.Boolean(u'Champs related_vsb_criteres_generaux_ids - Visibilité')
    related_rqr_criteres_generaux_ids     = fields.Boolean(u'Champs related_rqr_criteres_generaux_ids - Obligation')
    solution_prise_en_charge              = fields.Selection(OuiNon, u'En cas d’évènement ayant pour conséquence une exclusion temporaire ou définitive, y a-t-il des solutions de prises en charges ?')
    related_vsb_solution_prise_en_charge  = fields.Boolean(u'Champs related_vsb_solution_prise_en_charge - Visibilité')
    related_rqr_solution_prise_en_charge  = fields.Boolean(u'Champs related_rqr_solution_prise_en_charge - Obligation')
    demande_intervention_secours_ids             = fields.Many2many('is.demande.intervention.secours', 'is_type_event_secours_rel', 'type_event_id', 'secours_id', string=u'Demande d’intervention des secours')
    related_vsb_demande_intervention_secours_ids = fields.Boolean(u'Champs related_vsb_demande_intervention_secours_ids - Visibilité')
    related_rqr_demande_intervention_secours_ids = fields.Boolean(u'Champs related_rqr_demande_intervention_secours_ids - Obligation')
    risque_reproductivite                 = fields.Selection(OuiNon, 'Risque de reproductivité')
    related_vsb_risque_reproductivite     = fields.Boolean(u'Champs related_vsb_risque_reproductivite - Visibilité')
    related_rqr_risque_reproductivite     = fields.Boolean(u'Champs related_rqr_risque_reproductivite - Obligation')
    risque_extension                      = fields.Selection(OuiNon, "Risque d'extension")
    related_vsb_risque_extension          = fields.Boolean(u'Champs related_vsb_risque_extension - Visibilité')
    related_rqr_risque_extension          = fields.Boolean(u'Champs related_rqr_risque_extension - Obligation')
    risque_contentieux                    = fields.Selection(OuiNon, "Risque de contentieux immédiat")
    related_vsb_risque_contentieux        = fields.Boolean(u'Champs related_vsb_risque_contentieux - Visibilité')
    related_rqr_risque_contentieux        = fields.Boolean(u'Champs related_rqr_risque_contentieux - Obligation')
    evenement_maitrise                    = fields.Selection(OuiNon, "L'événement semble t-il maîtrisé")
    related_vsb_evenement_maitrise        = fields.Boolean(u'Champs related_vsb_evenement_maitrise - Visibilité')
    related_rqr_evenement_maitrise        = fields.Boolean(u'Champs related_rqr_evenement_maitrise - Obligation')
    si_non_maitrise                       = fields.Text(u"Si non maîtrisé")
    related_vsb_si_non_maitrise           = fields.Boolean(u'Champs related_vsb_si_non_maitrise - Visibilité')
    related_rqr_si_non_maitrise           = fields.Boolean(u'Champs related_rqr_si_non_maitrise - Obligation')
    lieu_faits                            = fields.Char('Lieu', help=u"Permet d'indiquer le lieu de déroulement des faits")
    related_vsb_lieu_faits                = fields.Boolean(u'Champs related_vsb_lieu_faits - Visibilité')
    related_rqr_lieu_faits                = fields.Boolean(u'Champs related_rqr_lieu_faits - Obligation')
    element_faits                         = fields.Text(u'Eléments préoccupants')
    related_vsb_element_faits             = fields.Boolean(u'Champs related_vsb_element_faits - Visibilité')
    related_rqr_element_faits             = fields.Boolean(u'Champs related_rqr_element_faits - Obligation')
    cause_faits                           = fields.Boolean(u'Cause identifiée', help="Cet item est obligatoire en cas de « maladie » ou d'« atteinte à l'intégrité des usagers » dans la partie « Type de risque ».")
    related_vsb_cause_faits               = fields.Boolean(u'Champs related_vsb_cause_faits - Visibilité')
    related_rqr_cause_faits               = fields.Boolean(u'Champs related_rqr_cause_faits - Obligation')
    reunion_debriefing                    = fields.Selection(OuiNon, "Une première réunion de débriefing a-t-elle été organisée")
    related_vsb_reunion_debriefing        = fields.Boolean(u'Champs related_vsb_reunion_debriefing - Visibilité')
    related_rqr_reunion_debriefing        = fields.Boolean(u'Champs related_rqr_reunion_debriefing - Obligation')
    si_reunion_debriefing                 = fields.Text("Si oui, quelles sont les premières conclusions")
    related_vsb_si_reunion_debriefing     = fields.Boolean(u'Champs related_vsb_si_reunion_debriefing - Visibilité')
    related_rqr_si_reunion_debriefing     = fields.Boolean(u'Champs related_rqr_si_reunion_debriefing - Obligation')
    causes_profondes                      = fields.Selection(OuiNon, u"Une recherche des causes profondes a-t-elle été réalisée ou est-elle prévue")
    related_vsb_causes_profondes          = fields.Boolean(u'Champs related_vsb_causes_profondes - Visibilité')
    related_rqr_causes_profondes          = fields.Boolean(u'Champs related_rqr_causes_profondes - Obligation')
    
    
    premiere_cause_identifiee                    = fields.Boolean(u"1ere(s) cause(s) identifiée(s)")
    related_vsb_premiere_cause_identifiee        = fields.Boolean(u'Champs related_vsb_premiere_cause_identifiee - Visibilité')
    related_rqr_premiere_cause_identifiee        = fields.Boolean(u'Champs related_rqr_premiere_cause_identifiee - Obligation')
    evolution_previsible                         = fields.Text(u"Evolutions prévisibles ou difficultés attendues")
    related_vsb_evolution_previsible             = fields.Boolean(u'Champs related_vsb_evolution_previsible - Visibilité')
    related_rqr_evolution_previsible             = fields.Boolean(u'Champs related_rqr_evolution_previsible - Obligation')
    
    enseignements_a_tirer                        = fields.Text(u"Y a-t-il des enseignements à tirer au niveau de l'établissement, ou au niveau régional, de l'évènement pour prévenir sa reproduction")
    related_vsb_enseignements_a_tirer            = fields.Boolean(u'Champs related_vsb_enseignements_a_tirer - Visibilité')
    related_rqr_enseignements_a_tirer            = fields.Boolean(u'Champs related_rqr_enseignements_a_tirer - Obligation')
    mesure_pour_proteger_accompagner             = fields.Text(u"Pour protéger, accompagner ou soutenir les personnes victimes ou exposées")
    related_vsb_mesure_pour_proteger_accompagner = fields.Boolean(u'Champs related_vsb_mesure_pour_proteger_accompagner - Visibilité')
    related_rqr_mesure_pour_proteger_accompagner = fields.Boolean(u'Champs related_rqr_mesure_pour_proteger_accompagner - Obligation')
    mesure_pour_assurer_continuite               = fields.Text(u"Pour assurer la continuité de la prise en charge, le cas échéant")
    related_vsb_mesure_pour_assurer_continuite   = fields.Boolean(u'Champs related_vsb_mesure_pour_assurer_continuite - Visibilité')
    related_rqr_mesure_pour_assurer_continuite   = fields.Boolean(u'Champs related_rqr_mesure_pour_assurer_continuite - Obligation')
    mesure_egard_autres_personnes                = fields.Text(u"A l’égard des autres personnes prises en charge ou du personnel, le cas échéant (par exemple : information à l’ensemble des usagers, soutien psychologique...)")
    related_vsb_mesure_egard_autres_personnes    = fields.Boolean(u'Champs related_vsb_mesure_egard_autres_personnes - Visibilité')
    related_rqr_mesure_egard_autres_personnes    = fields.Boolean(u'Champs related_rqr_mesure_egard_autres_personnes - Obligation')
    mesure_autre                                 = fields.Text(u"Autre (à préciser)")
    related_vsb_mesure_autre                     = fields.Boolean(u'Champs related_vsb_mesure_autre - Visibilité')
    related_rqr_mesure_autre                     = fields.Boolean(u'Champs related_rqr_mesure_autre - Obligation')
    mesure_usagers                               = fields.Text(u"Concernant les usagers ou les résidents")
    related_vsb_mesure_usagers                   = fields.Boolean(u'Champs related_vsb_mesure_usagers - Visibilité')
    related_rqr_mesure_usagers                   = fields.Boolean(u'Champs related_rqr_mesure_usagers - Obligation')
    mesure_personnel                             = fields.Text(u"Concernant le personnel")
    related_vsb_mesure_personnel                 = fields.Boolean(u'Champs related_vsb_mesure_personnel - Visibilité')
    related_rqr_mesure_personnel                 = fields.Boolean(u'Champs related_rqr_mesure_personnel - Obligation')
    mesure_organisation                          = fields.Text(u"Concernant l’organisation du travail")
    related_vsb_mesure_organisation              = fields.Boolean(u'Champs related_vsb_mesure_organisation - Visibilité')
    related_rqr_mesure_organisation              = fields.Boolean(u'Champs related_rqr_mesure_organisation - Obligation')
    mesure_structure                             = fields.Text(u"Concernant la structure")
    related_vsb_mesure_structure                 = fields.Boolean(u'Champs related_vsb_mesure_structure - Visibilité')
    related_rqr_mesure_structure                 = fields.Boolean(u'Champs related_rqr_mesure_structure - Obligation')
    si_causes_profondes                   = fields.Text("Si oui, quelle est la méthodologie utilisée")
    related_vsb_si_causes_profondes       = fields.Boolean(u'Champs related_vsb_si_causes_profondes - Visibilité')
    related_rqr_si_causes_profondes       = fields.Boolean(u'Champs related_rqr_si_causes_profondes - Obligation')
#     enseignements_a_tirer                 = fields.Selection(OuiNon, "Enseignements à tirer", help="Y a-t-il des enseignements à tirer au niveau de l’établissement, ou au niveau régional, de l’événement pour prévenir sa reproduction")
#     related_vsb_enseignements_a_tirer     = fields.Boolean(u'Champs related_vsb_enseignements_a_tirer - Visibilité')
#     related_rqr_enseignements_a_tirer     = fields.Boolean(u'Champs related_rqr_enseignements_a_tirer - Obligation')
    si_enseignements_a_tirer              = fields.Text("Si oui, lesquels")
    related_vsb_si_enseignements_a_tirer  = fields.Boolean(u'Champs related_vsb_si_enseignements_a_tirer - Visibilité')
    related_rqr_si_enseignements_a_tirer  = fields.Boolean(u'Champs related_rqr_si_enseignements_a_tirer - Obligation')
#     mesure_organisation                   = fields.Text('Organisationnelles', help=u"Permet d'indiquer les mesures prises au niveau du fonctionnement de l'établissement pour répondre à cet EIG")
#     related_vsb_mesure_organisation       = fields.Boolean(u'Champs related_vsb_mesure_organisation - Visibilité')
#     related_rqr_mesure_organisation       = fields.Boolean(u'Champs related_rqr_mesure_organisation - Obligation')
#     mesure_personnel                      = fields.Text(u'Personnel établissement', help=u"Permet d'indiquer les mesures prises (accompagnement, dialogue interne, disciplinaires...) à l'égard d'un ou de plusieurs membres du personnel suite à la déclaration de cet EIG.")
#     related_vsb_mesure_personnel          = fields.Boolean(u'Champs related_vsb_mesure_personnel - Visibilité')
#     related_rqr_mesure_personnel          = fields.Boolean(u'Champs related_rqr_mesure_personnel - Obligation')
#     mesure_usagers                        = fields.Text('Autres usagers', help=u"Permet d'indiquer les mesures prises à l'égard des usagers non directement touchés par cet EIG")
#     related_vsb_mesure_usagers            = fields.Boolean(u'Champs related_vsb_mesure_usagers - Visibilité')
#     related_rqr_mesure_usagers            = fields.Boolean(u'Champs related_rqr_mesure_usagers - Obligation')
#     mesure_autres                         = fields.Text('Autres', help=u"Permet d'indiquer les mesures prises à l'égard des autres personnes potentiellement impliquées (famille, professionnels extérieurs, structure partenaire...) suite à la déclaration de cet EIG.")
#     related_vsb_mesure_autres             = fields.Boolean(u'Champs related_vsb_mesure_autres - Visibilité')
#     related_rqr_mesure_autres             = fields.Boolean(u'Champs related_rqr_mesure_autres - Obligation')
    note                                  = fields.Text('Note')
    related_vsb_note                      = fields.Boolean(u'Champs related_vsb_note - Visibilité')
    related_rqr_note                      = fields.Boolean(u'Champs related_rqr_note - Obligation')
    attachment_ids                        = fields.Many2many('ir.attachment', 'is_eig_attachment_rel', 'eig_id', 'attachment_id', u'Pièces jointes', help=u"Permet d'ajouter, si besoin, tout élément complémentaire susceptible d'aider à la compréhension de l'EIG (chrono, rapport éducatif,...). Pour rappel : il est inutile de surcharger l'information.")
    related_vsb_attachment_ids            = fields.Boolean(u'Champs related_vsb_attachment_ids - Visibilité')
    related_rqr_attachment_ids            = fields.Boolean(u'Champs related_rqr_attachment_ids - Obligation')
    auteur_ids                            = fields.One2many('is.eig.auteur', 'is_eig_id', 'Auteur')
    related_vsb_auteur_ids                = fields.Boolean(u'Champs related_vsb_auteur_ids - Visibilité')
    related_rqr_auteur_ids                = fields.Boolean(u'Champs related_rqr_auteur_ids - Obligation')
    temoin_ids                            = fields.One2many('is.eig.temoin', 'is_eig_id', u'Témoins')
    related_vsb_temoin_ids                = fields.Boolean(u'Champs related_vsb_temoin_ids - Visibilité')
    related_rqr_temoin_ids                = fields.Boolean(u'Champs related_rqr_temoin_ids - Obligation')
    victim_ids                            = fields.One2many('is.eig.victime', 'is_eig_id', 'Victime')
    related_vsb_victim_ids                = fields.Boolean(u'Champs related_vsb_victim_ids - Visibilité')
    related_rqr_victim_ids                = fields.Boolean(u'Champs related_rqr_victim_ids - Obligation')
    intervention_police                   = fields.Selection(OuiNon, "Intervention de la police")
    related_vsb_intervention_police       = fields.Boolean(u'Champs related_vsb_intervention_police - Visibilité')
    related_rqr_intervention_police       = fields.Boolean(u'Champs related_rqr_intervention_police - Obligation')
    depot_plainte                         = fields.Selection(OuiNon, u"Dépôt de plainte par la famille")
    related_vsb_depot_plainte             = fields.Boolean(u'Champs related_vsb_depot_plainte - Visibilité')
    related_rqr_depot_plainte             = fields.Boolean(u'Champs related_rqr_depot_plainte - Obligation')
    enquete_police                        = fields.Selection(OuiNon, u"Enquête de police ou gendarmerie ")
    related_vsb_enquete_police            = fields.Boolean(u'Champs related_vsb_enquete_police - Visibilité')
    related_rqr_enquete_police            = fields.Boolean(u'Champs related_rqr_enquete_police - Obligation')
    depot_plainte_famille                 = fields.Selection(OuiNon, u"Dépôt de plainte par la famille")
    related_vsb_depot_plainte_famille     = fields.Boolean(u'Champs related_vsb_depot_plainte_famille - Visibilité')
    related_rqr_depot_plainte_famille     = fields.Boolean(u'Champs related_rqr_depot_plainte_famille - Obligation')
    communication_prevue                  = fields.Selection(OuiNon, u"Une communication par la Fondation est-elle prévue")
    related_vsb_communication_prevue      = fields.Boolean(u'Champs related_vsb_communication_prevue - Visibilité')
    related_rqr_communication_prevue      = fields.Boolean(u'Champs related_rqr_communication_prevue - Obligation')
    communication_prevue_oui              = fields.Text(u"Si oui, précisez")
    related_vsb_communication_prevue_oui  = fields.Boolean(u'Champs related_vsb_communication_prevue_oui - Visibilité')
    related_rqr_communication_prevue_oui  = fields.Boolean(u'Champs related_rqr_communication_prevue_oui - Obligation')
    infos_ids                             = fields.One2many('is.infos.communication', 'is_eig_id', 'Information communication')
    related_vsb_infos_ids                 = fields.Boolean(u'Champs related_vsb_infos_ids - Visibilité')
    related_rqr_infos_ids                 = fields.Boolean(u'Champs related_rqr_infos_ids - Obligation')
    motif_ids                             = fields.One2many('is.motif.retour.eig', 'eig_id1', 'Motif de retour', readonly=True)
    related_aut_vsb_identifie             = fields.Boolean(u'Champs related_aut_vsb_identifie - Visibilité')
    related_aut_rqr_identifie             = fields.Boolean(u'Champs related_aut_rqr_identifie - Obligation')
    related_aut_vsb_name                  = fields.Boolean(u'Champs technique - Visibilité')
    related_aut_rqr_name                  = fields.Boolean(u'Champs related_aut_vsb_name - Obligation')
    related_aut_vsb_prenom                = fields.Boolean(u'Champs related_aut_vsb_prenom - Visibilité')
    related_aut_rqr_prenom                = fields.Boolean(u'Champs related_aut_rqr_prenom - Obligation')
    related_aut_vsb_birthdate             = fields.Boolean(u'Champs related_aut_vsb_birthdate - Visibilité')
    related_aut_rqr_birthdate             = fields.Boolean(u'Champs related_aut_rqr_birthdate - Obligation')
    related_aut_vsb_qualite_id            = fields.Boolean(u'Champs related_aut_vsb_qualite_id - Visibilité')
    related_aut_rqr_qualite_id            = fields.Boolean(u'Champs related_aut_rqr_qualite_id - Obligation')
    related_aut_vsb_disposition_id        = fields.Boolean(u'Champs related_aut_vsb_disposition_id - Visibilité')
    related_aut_rqr_disposition_id        = fields.Boolean(u'Champs related_aut_rqr_disposition_id - Obligation')
    related_aut_vsb_sexe_id               = fields.Boolean(u'Champs related_aut_vsb_sexe_id - Visibilité')
    related_aut_rqr_sexe_id               = fields.Boolean(u'Champs related_aut_rqr_sexe_id - Obligation')
    related_aut_vsb_adresse               = fields.Boolean(u'Champs related_aut_vsb_adresse - Visibilité')
    related_aut_rqr_adresse               = fields.Boolean(u'Champs related_aut_rqr_adresse - Obligation')
    related_tem_vsb_identifie             = fields.Boolean(u'Champs related_tem_vsb_identifie - Visibilité')
    related_tem_rqr_identifie             = fields.Boolean(u'Champs related_tem_rqr_identifie - Obligation')
    related_tem_vsb_name                  = fields.Boolean(u'Champs related_tem_vsb_name - Visibilité')
    related_tem_rqr_name                  = fields.Boolean(u'Champs related_tem_rqr_name - Obligation')
    related_tem_vsb_prenom                = fields.Boolean(u'Champs related_tem_vsb_prenom - Visibilité')
    related_tem_rqr_prenom                = fields.Boolean(u'Champs related_tem_rqr_prenom - Obligation')
    related_tem_vsb_sexe_id               = fields.Boolean(u'Champs related_tem_vsb_sexe_id - Visibilité')
    related_tem_rqr_sexe_id               = fields.Boolean(u'Champs related_tem_rqr_sexe_id - Obligation')
    related_tem_vsb_address               = fields.Boolean(u'Champs related_tem_vsb_address - Visibilité')
    related_tem_rqr_address               = fields.Boolean(u'Champs related_tem_rqr_address - Obligation')
    related_tem_vsb_birthdate             = fields.Boolean(u'Champs related_tem_vsb_birthdate - Visibilité')
    related_tem_rqr_birthdate             = fields.Boolean(u'Champs related_tem_rqr_birthdate - Obligation')
    related_tem_vsb_qualite_id            = fields.Boolean(u'Champs related_tem_vsb_qualite_id - Visibilité')
    related_tem_rqr_qualite_id            = fields.Boolean(u'Champs related_tem_rqr_qualite_id - Obligation')
    related_tem_vsb_disposition_id        = fields.Boolean(u'Champs related_tem_vsb_disposition_id - Visibilité')
    related_tem_rqr_disposition_id        = fields.Boolean(u'Champs related_tem_rqr_disposition_id - Obligation')
    related_vict_vsb_identifie            = fields.Boolean(u'Champs related_vict_vsb_identifie - Visibilité')
    related_vict_rqr_identifie            = fields.Boolean(u'Champs related_vict_rqr_identifie - Obligation')
    related_vict_vsb_name                 = fields.Boolean(u'Champs related_vict_vsb_name - Visibilité')
    related_vict_rqr_name                 = fields.Boolean(u'Champs related_vict_rqr_name - Obligation')
    related_vict_vsb_prenom               = fields.Boolean(u'Champs related_vict_vsb_prenom - Visibilité')
    related_vict_rqr_prenom               = fields.Boolean(u'Champs related_vict_rqr_prenom - Obligation')
    related_vict_vsb_sexe_id              = fields.Boolean(u'Champs related_vict_vsb_sexe_id - Visibilité')
    related_vict_rqr_sexe_id              = fields.Boolean(u'Champs related_vict_rqr_sexe_id - Obligation')
    related_vict_vsb_address              = fields.Boolean(u'Champs related_vict_vsb_address - Visibilité')
    related_vict_rqr_address              = fields.Boolean(u'Champs related_vict_rqr_address - Obligation')
    related_vict_vsb_ecole                = fields.Boolean(u'Champs related_vict_vsb_ecole - Visibilité')
    related_vict_rqr_ecole                = fields.Boolean(u'Champs related_vict_rqr_ecole - Obligation')
    related_vict_vsb_birthdate            = fields.Boolean(u'Champs related_vict_vsb_birthdate - Visibilité')
    related_vict_rqr_birthdate            = fields.Boolean(u'Champs related_vict_rqr_birthdate - Obligation')
    related_vict_vsb_qualite_id           = fields.Boolean(u'Champs related_vict_vsb_qualite_id - Visibilité')
    related_vict_rqr_qualite_id           = fields.Boolean(u'Champs related_vict_rqr_qualite_id - Obligation')
    related_vict_vsb_disposition_id       = fields.Boolean(u'Champs related_vict_vsb_disposition_id - Visibilité')
    related_vict_rqr_disposition_id       = fields.Boolean(u'Champs related_vict_rqr_disposition_id - Obligation')
    related_vict_vsb_consequence_id       = fields.Boolean(u'Champs related_vict_vsb_consequence_id - Visibilité')
    related_vict_rqr_consequence_id       = fields.Boolean(u'Champs related_vict_rqr_consequence_id - Obligation')
    related_vict_vsb_nom_pere             = fields.Boolean(u'Champs related_vict_vsb_nom_pere - Visibilité')
    related_vict_rqr_nom_pere             = fields.Boolean(u'Champs related_vict_rqr_nom_pere - Obligation')
    related_vict_vsb_prenom_pere          = fields.Boolean(u'Champs related_vict_vsb_prenom_pere - Visibilité')
    related_vict_rqr_prenom_pere          = fields.Boolean(u'Champs related_vict_rqr_prenom_pere - Obligation')
    related_vict_vsb_address_pere         = fields.Boolean(u'Champs related_vict_vsb_address_pere - Visibilité')
    related_vict_rqr_address_pere         = fields.Boolean(u'Champs related_vict_rqr_address_pere - Obligation')
    related_vict_vsb_nom_mere             = fields.Boolean(u'Champs related_vict_vsb_nom_mere - Visibilité')
    related_vict_rqr_nom_mere             = fields.Boolean(u'Champs related_vict_rqr_nom_mere - Obligation')
    related_vict_vsb_prenom_mere          = fields.Boolean(u'Champs related_vict_vsb_prenom_mere - Visibilité')
    related_vict_rqr_prenom_mere          = fields.Boolean(u'Champs related_vict_rqr_prenom_mere - Obligation')
    related_vict_vsb_address_mere         = fields.Boolean(u'Champs related_vict_vsb_address_mere - Visibilité')
    related_vict_rqr_address_mere         = fields.Boolean(u'Champs related_vict_rqr_address_mere - Obligation')
    related_vict_vsb_auteur_victime       = fields.Boolean(u'Champs related_vict_vsb_auteur_victime - Visibilité')
    related_vict_rqr_auteur_victime       = fields.Boolean(u'Champs related_vict_rqr_auteur_victime - Obligation')
    related_vict_vsb_tuteur_nom           = fields.Boolean(u'Champs related_vict_vsb_tuteur_nom - Visibilité')
    related_vict_rqr_tuteur_nom           = fields.Boolean(u'Champs related_vict_rqr_tuteur_nom - Obligation')
    related_vict_vsb_tuteur_prenom        = fields.Boolean(u'Champs related_vict_vsb_tuteur_prenom - Visibilité')
    related_vict_rqr_tuteur_prenom        = fields.Boolean(u'Champs related_vict_rqr_tuteur_prenom - Obligation')
    related_vict_vsb_tuteur_adresse       = fields.Boolean(u'Champs related_vict_vsb_tuteur_adresse - Visibilité')
    related_vict_rqr_tuteur_adresse       = fields.Boolean(u'Champs related_vict_rqr_tuteur_adresse - Obligation')
    related_inf_vsb_date                  = fields.Boolean(u'Champs related_inf_vsb_date - Visibilité')
    related_inf_rqr_date                  = fields.Boolean(u'Champs related_inf_rqr_date - Obligation')
    related_inf_vsb_user_id               = fields.Boolean(u'Champs related_inf_vsb_user_id - Visibilité')
    related_inf_rqr_user_id               = fields.Boolean(u'Champs related_inf_rqr_user_id - Obligation')
    related_inf_vsb_responsible_id        = fields.Boolean(u'Champs related_inf_vsb_responsible_id - Visibilité')
    related_inf_rqr_responsible_id        = fields.Boolean(u'Champs related_inf_rqr_responsible_id - Obligation')
    related_inf_vsb_support               = fields.Boolean(u'Champs related_inf_vsb_support - Visibilité')
    related_inf_rqr_support               = fields.Boolean(u'Champs related_inf_rqr_support - Obligation')
    related_inf_vsb_info_cible            = fields.Boolean(u'Champs related_inf_vsb_info_cible - Visibilité')
    related_inf_rqr_info_cible            = fields.Boolean(u'Champs related_inf_rqr_info_cible - Obligation')
    related_inf_vsb_impact                = fields.Boolean(u'Champs related_inf_vsb_impact - Visibilité')
    related_inf_rqr_impact                = fields.Boolean(u'Champs related_inf_rqr_impact - Obligation')
    related_onglet_faits                  = fields.Boolean(u'Champs related_onglet_faits - Onglet Faits')
    related_onglet_auteurs                = fields.Boolean(u'Champs related_onglet_auteurs - Onglet Auteurs')
    related_onglet_temoins                = fields.Boolean(u'Champs related_onglet_temoins - Onglet Témoins')
    related_onglet_victimes               = fields.Boolean(u'Champs related_onglet_victimes - Onglet Victimes')
    related_onglet_mesures                = fields.Boolean(u'Champs related_onglet_mesures - Onglet Mesures')
    related_onglet_infos                  = fields.Boolean(u'Champs related_onglet_infos - Onglet Infos')
    related_onglet_element_complementaire = fields.Boolean(u'Champs related_onglet_element_complementaire - Onglet Eléments complémentaires')
    related_group_motif_retour            = fields.Boolean(u'Champs related_group_motif_retour - Tableau motif retour')
    autre_personne_ids                         = fields.One2many('is.eig.autre.personne', 'is_eig_id', u"Autre(s) personne(s) concernée(s) par l’IP")
    related_vsb_autre_personne_ids             = fields.Boolean(u'Champs related_vsb_autre_personne_ids - Visibilité')
    related_rqr_autre_personne_ids             = fields.Boolean(u'Champs related_rqr_autre_personne_ids - Obligation')
    related_autre_personne_vsb_identifie       = fields.Boolean(u'Champs related_autre_personne_vsb_identifie - Visibilité')
    related_autre_personne_rqr_identifie       = fields.Boolean(u'Champs related_autre_personne_rqr_identifie - Obligation')
    related_autre_personne_vsb_nom             = fields.Boolean(u'Champs related_autre_personne_vsb_nom - Visibilité')
    related_autre_personne_rqr_nom             = fields.Boolean(u'Champs related_autre_personne_rqr_nom - Obligation')
    related_autre_personne_vsb_prenom          = fields.Boolean(u'Champs related_autre_personne_vsb_prenom - Visibilité')
    related_autre_personne_rqr_prenom          = fields.Boolean(u'Champs related_autre_personne_rqr_prenom - Obligation')
    related_autre_personne_vsb_qualite_id      = fields.Boolean(u'Champs related_autre_personne_vsb_qualite_id - Visibilité')
    related_autre_personne_rqr_qualite_id      = fields.Boolean(u'Champs related_autre_personne_rqr_qualite_id - Obligation')
    related_autre_personne_vsb_consequence_id  = fields.Boolean(u'Champs related_autre_personne_vsb_consequence_id - Visibilité')
    related_autre_personne_rqr_consequence_id  = fields.Boolean(u'Champs related_autre_personne_rqr_consequence_id - Obligation')
    related_autre_personne_vsb_disposition_id  = fields.Boolean(u'Champs related_autre_personne_vsb_disposition_id - Visibilité')
    related_autre_personne_rqr_disposition_id  = fields.Boolean(u'Champs related_autre_personne_rqr_disposition_id - Obligation')
    related_autre_personne_vsb_auteur_victime  = fields.Boolean(u'Champs related_autre_personne_vsb_auteur_victime - Visibilité')
    related_autre_personne_rqr_auteur_victime  = fields.Boolean(u'Champs related_autre_personne_rqr_auteur_victime - Obligation')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Files')

class Item(object):
    pass

class is_default_type_event(models.Model):
    _name = 'is.default.type.event'
    _description = "Event Default Type"

    @api.multi
    def get_eig_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['start_date', 'date_heure_constatation_faits', 'end_date', 'nature_precision', 'description_faits',
                           'lieu_faits', 'element_faits', 'cause_faits', 'criteres_generaux_ids', 'solution_prise_en_charge',
                           'demande_intervention_secours_ids'
            ])])
        return field_ids

    @api.multi
    def get_fields_eig_properties(self, visible=False):
        field_ids = self.get_eig_fields()
        lst = []
        sequence = {
            'start_date': 1,
            'date_heure_constatation_faits': 2,
            'lieu_faits': 3,
            'end_date': 4,
            'cause_faits': 5,
            'description_faits': 6,
            'criteres_generaux_ids': 7,
            'solution_prise_en_charge': 8,
            'demande_intervention_secours_ids': 9,
            'element_faits': 10,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def get_mesures_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['reunion_debriefing','si_reunion_debriefing','causes_profondes','si_causes_profondes',
                           'enseignements_a_tirer','si_enseignements_a_tirer','premiere_cause_identifiee',
                           'evolution_previsible','mesure_pour_proteger_accompagner',
                           'mesure_pour_assurer_continuite','mesure_egard_autres_personnes','mesure_autre',
                           'mesure_usagers','mesure_personnel','mesure_organisation','mesure_structure'
            ])])
        return field_ids

    @api.multi
    def get_fields_mesures_properties(self, visible=False):
        field_ids = self.get_mesures_fields()
        lst = []
        sequence = {
            'si_causes_profondes': 1,
            'si_reunion_debriefing': 2,
            'reunion_debriefing': 3,
            'causes_profondes': 4,
            'premiere_cause_identifiee': 5,
            'evolution_previsible': 6,
            'enseignements_a_tirer': 7,
            'mesure_pour_proteger_accompagner': 8,
            'mesure_pour_assurer_continuite': 9,
            'mesure_egard_autres_personnes': 10,
            'mesure_autre': 11,
            'mesure_usagers': 12,
            'mesure_personnel': 13,
            'mesure_organisation': 14,
            'mesure_structure': 15,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_mesures': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def get_elements_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['note', 'attachment_ids',
            ])])
        return field_ids

    @api.multi
    def get_fields_elements_properties(self, visible=False):
        field_ids = self.get_elements_fields()
        lst = []
        for field_id in field_ids:
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_elements': True,
            }))
        return lst

    @api.multi
    def get_group_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['consequence_personne_prise_en_charge_ids', 'consequence_personnel_ids', 'consequence_fonctionnement_stucture_ids',
                            'si_autre_pour_personnel', 'si_autre_pour_organisation', 'nb_jours_interuption_travail',
                            'fait_deja_produit', 'eig_deja_declare', 'risque_reproductibilite', 'risque_extension',
                            'risque_contentieux', 'evenement_semble_maitrise', 'si_non_maitrise_precisez',
            ])])
        return field_ids

    @api.multi
    def get_fields_group_properties(self, visible=False):
        field_ids = self.get_group_fields()
        lst = []
        for field_id in field_ids:
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_group': True,
            }))
        return lst

    @api.multi
    def get_entete_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['signalement_autorites', 'si_autre_presumees', 'si_autre_personees',
                            'en_case_suspectees', 'en_case_lesquelles',
            ])])
        return field_ids

    @api.multi
    def get_fields_entete_properties(self, visible=False):
        field_ids = self.get_entete_fields()
        lst = []
        for field_id in field_ids:
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_entete': True,
            }))
        return lst

    @api.multi
    def get_auteur_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig.auteur'),
            ('name', 'in', ('identifie', 'name', 'adresse', 'prenom', 'birthdate',
                           'qualite_id', 'sexe_id', 'disposition_id',
            ))])
        return field_ids

    @api.multi
    def get_fields_auteur_properties(self, visible=False):
        field_ids = self.get_auteur_fields()
        lst = []
        sequence = {
            'identifie': 1,
            'name': 2,
            'prenom': 3,
            'sexe_id': 4,
            'birthdate': 5,
            'qualite_id': 6,
            'disposition_id': 7,
            'adresse': 8,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_auteur': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def get_victim_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig.victime'),
            ('name','in', ('identifie','name','prenom','address','ecole','birthdate','sexe_id',
                           'qualite_id','disposition_id','consequence_id','nom_pere','prenom_pere',
                            'address_pere','nom_mere','prenom_mere','address_mere', 'auteur_victime',
                            'tuteur_nom','tuteur_prenom','tuteur_adresse',
            ))])
        return field_ids

    @api.multi
    def get_fields_victim_properties(self, visible=False):
        field_ids = self.get_victim_fields()
        lst = []
        sequence = {
            'identifie': 1,
            'name': 2,
            'prenom': 3,
            'sexe_id': 4,
            'birthdate': 5,
            'address': 6,
            'ecole': 7,
            'qualite_id': 8,
            'consequence_id': 9,
            'disposition_id': 10,
            'auteur_victime': 11,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False, 
                'is_eig_victim': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def get_temoin_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig.temoin'),
            ('name','in', ('identifie','name','prenom','sexe_id','address',
                           'birthdate','qualite_id','disposition_id'
            ))])
        return field_ids

    @api.multi
    def get_fields_temoin_properties(self, visible=False):
        field_ids = self.get_temoin_fields()
        lst = []
        sequence = {
            'identifie': 1,
            'name': 2,
            'prenom': 3,
            'sexe_id': 4,
            'birthdate': 5,
            'address': 6,
            'disposition_id': 7,
            'qualite_id': 8,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0, {
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_temoin': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def get_infos_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.infos.communication'),
            ('name','in', ('date','user_id','responsible_id','support',
                           'info_cible','impact',
            ))])
        return field_ids

    @api.multi
    def get_fields_infos_properties(self, visible=False):
        field_ids = self.get_infos_fields()
        lst = []
        for field_id in field_ids:
            lst.append((0,0,{'fields_id': field_id.id, 'field_visible': visible, 'field_required': False, 'is_eig_infos': True}))
        return lst

    @api.multi
    def get_infos2_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['intervention_police', 'depot_plainte', 'enquete_police',
                            'depot_plainte_famille', 'communication_prevue', 'communication_prevue_oui'
            ])])
        return field_ids

    @api.multi
    def get_fields_infos2_properties(self, visible=False):
        field_ids = self.get_infos2_fields()
        lst = []
        sequence = {
            'intervention_police': 1,
            'depot_plainte': 2,
            'enquete_police': 3,
            'communication_prevue': 4,
            'communication_prevue_oui': 5,
            'depot_plainte_famille': 6,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0,{
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_infos2': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def get_autre_personne_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig.autre.personne'),
            ('name','in', ('identifie','nom','prenom','qualite_id','consequence_id','disposition_id','auteur_victime',
            ))])
        return field_ids

    @api.multi
    def get_fields_autre_personne_properties(self, visible=False):
        field_ids = self.get_autre_personne_fields()
        lst = []
        sequence = {
            'identifie': 1,
            'nom': 2,
            'prenom': 3,
            'qualite_id': 4,
            'consequence_id': 5,
            'disposition_id': 6,
            'auteur_victime': 7,
        }
        for field_id in field_ids:
            seq = sequence.get(field_id.name, 999)
            lst.append((0,0,{
                'fields_id': field_id.id,
                'field_visible': visible,
                'field_required': False, 
                'is_eig_autre_personne': True,
                'sequence': seq,
            }))
        return lst

    @api.multi
    def manip_type_evenement1(self):
        eig_lst = []
        fields_eig_ids = self.get_eig_fields()
        for field in fields_eig_ids:
            if field.name == 'nature_precision':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'start_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'end_date':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': False, 'is_eig': True}])
            if field.name == 'description_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'lieu_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'element_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'cause_faits':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
        mesures_lst = []
        fields_mesures_ids = self.get_mesures_fields()
        for field in fields_mesures_ids:
            if field.name == 'reunion_debriefing':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'si_reunion_debriefing':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'causes_profondes':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'si_causes_profondes':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'si_enseignements_a_tirer':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'premiere_cause_identifiee':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'evolution_previsible':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'enseignements_a_tirer':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_pour_proteger_accompagner':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_pour_assurer_continuite':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_egard_autres_personnes':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_autre':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_usagers':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_personnel':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_organisation':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            if field.name == 'mesure_structure':
                mesures_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig_mesures': True}])
            
            
        elements_lst = []
        fields_elements_ids = self.get_elements_fields()
        for field in fields_elements_ids:
            if field.name == 'note':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_elements': True}])
            if field.name == 'attachment_ids':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_elements': True}])
        group_lst = []
        fields_group_ids = self.get_group_fields()
        for field in fields_group_ids:
            if field.name == 'consequence_personne_prise_en_charge_ids':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'consequence_personnel_ids':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'consequence_fonctionnement_stucture_ids':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'si_autre_pour_personnel':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'si_autre_pour_organisation':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'nb_jours_interuption_travail':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'fait_deja_produit':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'eig_deja_declare':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'risque_reproductibilite':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'risque_extension':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'risque_contentieux':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'evenement_semble_maitrise':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
            if field.name == 'si_non_maitrise_precisez':
                group_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_group': True}])
        entete_lst = []
        fields_entete_ids = self.get_entete_fields()
        for field in fields_entete_ids:
            if field.name == 'signalement_autorites':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_entete': True}])
            if field.name == 'si_autre_presumees':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_entete': True}])
            if field.name == 'si_autre_personees':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_entete': True}])
            if field.name == 'en_case_suspectees':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_entete': True}])
            if field.name == 'en_case_lesquelles':
                elements_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_entete': True}])
        victim_lst = []
        default_victim_lst = self.get_fields_victim_properties(False)
        for item in default_victim_lst:
            item.update({'field_visible': True})
            victim_lst.append([0,False, item])
        auteur_lst = []
        default_auteur_lst = self.get_fields_auteur_properties(False)
        for item in default_auteur_lst:
            auteur_lst.append([0,False, item])
        temoin_lst = []   
        default_temoin_lst = self.get_fields_temoin_properties(False)
        for item in default_temoin_lst:
            temoin_lst.append([0,False, item])
        infos_lst = []
        default_infos_lst = self.get_fields_infos_properties(False)
        for item in default_infos_lst:
            infos_lst.append([0,False, item])
        infos2_lst = []
        fields_infos2_ids = self.get_infos2_fields()
        for field in fields_infos2_ids:
            if field.name == 'intervention_police':
                infos2_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_infos2': True}])
            if field.name == 'depot_plainte':
                infos2_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_infos2': True}])
            if field.name == 'enquete_police':
                infos2_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_infos2': True}])
            if field.name == 'depot_plainte_famille':
                infos2_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_infos2': True}])
            if field.name == 'communication_prevue':
                infos2_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_infos2': True}])
            if field.name == 'communication_prevue_oui':
                infos2_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig_infos2': True}])
        autre_personne_lst = []
        default_autre_personne_lst = self.get_fields_autre_personne_properties(False)
        for item in default_autre_personne_lst:
            item.update({'field_visible': True})
            autre_personne_lst.append([0,False, item])
        return {
            'eig'           : eig_lst,
            'auteur'        : auteur_lst,
            'temoin'        : temoin_lst,
            'victim'        : victim_lst,
            'infos'         : infos_lst,
            'infos2'        : infos2_lst,
            'mesures'       : mesures_lst,
            'elements'      : elements_lst,
            'group'         : group_lst,
            'entete'        : entete_lst,
            'autre_personne': autre_personne_lst,
        }

    @api.multi
    def update_vals_create(self, code):
        vals = {}
        if code == 'E1':
            properties = self.manip_type_evenement1()
            vals.update({
                'fields_eig_id'           : properties['eig'],
                'fields_auteur_id'        : properties['auteur'],
                'fields_victim_id'        : properties['victim'],
                'fields_temoin_id'        : properties['temoin'],
                'fields_info_id'          : properties['infos'],
                'fields_info2_id'         : properties['infos2'],
                'fields_mesures_id'       : properties['mesures'],
                'fields_elements_id'      : properties['elements'],
                'fields_group_id'         : properties['group'],
                'fields_entete_id'        : properties['entete'],
                'fields_autre_personne_id': properties['autre_personne'],
            })
        return vals


class is_type_evenement(models.Model):
    _name = 'is.type.evenement'
    _description = u"Type d’événement"
    _order = "sequence desc"

#     @api.onchange('name')
#     def onchange_name(self):
# #         if self.name:
#             default_obj        = self.env['is.default.type.event']
#             lst_eig            = default_obj.get_fields_eig_properties(True)
#             lst_eig_auteur     = default_obj.get_fields_auteur_properties(True)
#             lst_eig_victim     = default_obj.get_fields_victim_properties(True)
#             lst_eig_temoin     = default_obj.get_fields_temoin_properties(True)
#             lst_eig_infos      = default_obj.get_fields_infos_properties(True)
#             lst_eig_infos2     = default_obj.get_fields_infos2_properties(True)
#             lst_eig_mesures    = default_obj.get_fields_mesures_properties(True)
#             lst_eig_elements   = default_obj.get_fields_elements_properties(True)
#             lst_eig_group      = default_obj.get_fields_group_properties(True)
#             lst_entete_group   = default_obj.get_fields_entete_properties(True)
#             lst_autre_personne = default_obj.get_fields_autre_personne_properties(True)
#             return {'value': {
#                 'fields_eig_id'           : lst_eig,
#                 'fields_auteur_id'        : lst_eig_auteur,
#                 'fields_victim_id'        : lst_eig_victim, 
#                 'fields_temoin_id'        : lst_eig_temoin,
#                 'fields_info_id'          : lst_eig_infos,
#                 'fields_info2_id'         : lst_eig_infos2,
#                 'fields_mesures_id'       : lst_eig_mesures,
#                 'fields_elements_id'      : lst_eig_elements,
#                 'fields_group_id'         : lst_eig_group,
#                 'fields_entete_id'        : lst_entete_group,
#                 'fields_autre_personne_id': lst_autre_personne,
#             }}

    @api.model
    def default_get(self,default_fields):
        res = super(is_type_evenement, self).default_get(default_fields)
        default_obj        = self.env['is.default.type.event']
        res['fields_eig_id']            = default_obj.get_fields_eig_properties(True)
        res['fields_auteur_id']         = default_obj.get_fields_auteur_properties(True)
        res['fields_victim_id']         = default_obj.get_fields_victim_properties(True)
        res['fields_temoin_id']         = default_obj.get_fields_temoin_properties(True)
        res['fields_info_id']           = default_obj.get_fields_infos_properties(True)
        res['fields_info2_id']          = default_obj.get_fields_infos2_properties(True)
        res['fields_mesures_id']        = default_obj.get_fields_mesures_properties(True)
        res['fields_elements_id']       = default_obj.get_fields_elements_properties(True)
        res['fields_group_id']          = default_obj.get_fields_group_properties(True)
        res['fields_entete_id']         = default_obj.get_fields_entete_properties(True)
        res['fields_autre_personne_id'] = default_obj.get_fields_autre_personne_properties(True)
        return res

    @api.model
    def create(self, vals):
        if 'code' in vals and vals['code']:
            value = self.env['is.default.type.event'].update_vals_create(vals['code'])
            vals.update(value)
        add_data_obj = self.env['is.nature.evenement']
        if 'name' in vals and vals['name']:
            if vals['name'] in [u'Situation exceptionnelle pour public d’AMI ou de CHU']:
                type4_list = [
                    u"Actes de malveillance au sein de la structure",
                    u"Autre (évènement relatif à la sécurité des biens et des personnes)",
                    u"Tentative de suicide",
                    u"Violences physiques",
                    u"Violences psychologiques et morales",
                    u"Violences sexuelles",
                    u"Accident corporel grave",
                    u"Autre (évènements relatifs aux victimes présumées)",
                    u"Décès",
                    u"Défaillances techniques graves",
                    u"Epidémie - Propagation de parasites",
                    u"Explosions ou incendie ou inondation",
                    u"Fugues ou disparition de personnes accueillies > à 48 H",
                    u"Intoxication alimentaire si plusieurs personnes sont concernées",
                    u"Négligences graves de l’entourage",
                    u"Racket",
                    u"Trafic au sein de l’établissement",
                    u"Vols récurrents et /ou qualifiés à l’encontre des autres résidents et ou des salariés ou des bénévoles",
                ]
                nature_ids = add_data_obj.search([('name', 'in', type4_list)])
                if nature_ids:
                    vals['is_nature_ids'] = [(6, 0, nature_ids.ids)]
            if vals['name'] in [u'Situation exceptionnelle', u'Information préoccupante', u'Signalement au Procureur']:
                type123_list = [
                    u"Absence imprévue de plusieurs professionnels, mettant en difficulté l’effectivité de l’accompagnement ou la sécurité des personnes accueillies",
                    u"Autre (accident ou incident lié à une erreur ou à un défaut de soin ou de surveillance)",
                    u"Autre (évènement en santé environnementale)",
                    u"Autre (évènement relatif à l’accompagnement des usagers)",
                    u"Autre (évènement relatif au fonctionnement et organisation de l’établissement)",
                    u"Comportements violents de la part d’usagers à l’égard d’autres usagers",
                    u"Comportements violents de la part d’usagers à l’égard de professionnels",
                    u"Conflits sociaux ou menaces de conflits sociaux pouvant entraîner un risque pour l’usager",
                    u"Décès accidentel ou consécutif à un défaut de surveillance ou de prise en charge de la personne",
                    u"Défaillance technique significative et durable",
                    u"Difficultés relationnelles récurrentes avec la famille entraînant une perturbation de l’organisation ou du fonctionnement de la structure",
                    u"Disparition(s) inquiétante(s) de personne(s) accueillie(s) (services de police ou gendarmeries alertés)",
                    u"Epidémie",
                    u"Erreur d’identité dans la délivrance d’un médicament",
                    u"Fugue(s) inquiétante(s) de personne(s) accueillie(s) (services de police ou gendarmeries alertés)",
                    u"Intoxication",
                    u"Intrusion informatique",
                    u"Légionnelles",
                    u"Maladie infectieuse",
                    u"Maltraitances non précisées",
                    u"Manquements graves au règlement du lieu d’hébergement ou d’accueil qui compromettent la prise en charge",
                    u"Mise en danger par dérive sectaire et radicalisation",
                    u"Négligences graves ou erreurs successives",
                    u"Non-respect de la prescription médicale, erreur dans la dispensation, la préparation ou l’administration",
                    u"Présentation de faux diplômes",
                    u"Sinistre ou évènement météorologique exceptionnel",
                    u"Suicide",
                    u"Turn-over du personnel ou grève, mettant en difficulté l’effectivité de l’accompagnement ou la sécurité des personnes accueillies",
                    u"Vacance de poste prolongée, notamment d’encadrement, difficulté de recrutement",
                    u"Violences médicales ou médicamenteuses",
                    u"Vols récurrents à l’encontre des résidents, si dépôt de plainte",
                    u"Actes de malveillance au sein de la structure",
                    u"Autre (évènement relatif à la sécurité des biens et des personnes)",
                    u"Tentative de suicide",
                    u"Violences physiques",
                    u"Violences psychologiques et morales",
                    u"Violences sexuelles",
                ]
                nature_ids = add_data_obj.search([('name', 'in', type123_list)])
                if nature_ids:
                    vals['is_nature_ids'] = [(6, 0, nature_ids.ids)]
            
        return super(is_type_evenement, self).create(vals)

    @api.multi
    def update_one2many_fields(self, object, eig_id, lst_fields):
        field_ids = object.search([('is_eig_id', '=', eig_id)])
        for field_id in field_ids:
            for item in lst_fields:
                field_vsb = str('related_vsb_' + item.fields_id.name)
                field_rqr = str('related_rqr_' + item.fields_id.name)
                field_id.write({field_vsb:False, field_rqr:False})
                vals = {}
                if item.field_visible:
                    field = str('related_vsb_' + item.fields_id.name)
                    vals.update({field: True})
                    if item.field_required:
                        field = str('related_rqr_' + item.fields_id.name)
                        vals.update({field: True})
                if vals:
                    field_id.write(vals)
        return True

    @api.multi
    def write(self, vals):
        res = super(is_type_evenement, self).write(vals)
        """ Mettre à jour les EIG utilisant ce type d'evenement """
        eig_obj = self.env['is.eig']
        for data in self:
            eig_ids = eig_obj.search([('type_event_id','=', data.id)])
            if eig_ids:
                for eig_id in eig_ids:
                    value = eig_id.onchange_type_event_id()
                    eig_id.write(value['value'])
                    auteur_obj = self.env['is.eig.auteur']
                    temoin_obj = self.env['is.eig.temoin']
                    victim_obj = self.env['is.eig.victime']
                    infos_obj = self.env['is.infos.communication']
                    data.update_one2many_fields(auteur_obj, eig_id.id, data.fields_auteur_id)
                    data.update_one2many_fields(temoin_obj, eig_id.id, data.fields_temoin_id)
                    data.update_one2many_fields(victim_obj, eig_id.id, data.fields_victim_id)
                    data.update_one2many_fields(infos_obj,  eig_id.id, data.fields_info_id)
        return res

    name                          = fields.Char('Nom', required=True)
    code                          = fields.Char('Code')
    sequence                      = fields.Integer('Sequence')
    description                   = fields.Text('Description')
    information_speciale          = fields.Text(u'Information spéciale')
    mail_destination_ids          = fields.One2many('is.type.evenement.mail', 'type_evenement_id', 'Mail de destination')
    onglet_faits                  = fields.Boolean(u'Afficher onglet Faits', default=True)
    onglet_auteurs                = fields.Boolean(u'Afficher onglet Auteurs', default=True)
    onglet_temoins                = fields.Boolean(u'Afficher onglet Témoins', default=True)
    onglet_victimes               = fields.Boolean(u'Afficher onglet Victimes', default=True)
    onglet_mesures                = fields.Boolean(u'Afficher onglet Mesures', default=True)
    onglet_infos                  = fields.Boolean(u'Afficher onglet Infos', default=True)
    onglet_element_complementaire = fields.Boolean(u'Afficher onglet Eléments complémentaires', default=True)
    fields_entete_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Entête', domain=[('is_eig_entete', '=', True)])
    fields_eig_id                 = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs EIG', domain=[('is_eig', '=', True)])
    fields_auteur_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Auteur', domain=[('is_eig_auteur', '=', True)])
    fields_victim_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Victime', domain=[('is_eig_victim', '=', True)])
    fields_temoin_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Témoins', domain=[('is_eig_temoin', '=', True)])
    fields_info_id                = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs ', domain=[('is_eig_infos', '=', True)])
    fields_info2_id               = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs ', domain=[('is_eig_infos2', '=', True)])
    fields_mesures_id             = fields.One2many('is.manip.fields', 'type_event_id', u"Caractéristiques des champs Mesures d'accompagnement", domain=[('is_eig_mesures', '=', True)])
    fields_elements_id            = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Eléments complémentaires', domain=[('is_eig_elements', '=', True)])
    fields_group_id               = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Eléments Group', domain=[('is_eig_group', '=', True)])
    fields_autre_personne_id      = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Autre(s) personne(s) concernée(s)', domain=[('is_eig_autre_personne', '=', True)])
    is_nature_ids                 = fields.Many2many('is.nature.evenement', 'type_evenement_nature_rel', 'type_event_id', 'nature_id', u"Nature d'événement")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le Type d'évènement doit être unique !"),
    ]


class res_company(models.Model):
    _inherit = 'res.company'

    attachment_ids = fields.Many2many('ir.attachment', 'company_attach_rel', 'res_id', 'attachment_id', string='Files')


class is_trame(models.Model):
    _name = 'is.trame'
    _description = 'Trame'

    name = fields.Char(string='Nom de la trame', required=True)
    attachment_ids = fields.Many2many('ir.attachment', string=u"Modèle ODT", required=True)

