# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        #TODO : Cela permet de désactiver l'envoi du mail d'invitation lors de la création d'un utilisateur
        user = super(ResUsers, self.with_context(no_reset_password=True)).create(vals)
        return user
