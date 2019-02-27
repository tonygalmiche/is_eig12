# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class is_motif_retour(models.TransientModel):
    _name = 'is.motif.retour'
    _description = u"Motif de retour à l'étape rédaction"

    date= fields.Datetime(string='Date/Heure', readonly=True, required=True, default=lambda self: fields.Datetime.now())
    user_id= fields.Many2one('res.users', string='Utilisateur', required=True, readonly=True, default=lambda self: self.env.uid)
    motif= fields.Text('Motif de retour', required=True)

    @api.multi
    def valider_reponse(self):
        ei_obj = self.env['is.ei']
        is_motif_obj = self.env['is.motif.retour.ei']
        for data in ei_obj.browse(self._context.get('active_ids')):
            is_motif_obj.create({'date': self.date,
                                          'user_id': self.user_id.id,
                                          'description': self.motif,
                                          'ei_id1': data.id})
            data.write({'state': 'draft'})
            template = self.env.ref('is_eig12.email_template_ei_vers_redaction', False)
            if template:
                template.send_mail(data.id, force_send=True, raise_exception=True)
        return True

