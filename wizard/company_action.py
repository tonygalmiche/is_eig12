# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class add_is_criteres_generaux(models.TransientModel):
    _name = 'add.is.criteres.generaux'
    _description = u"Initialisation Critères généraux"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.criteres.generaux']
        add_list = [
            u'Evènement inhabituel par sa nature, son ampleur ou sa gravité',
            u'Evènement ayant pour conséquence une exclusion temporaire ou définitive',
            u'Evènement ayant pour conséquence une sanction disciplinaire grave ou une procédure judiciaire à l’encontre de personnels',
            u'Evènement nécessitant l’activation du Plan Bleu',
            u'Evènement nécessitant l’activation d’une CUMP',
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data)])
            if not generaux_ids:
                add_data_obj.create({'name': data})
        return True


class add_is_demande_intervention_secours(models.TransientModel):
    _name = 'add.is.demande.intervention.secours'
    _description = u"Initialisation Demande d’intervention des secours"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.demande.intervention.secours']
        add_list = [
            'Pompiers',
            'SAMU',
            'Police',
            'Gendarmerie',
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data)])
            if not generaux_ids:
                add_data_obj.create({'name': data})
        return True


class add_is_consequence_personne_prise_en_charge(models.TransientModel):
    _name = 'add.is.consequence.personne.prise.en.charge'
    _description = u"Initialisation Conséquence pour la personne prises en charge"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.consequence.personne.prise.en.charge']
        add_list = [
            u'décès',
            'mise en jeu du pronostic vital',
            u'probable déficit fonctionnel permanent',
            'soins internes',
            'hospitalisation',
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data)])
            if not generaux_ids:
                add_data_obj.create({'name': data})
        return True


class add_is_consequence_personnel(models.TransientModel):
    _name = 'add.is.consequence.personnel'
    _description = u"Initialisation Conséquence pour le personnel"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.consequence.personnel']
        add_list = [
            'interruption temporaire de travail',
            u'réquisition',
            'autre (y compris suicide ou tentative de suicide)',
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data)])
            if not generaux_ids:
                add_data_obj.create({'name': data})
        return True


class add_is_consequence_fonctionnement_stucture(models.TransientModel):
    _name = 'add.is.consequence.fonctionnement.stucture'
    _description = u"Initialisation Conséquence pour l’organisation de la structure"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.consequence.fonctionnement.stucture']
        add_list = [
            u'difficulté d’approvisionnement',
            u'difficulté d’accès à la structure ou au lieu de prise en charge',
            u'nécessité de déplacer des résidents',
            u'suspension d’activité',
            u"intervention des forces de l’ordre ou des secours",
            u'autre (à préciser)',
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data)])
            if not generaux_ids:
                add_data_obj.create({'name': data})
        return True


class add_toutes_tables(models.TransientModel):
    _name = 'add.toutes.tables'
    _description = u"Initialisation de toutes les tables"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['add.is.criteres.generaux']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.demande.intervention.secours']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.consequence.personne.prise.en.charge']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.consequence.personnel']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.consequence.fonctionnement.stucture']
        add_data_obj.add_data()
        return True

