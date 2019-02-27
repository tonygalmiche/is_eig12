# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class is_ei(models.Model):
    _name = 'is.ei'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u"Gestion des Événements Indésirables"
    _order = "name desc"

    name                    = fields.Char('N°')
    etablissement_id        = fields.Many2one('is.etablissement', u'Établissement', required=True)
    redacteur_id            = fields.Many2one('res.users', u'Rédacteur', readonly=True, required=True, default=lambda self: self.env.uid)
    valideur_id             = fields.Many2one('res.users', 'Valideur')
    type_event_id           = fields.Many2one('is.type.evenement.ei', u"Type d'événement", required=True)
    nature_event_id         = fields.Many2one('is.nature.evenement.ei', u"Nature d'événement", required=True)
    date_faits              = fields.Datetime('Date/heure', required=True)
    date_constatation_faits = fields.Datetime('Date / Heure de la constatation des faits')
    description_faits       = fields.Text('Description des faits', required=True)
    evenement_survenu       = fields.Selection([('oui', 'Oui'),
                              ('non', 'non or ne sait')], u'Evénement déjà survenu')
    consequences            = fields.Text(u'Conséquences')
    consequence_faits       = fields.Text('Conséquences', required=True)
    lieu_faits              = fields.Char('Lieu', required=True)
    victime_ids             = fields.One2many('is.victime.ei', 'ei_id', 'Victime')
    mesure_immediat         = fields.Text(u'Mesures immédiates', required=True)
    mesure_amelioration     = fields.Text(u"mesures d'amélioration éventuelles", required=True)
    mesure_autre            = fields.Text('Autres', required=True)
#     info_date = fields.Datetime('Date/heure')
#     destinataire_id = fields.Many2one('is.destinataire', 'Destinataire', required=True)
#     auteur_id = fields.Many2one('res.users', 'Auteur (responsable de la diffusion)')
    attachment_ids          = fields.Many2many('ir.attachment', 'is_ei_attachment_rel', 'ei_id', 'attachment_id', u'Pièces jointes')
    motif_ids               = fields.One2many('is.motif.retour.ei', 'ei_id1', 'Motif de retour', readonly=True)
    state                   = fields.Selection([('draft', u'Rédaction'),
                              ('redige', u'Rédigé'),
                              ('valide', u'Validé')], u'État', default='draft', readonly=True, select=True)
    pour_proteger           = fields.Text(u'Pour protéger, accompagner ou soutenir les personnes victimes ou exposées')
    pour_assurer            = fields.Text(u'Pour assurer la continuité de la prise en charge, le cas échéant')
    legard                  = fields.Text(u'A l’égard des autres personnes prises en charge ou du personnel, le cas échéant (par exemple : information à l’ensemble des usagers, soutien psychologique...)')
    autre_preciser          = fields.Text(u'Autre (à préciser)')
    proposition             = fields.Text(u'Proposition d’actions d’amélioration')
    une_recherche           = fields.Selection([('oui', 'Oui'),
                                      ('non', 'Non')], u'Une recherche des causes profondes a-t-elle été réalisée ou est-elle prévue ?')
    cause_identifiee        = fields.Text(u'Cause(s) identifiée(s)')
    concernant_les          = fields.Text(u'Concernant les usagers ou les résidents ')
    concernant_personnel    = fields.Text('Concernant le personnel')
    concernant_travail      = fields.Text(u'Concernant l’organisation du travail')
    concernant_structure    = fields.Text('Concernant la structure ')
    


    @api.multi
    def get_signup_url(self):
        url = False
        for data in self:
            url = "https://eig.fondation-ove.fr/web#id=" + str(data.id) + "&view_type=form&model=is.ei"
        return url

    @api.onchange('etablissement_id')
    def onchange_etablissement_id(self):
        if self.etablissement_id:
            self.valideur_id = self.etablissement_id.director_id and self.etablissement_id.director_id.id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ei.number') or ''
        if 'etablissement_id' in vals and vals['etablissement_id']:
#             res = self.get_valideur_traiteurs(vals['etablissement_id'])
            etablissement_obj = self.env['is.etablissement']
            etablissement = etablissement_obj.browse(vals['etablissement_id'])
            vals.update({'valideur_id': etablissement.director_id and etablissement.director_id.id or False})
        return super(is_ei, self).create(vals)

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default.update({
            'redacteur_id': self._uid,
        })
        return super(is_ei, self).copy(default)

    @api.multi
    def action_rediger_ei(self):
        for data in self:
            data.write({'state': 'redige'})
            template = self.env.ref('is_eig12.email_template_ei_vers_redige', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)

    @api.multi
    def action_valider_eig(self):
        """ transaction de redigé vers validé """
        for data in self:
            data.write({'state': 'valide'})
            template = self.env.ref('is_eig12.email_template_ei_vers_valide', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)

    @api.multi
    def action_rediger_eig(self):
        """ transaction de validé vers redigé """
        for data in self:
            data.write({'state': 'redige'})

    @api.multi
    def action_send_manual_ei(self):
        """ Envoi manuel d'email """
        return self.action_ei_manual_send('is_eig12.email_template_edi_is_ei')

    @api.multi
    def action_ei_manual_send(self, email_template):
        '''
        This function opens a window to compose an email
        '''
        template_id = False
        try:
            template_id = self.env.ref(email_template, False)
        except ValueError:
            template_id = False
        try:
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form', False)
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        if template_id:
            template_id = template_id.id
        else:
            template_id = False
        ctx.update({
            'default_model': 'is.ei',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
             'type': 'ir.actions.act_window',
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'mail.compose.message',
             'views': [(compose_form_id.id, 'form')],
             'view_id': compose_form_id.id,
             'target': 'new',
             'context': ctx,
         }


class is_type_evenement_ei(models.Model):
    _name = 'is.type.evenement.ei'
    _description = u"Type d'évènement"

    name = fields.Char(u"Type d'évènement", required=True)


class is_nature_evenement_ei(models.Model):
    _name = 'is.nature.evenement.ei'
    _description = u"Nature d'évènement"

    name = fields.Char(u"Nature d'évènement", required=True)


class is_qualite(models.Model):
    _name = 'is.qualite'
    _description = u'Qualité'

    name = fields.Char(u'Qualité', required=True)


class is_sexe(models.Model):
    _name = 'is.sexe'
    _description = 'Sexe'

    name = fields.Char('Sexe', required=True)


class is_victime_ei(models.Model):
    _name = 'is.victime.ei'
    _description = 'Victime'

    name           = fields.Char('Nom')
    prenom         = fields.Char(u'Prénom')
    date_naissance = fields.Date('Date de naissance')
    qualite_id     = fields.Many2one('is.qualite', u'Qualité')
    sexe_id        = fields.Many2one('is.sexe', 'Sexe')
    ei_id          = fields.Many2one('is.ei', 'EI', readonly=True)


class is_motif_retour_ei(models.Model):
    _name = 'is.motif.retour.ei'
    _description = u"Motifs de retour à l'étape Rédigé"

    date        = fields.Datetime('Date/Heure')
    user_id     = fields.Many2one('res.users', 'Auteur')
    description = fields.Text('Motif')
    ei_id1      = fields.Many2one('is.ei', 'EI', readonly=True)


# class is_destinataire (models.Model):
#     _name = 'is.destinataire'
#     _description = u"Destinataire"
# 
#     name = fields.Char('Nom' , required=True)
# 
#     _sql_constraints = [
#         ('name_uniq', 'unique(name)', u"Le nom doit être unique !"),
#     ]

