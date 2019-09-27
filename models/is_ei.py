# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _, SUPERUSER_ID

class is_ei(models.Model):
    _name = 'is.ei'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = u"Événements Indésirables"
    _order = "name desc"

    name                    = fields.Char('N°')
    etablissement_id        = fields.Many2one('is.etablissement', u'Établissement', required=True)
    redacteur_id            = fields.Many2one('res.users', u'Rédacteur', readonly=True, required=True, default=lambda self: self.env.uid)
    valideur_id             = fields.Many2one('res.users', 'Valideur', compute='_valideur_id', readonly=True, store=True)
    #type_event_id           = fields.Many2one('is.type.evenement.ei', u"Type d'événement", required=True)
    nature_event_id         = fields.Many2one('is.nature.evenement.ei', u"Nature d'événement", required=True)
    date_faits              = fields.Datetime('Date/heure', required=True)
    date_constatation_faits = fields.Datetime('Date / Heure de la constatation des faits')
    description_faits       = fields.Text('Description des faits', required=True)
    evenement_survenu       = fields.Selection([
            ('oui', 'oui'),
            ('non', 'non'),
            ('ne_sait_pas', 'ne sait pas')], u'Evénement déjà survenu')
    consequences            = fields.Text(u'Conséquences')
#    consequence_faits       = fields.Text(u'Conséquences Faits', required=True)
    lieu_faits              = fields.Char('Lieu', required=True)
    victime_ids             = fields.One2many('is.victime.ei', 'ei_id', 'Victime')
#    mesure_immediat         = fields.Text(u'Mesures immédiates', required=True)
#    mesure_amelioration     = fields.Text(u"mesures d'amélioration éventuelles", required=True)
#    mesure_autre            = fields.Text('Autres', required=True)
#     info_date = fields.Datetime('Date/heure')
#     destinataire_id = fields.Many2one('is.destinataire', 'Destinataire', required=True)
#     auteur_id = fields.Many2one('res.users', 'Auteur (responsable de la diffusion)')
    attachment_ids          = fields.Many2many('ir.attachment', 'is_ei_attachment_rel', 'ei_id', 'attachment_id', u'Pièces jointes')
    motif_ids               = fields.One2many('is.motif.retour.ei', 'ei_id1', 'Motif de retour', readonly=True)
    state                   = fields.Selection([
                                ('draft', u'Rédaction'),
                                ('redige', u'Rédigé'),
                                ('valide', u'Validé'),
                                ('eig', u'EIG'),
                            ], u'État', default='draft', readonly=True)
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
    
    btn_redaction_ei        = fields.Boolean('Bouton vers Rédaction'   , compute='_btn_redaction_ei')
    btn_valider_ei          = fields.Boolean('Bouton vers Valider'     , compute='_btn_valider_ei')
    btn_rediger_ei          = fields.Boolean('Bouton vers Rédiger'     , compute='_btn_rediger_ei')
    btn_send_mail_ei        = fields.Boolean('Bouton envoyer mail'     , compute='_btn_send_mail_ei')
    btn_convertir_en_eig    = fields.Boolean('Bouton convertir en EIG' , compute='_btn_convertir_en_eig')
    partner_id              = fields.Many2one('res.partner', u'Partner', compute='_partner_id')
    eig_id                  = fields.Many2one('is.eig', u'EIG', readonly=True)


    @api.multi
    def liste_mails(self, subject):
        for obj in self:
            return {
                'name': "Historique des mails",
                'view_mode': 'tree,form',
                'view_type': 'form',
                'res_model': 'mail.mail',
                'type': 'ir.actions.act_window',
                'domain': [
                    ('model' ,'=','is.ei'),
                    ('res_id','=',obj.id),
                ],
            }


    @api.depends('etablissement_id')
    def _valideur_id(self):
        for obj in self:
            obj.valideur_id = obj.etablissement_id.responsible_id.id


    @api.depends('redacteur_id')
    def _partner_id(self):
        for obj in self:
            obj.partner_id=obj.redacteur_id.partner_id


    @api.multi
    def get_responsable_ids(self):
        for obj in self:
            responsable_ids=[]
            for responsable in obj.etablissement_id.responsable_ids:
                responsable_ids.append(responsable.id)
            return responsable_ids


    @api.depends('state','etablissement_id','redacteur_id')
    def _btn_redaction_ei(self):
        for obj in self:
            r = False
            responsable_ids=self.get_responsable_ids()
            if obj.state == "redige":
                if self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_gestionnaire_ei') \
                    or self.env.user.has_group('is_eig12.group_is_directeur') \
                    or self._uid == obj.etablissement_id.director_id.id \
                    or self._uid == obj.etablissement_id.responsible_id.id \
                    or self._uid in responsable_ids:
                    r = True
            obj.btn_redaction_ei = r

    @api.depends('state','etablissement_id','redacteur_id')
    def _btn_valider_ei(self):
        for obj in self:
            r = False
            responsable_ids=self.get_responsable_ids()
            if obj.state == "redige":
                if self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_gestionnaire_ei') \
                    or self.env.user.has_group('is_eig12.group_is_directeur') \
                    or self._uid == obj.etablissement_id.director_id.id \
                    or self._uid == obj.etablissement_id.responsible_id.id \
                    or self._uid in responsable_ids:
                    r = True
            obj.btn_valider_ei = r

    @api.depends('state','etablissement_id','redacteur_id')
    def _btn_rediger_ei(self):
        for obj in self:
            r = False
            responsable_ids=self.get_responsable_ids()
            if obj.state == "valide":
                if self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_gestionnaire_ei') \
                    or self.env.user.has_group('is_eig12.group_is_directeur') \
                    or self._uid == obj.etablissement_id.director_id.id \
                    or self._uid == obj.etablissement_id.responsible_id.id \
                    or self._uid in responsable_ids:
                    r = True
            obj.btn_rediger_ei = r

    @api.depends('state','etablissement_id','redacteur_id')
    def _btn_send_mail_ei(self):
        for obj in self:
            r = False
            responsable_ids=self.get_responsable_ids()
            if obj.state == "draft":
                if self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_gestionnaire_ei') \
                    or self.env.user.has_group('is_eig12.group_is_directeur') \
                    or self._uid == obj.etablissement_id.director_id.id \
                    or self._uid == obj.etablissement_id.responsible_id.id \
                    or self._uid in responsable_ids:
                    r = True
            obj.btn_send_mail_ei = r


    @api.depends('state','etablissement_id','redacteur_id')
    def _btn_convertir_en_eig(self):
        for obj in self:
            r = False
            responsable_ids=self.get_responsable_ids()
            if obj.state == "redige" or obj.state == "valide":
                if self._uid == SUPERUSER_ID \
                    or self.env.user.has_group('is_eig12.group_is_gestionnaire_ei') \
                    or self.env.user.has_group('is_eig12.group_is_directeur') \
                    or self._uid == obj.etablissement_id.director_id.id \
                    or self._uid == obj.etablissement_id.responsible_id.id \
                    or self._uid in responsable_ids:
                    r = True
            obj.btn_convertir_en_eig = r


    @api.multi
    def action_convertir_en_eig(self):
        for obj in self:
            attachment_ids=[]
            for attachment in obj.attachment_ids:
                attachment_ids.append(attachment.id)
            type_event = self.env['is.type.evenement'].search([('code', '=', 'IP')])[0]
            vals={
                'start_date'                   : obj.date_faits,
                'date_heure_constatation_faits': obj.date_constatation_faits,
                'lieu_faits'                   : obj.lieu_faits,
                'description_faits'            : obj.description_faits,
                'causes_profondes'             : obj.une_recherche,
                'attachment_ids'               : [(6,0,attachment_ids)],
                'etablissement_id'             : obj.etablissement_id.id,
                'redacteur_id'                 : obj.redacteur_id.id,
                'valideur_id'                  : obj.valideur_id.id,
                'type_event_id'                : type_event.id,
                'ei_id'                        : obj.id,

            }
            eig=self.env['is.eig'].create(vals)
            vals=eig.onchange_type_event_id()
            if 'value' in vals:
                eig.write(vals['value'])
            obj.eig_id = eig.id
            template = self.env.ref('is_eig12.email_template_ei_vers_eig', False)
            if template:
                template.send_mail(obj.id, force_send=True, raise_exception=True)
            self.creer_notification(u'vers EIG')
            obj.state='eig'
            return {
                'name': "EIG",
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_model': 'is.eig',
                'type': 'ir.actions.act_window',
                'res_id': eig.id,
            }



    @api.multi
    def get_signup_url(self):
        url = False
        for data in self:
            url = "https://eig.fondation-ove.fr/web#id=" + str(data.id) + "&view_type=form&model=is.ei"
        return url

    #@api.onchange('etablissement_id')
    #def onchange_etablissement_id(self):
    #    if self.etablissement_id:
    #        self.valideur_id = self.etablissement_id.responsible_id and self.etablissement_id.responsible_id.id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ei.number') or ''
        if 'etablissement_id' in vals and vals['etablissement_id']:
#             res = self.get_valideur_traiteurs(vals['etablissement_id'])
            etablissement_obj = self.env['is.etablissement']
            etablissement = etablissement_obj.browse(vals['etablissement_id'])
            #vals.update({'valideur_id': etablissement.responsible_id and etablissement.responsible_id.id or False})
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
    def creer_notification(self, subject):
        for obj in self:
            vals={
                'subject'       : subject,
                'body'          : subject, 
                'body_html'     : subject, 
                'model'         : self._name,
                'res_id'        : obj.id,
                'notification'  : True,
                'message_type'  : 'comment',
                'state'         : 'sent',
            }
            email=self.env['mail.mail'].create(vals)



    @api.multi
    def get_directeur_autre(self):
        mails=[]
        for obj in self:
            mails.append(obj.etablissement_id.director_id.email)
            for line in obj.etablissement_id.responsable_ids:
                if line.email:
                    mails.append(line.email)
        mail=','.join(mails)
        return mail



    @api.multi
    def get_directeur_responsable_autre(self):
        mails=[]
        for obj in self:
            mails.append(obj.etablissement_id.director_id.email)
            mails.append(obj.etablissement_id.responsible_id.email)
            for line in obj.etablissement_id.responsable_ids:
                if line.email:
                    mails.append(line.email)
        mail=','.join(mails)
        return mail


    @api.multi
    def action_rediger_ei(self):
        for data in self:
            data.write({'state': 'redige'})
            template = self.env.ref('is_eig12.email_template_ei_vers_redige', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)
            self.creer_notification(u'de Rédaction vers Rédigé')

    @api.multi
    def action_valider_ei(self):
        """ transaction de redigé vers validé """
        for data in self:
            template = self.env.ref('is_eig12.email_template_ei_vers_valide', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)
            self.creer_notification(u'de Redigé vers Validé')
            data.write({'state': 'valide'})


#    @api.multi
#    def action_rediger_ei(self):
#        """ transaction de validé vers redigé """
#        for data in self:
#            data.sudo().write({'state': 'redige'})
#            self.creer_notification(u'de Validé vers Redigé')

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


#class is_type_evenement_ei(models.Model):
#    _name = 'is.type.evenement.ei'
#    _description = u"Type d'évènement"

#    name = fields.Char(u"Type d'évènement", required=True)


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

