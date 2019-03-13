# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError

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


class is_type_evenement_mail(models.Model):
    _name = 'is.type.evenement.mail'
    _description = 'is.type.evenement.mail'

    autorite_controle = fields.Selection(AutoriteControle  , u'Autorité de Contrôle')
    mail_destination  = fields.Selection(AutoriteControle  , u'Mail de destination du département')
    type_evenement_id = fields.Many2one('is.type.evenement', u'Type d’événement')


class is_manip_fields(models.Model):
    _name = 'is.manip.fields'
    _description = u"Caractéristiques des champs"

    fields_id       = fields.Many2one('ir.model.fields', 'Champs', ondelete='cascade', required=True)
    field_visible   = fields.Boolean('Visible')
    field_required  = fields.Boolean('Obligatoire')
    type_event_id   = fields.Many2one('is.type.evenement', 'Type evenement')
    is_eig          = fields.Boolean('EIG', default=False)
    is_eig_auteur   = fields.Boolean('Auteur', default=False)
    is_eig_temoin   = fields.Boolean('Temoin', default=False)
    is_eig_victim   = fields.Boolean('Victim', default=False)
    is_eig_infos    = fields.Boolean('Infos', default=False)


class is_nature_evenement(models.Model):
    _name = 'is.nature.evenement'
    _description = u"Nature d'événement"

    name = fields.Char('Nature', required=True)


class is_type_risque(models.Model):
    _name = 'is.type.risque'
    _description = "Type de risque"

    name = fields.Char('Type', required=True)


class is_nature_risque(models.Model):
    _name = 'is.nature.risque'
    _description = "Nature de risque"

    name = fields.Char('Nature', required=True)


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


class is_eig(models.Model):
    _name = 'is.eig'
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
                'related_vsb_nature_precision':  False,
                'related_rqr_nature_precision':  False,
                'related_vsb_start_date':  False,
                'related_rqr_start_date':  False,
                'related_vsb_end_date':  False,
                'related_vsb_description_faits':  False,
                'related_rqr_description_faits':  False,
                'related_vsb_risque_reproductivite':  False,
                'related_rqr_risque_reproductivite':  False,
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
        for o in obj.read(data_ids, ['res_id', 'name']):
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
            if not doc.type_risq_id:
                raise UserError(_("Champ 'Type de risque' obligatoire !"))
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
    nature_event_id                       = fields.Many2one('is.nature.evenement', u"Nature d'événement", required=True, help=u"Préciser le type d'événement à déclarer.")
    nature_precision                      = fields.Char('Précision nature évènement')
    related_vsb_nature_precision          = fields.Boolean(u'Champs related_vsb_nature_precision - Visibilité')
    related_rqr_nature_precision          = fields.Boolean(u'Champs related_rqr_nature_precision - Obligation')
    type_risq_id                          = fields.Many2one('is.type.risque', "Type de risque", required=False, help=u"Permet de préciser sur quel temps du parcours de l'usager est apparu l'EIG.")
    nature_risq_id                        = fields.Many2one('is.nature.risque', "Nature de risque", required=True, help=u"Permet d'identifier la nature du risque afin d'alimenter la cartographie des risques de la fondation OVE")
    signalement_autorites                 = fields.Boolean(u'Signalement aux autorités judiciaires')
    start_date                            = fields.Datetime(u'Date heure de début', help=u"Date connue de début de l'événement. En cas de maladie il s'agit de la date connue de déclaration des symptômes chez le premier malade.")
    related_vsb_start_date                = fields.Boolean(u'Champs related_vsb_start_date - Visibilité')
    related_rqr_start_date                = fields.Boolean(u'Champs related_rqr_start_date - Obligation')
    end_date                              = fields.Datetime('Date heure de fin', help=u"Date connue de fin de l'événement. En cas de maladie il s'agit de la date connue de déclaration des symptômes chez le dernier malade.")
    related_vsb_end_date                  = fields.Boolean(u'Champs related_vsb_end_date - Visibilité')
    related_rqr_end_date                  = fields.Boolean(u'Champs related_rqr_end_date - Obligation')
    description_faits                     = fields.Text('Description des faits', help=u"Permet de décrire de manière exhaustive et détaillée les faits survenus dans votre établissement. En cas de maladie il est nécessaire de préciser de quelle maladie ou contamination il s'agit en l'espèce.")
    related_vsb_description_faits         = fields.Boolean(u'Champs related_vsb_description_faits - Visibilité')
    related_rqr_description_faits         = fields.Boolean(u'Champs related_rqr_description_faits - Obligation')
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
    si_non_maitrise                       = fields.Text("Si non maîtrisé, précisez pourquoi")
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
    causes_profondes                      = fields.Selection(OuiNon, "Une recherche des causes profondes est-elle prévue le cas échéant")
    related_vsb_causes_profondes          = fields.Boolean(u'Champs related_vsb_causes_profondes - Visibilité')
    related_rqr_causes_profondes          = fields.Boolean(u'Champs related_rqr_causes_profondes - Obligation')
    si_causes_profondes                   = fields.Text("Si oui, quelle est la méthodologie utilisée")
    related_vsb_si_causes_profondes       = fields.Boolean(u'Champs related_vsb_si_causes_profondes - Visibilité')
    related_rqr_si_causes_profondes       = fields.Boolean(u'Champs related_rqr_si_causes_profondes - Obligation')
    enseignements_a_tirer                 = fields.Selection(OuiNon, "Enseignements à tirer", help="Y a-t-il des enseignements à tirer au niveau de l’établissement, ou au niveau régional, de l’événement pour prévenir sa reproduction")
    related_vsb_enseignements_a_tirer     = fields.Boolean(u'Champs related_vsb_enseignements_a_tirer - Visibilité')
    related_rqr_enseignements_a_tirer     = fields.Boolean(u'Champs related_rqr_enseignements_a_tirer - Obligation')
    si_enseignements_a_tirer              = fields.Text("Si oui, lesquels")
    related_vsb_si_enseignements_a_tirer  = fields.Boolean(u'Champs related_vsb_si_enseignements_a_tirer - Visibilité')
    related_rqr_si_enseignements_a_tirer  = fields.Boolean(u'Champs related_rqr_si_enseignements_a_tirer - Obligation')
    mesure_organisation                   = fields.Text('Organisationnelles', help=u"Permet d'indiquer les mesures prises au niveau du fonctionnement de l'établissement pour répondre à cet EIG")
    related_vsb_mesure_organisation       = fields.Boolean(u'Champs related_vsb_mesure_organisation - Visibilité')
    related_rqr_mesure_organisation       = fields.Boolean(u'Champs related_rqr_mesure_organisation - Obligation')
    mesure_personnel                      = fields.Text(u'Personnel établissement', help=u"Permet d'indiquer les mesures prises (accompagnement, dialogue interne, disciplinaires...) à l'égard d'un ou de plusieurs membres du personnel suite à la déclaration de cet EIG.")
    related_vsb_mesure_personnel          = fields.Boolean(u'Champs related_vsb_mesure_personnel - Visibilité')
    related_rqr_mesure_personnel          = fields.Boolean(u'Champs related_rqr_mesure_personnel - Obligation')
    mesure_usagers                        = fields.Text('Autres usagers', help=u"Permet d'indiquer les mesures prises à l'égard des usagers non directement touchés par cet EIG")
    related_vsb_mesure_usagers            = fields.Boolean(u'Champs related_vsb_mesure_usagers - Visibilité')
    related_rqr_mesure_usagers            = fields.Boolean(u'Champs related_rqr_mesure_usagers - Obligation')
    mesure_autres                         = fields.Text('Autres', help=u"Permet d'indiquer les mesures prises à l'égard des autres personnes potentiellement impliquées (famille, professionnels extérieurs, structure partenaire...) suite à la déclaration de cet EIG.")
    related_vsb_mesure_autres             = fields.Boolean(u'Champs related_vsb_mesure_autres - Visibilité')
    related_rqr_mesure_autres             = fields.Boolean(u'Champs related_rqr_mesure_autres - Obligation')
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
    depot_plainte                         = fields.Selection(OuiNon, "Dépôt de plainte par la famille")
    related_vsb_depot_plainte             = fields.Boolean(u'Champs related_vsb_depot_plainte - Visibilité')
    related_rqr_depot_plainte             = fields.Boolean(u'Champs related_rqr_depot_plainte - Obligation')
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


class is_default_type_event(models.Model):
    _name = 'is.default.type.event'
    _description = "Event Default Type"

    @api.multi
    def get_eig_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig'),
            ('name', 'in', ['start_date', 'end_date', 'nature_precision', 'description_faits',
                           'lieu_faits', 'element_faits', 'cause_faits', 'mesure_organisation',
                           'mesure_personnel', 'mesure_usagers', 'mesure_autres', 'note', 'attachment_ids',
            ])])
        return field_ids

    @api.multi
    def get_fields_eig_properties(self, visible=False):
        field_ids = self.get_eig_fields()
        lst = []
        for field_id in field_ids:
            lst.append({
                'fields_id': field_id,
                'field_visible': visible,
                'field_required': False,
                'is_eig': True
            })
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
        for field_id in field_ids:
            lst.append({
                'fields_id': field_id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_auteur': True
            })
        return lst

    @api.multi
    def get_victim_fields(self):
        field_obj = self.env['ir.model.fields']
        field_ids = field_obj.search([
            ('model', '=', 'is.eig.victime'),
            ('name','in', ('identifie','name','prenom','address','ecole','birthdate','sexe_id',
                           'qualite_id','disposition_id','consequence_id','nom_pere','prenom_pere',
                            'address_pere','nom_mere','prenom_mere','address_mere',
            ))])
        return field_ids

    @api.multi
    def get_fields_victim_properties(self, visible=False):
        field_ids = self.get_victim_fields()
        lst = []
        for field_id in field_ids:
            lst.append({
                'fields_id': field_id,
                'field_visible': visible,
                'field_required': False, 
                'is_eig_victim': True
            })
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
        for field_id in field_ids:
            lst.append({
                'fields_id': field_id,
                'field_visible': visible,
                'field_required': False,
                'is_eig_temoin': True
            })
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
            lst.append({'fields_id': field_id, 'field_visible': visible, 'field_required': False, 'is_eig_infos': True})
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
            if field.name == 'mesure_organisation':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_personnel':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_usagers':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'mesure_autres':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': False, 'field_required': False, 'is_eig': True}])
            if field.name == 'note':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
            if field.name == 'attachment_ids':
                eig_lst.append([0,False, {'fields_id': field.id, 'field_visible': True, 'field_required': True, 'is_eig': True}])
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
        return {'eig': eig_lst, 'auteur': auteur_lst, 'temoin': temoin_lst, 'victim': victim_lst, 'infos': infos_lst}

    @api.multi
    def update_vals_create(self, code):
        vals = {}
        if code == 'E1':
            properties = self.manip_type_evenement1()
            vals.update({
                'fields_eig_id': properties['eig'],
                'fields_auteur_id': properties['auteur'],
                'fields_victim_id': properties['victim'],
                'fields_temoin_id': properties['temoin'],
                'fields_info_id': properties['infos']
            })
            return vals


class is_type_evenement(models.Model):
    _name = 'is.type.evenement'
    _description = u"Type d’événement"

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            default_obj    = self.env['is.default.type.event']
            lst_eig        = default_obj.get_fields_eig_properties(True)
            lst_eig_auteur = default_obj.get_fields_auteur_properties(True)
            lst_eig_victim = default_obj.get_fields_victim_properties(True)
            lst_eig_temoin = default_obj.get_fields_temoin_properties(True)
            lst_eig_infos  = default_obj.get_fields_infos_properties(True)
            return {'value': {
                'fields_eig_id': lst_eig,
                'fields_auteur_id': lst_eig_auteur,
                'fields_victim_id': lst_eig_victim, 
                'fields_temoin_id': lst_eig_temoin,
                'fields_info_id': lst_eig_infos
            }}

    @api.model
    def create(self, vals):
        if 'code' in vals and vals['code']:
            value = self.env['is_default_type_event'].update_vals_create(vals['code'])
            vals.update(value)
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

    code                          = fields.Char('Code')
    name                          = fields.Char('Nom', required=True)
    mail_destination_ids          = fields.One2many('is.type.evenement.mail', 'type_evenement_id', 'Mail de destination')
    onglet_faits                  = fields.Boolean(u'Afficher onglet Faits')
    onglet_auteurs                = fields.Boolean(u'Afficher onglet Auteurs')
    onglet_temoins                = fields.Boolean(u'Afficher onglet Témoins')
    onglet_victimes               = fields.Boolean(u'Afficher onglet Victimes')
    onglet_mesures                = fields.Boolean(u'Afficher onglet Mesures')
    onglet_infos                  = fields.Boolean(u'Afficher onglet Infos')
    onglet_element_complementaire = fields.Boolean(u'Afficher onglet Eléments complémentaires')
    fields_eig_id                 = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs EIG', domain=[('is_eig', '=', True)])
    fields_auteur_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Auteur', domain=[('is_eig_auteur', '=', True)])
    fields_victim_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Victime', domain=[('is_eig_victim', '=', True)])
    fields_temoin_id              = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs Témoins', domain=[('is_eig_temoin', '=', True)])
    fields_info_id                = fields.One2many('is.manip.fields', 'type_event_id', u'Caractéristiques des champs ', domain=[('is_eig_infos', '=', True)])

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le Type d'évènement doit être unique !"),
    ]

