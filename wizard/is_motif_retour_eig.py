# -*- coding: utf-8 -*-


from odoo import api, exceptions, fields, models, _


class is_motif_retour_redaction_eig(models.TransientModel):
    _name = 'is.motif.retour.redaction.eig'
    _description = u"Motif de retour à l'étape rédaction d'un EIG"

    date = fields.Datetime('Date/Heure', required=True, readonly=True, default=lambda self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', 'Utilisateur', required=True, readonly=True, default=lambda self: self.env.uid)
    operation = fields.Char(u'Opération', readonly=True)
    operation_id = fields.Char(u'Opération Id', readonly=True)
    motif = fields.Text('Motif de retour', required=True)

    @api.model
    def default_get(self, fields):
        context = self._context
        context = context or {}
        res = super(is_motif_retour_redaction_eig, self).default_get(fields)
        operation_id = context["operation_id"]
        res["operation_id"] = operation_id
        if operation_id == "retour_redaction":
            res["operation"] = "retour_redaction"
        if operation_id == "retour_completer":
            res["operation"] = "retour_completer"
        return res

    @api.multi
    def valider_reponse(self):
        eig_obj = self.env['is.eig']
        is_motif_obj = self.env['is.motif.retour.eig']
        for eig in eig_obj.browse(self._context.get('active_ids')):
            is_motif_obj.create({
                'date': self.date,
                'user_id': self.user_id.id,
                'action': self.operation,
                'description': self.motif,
                'eig_id1': eig.id
            })
            if self.operation_id == "retour_redaction":
                eig.write({'state': 'draft', 'related_group_motif_retour': True})
                template_id = self.env.ref('is_eig12.email_template_redige_vers_redaction', False)
            if self.operation_id == "retour_completer":
                eig.write({'state': 'complet', 'related_group_motif_retour': True})
                template_id = self.env.ref('is_eig12.email_template_valide_vers_a_completer', False)
            if template_id:
                template_id.send_mail(eig.id, force_send=True, raise_exception=True)

