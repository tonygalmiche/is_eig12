# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class add_is_criteres_generaux(models.TransientModel):
    _name = 'add.is.criteres.generaux'
    _description = u"Initialisation Critères généraux"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.criteres.generaux']
        add_list = [
            [u'Evènement inhabituel par sa nature, son ampleur ou sa gravité', 1],
            [u'Evènement ayant pour conséquence une exclusion temporaire ou définitive', 2],
            [u'Evènement ayant pour conséquence une sanction disciplinaire grave ou une procédure judiciaire à l’encontre de personnels', 3],
            [u'Evènement nécessitant l’activation du Plan Bleu', 4],
            [u'Evènement nécessitant l’activation d’une CUMP', 5],
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data[0])])
            if not generaux_ids:
                add_data_obj.create({'name': data[0], 'code': data[1]})
            else:
                for c in generaux_ids:
                    c.write({'name': data[0], 'code': data[1]})
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
            [u'décès', 1],
            ['mise en jeu du pronostic vital', 2],
            [u'probable déficit fonctionnel permanent', 3],
            ['soins internes', 4],
            ['hospitalisation', 5],
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data[0])])
            if not generaux_ids:
                add_data_obj.create({'name': data[0],'code': data[1]})
            else:
                for c in generaux_ids:
                    c.write({'name': data[0],'code': data[1]})
        return True


class add_is_consequence_personnel(models.TransientModel):
    _name = 'add.is.consequence.personnel'
    _description = u"Initialisation Conséquence pour le personnel"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.consequence.personnel']
        add_list = [
            ['interruption temporaire de travail', 1],
            [u'réquisition', 2],
            ['autre (y compris suicide ou tentative de suicide)', 3],
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data[0])])
            if not generaux_ids:
                add_data_obj.create({'name': data[0], 'code': data[1]})
            else:
                for c in generaux_ids:
                    c.write({'name': data[0],'code': data[1]})
        return True


class add_is_consequence_fonctionnement_stucture(models.TransientModel):
    _name = 'add.is.consequence.fonctionnement.stucture'
    _description = u"Initialisation Conséquence pour l’organisation de la structure"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.consequence.fonctionnement.stucture']
        add_list = [
            [u'difficulté d’approvisionnement', 1],
            [u'difficulté d’accès à la structure ou au lieu de prise en charge', 2],
            [u'nécessité de déplacer des résidents', 3],
            [u'suspension d’activité', 4],
            [u"intervention des forces de l’ordre ou des secours", 5],
            [u'autre (à préciser)', 6],
        ]
        for data in add_list:
            generaux_ids = add_data_obj.search([('name', '=', data[0])])
            if not generaux_ids:
                add_data_obj.create({'name': data[0], 'code': data[1]})
            else:
                for c in generaux_ids:
                    c.write({'name': data[0],'code': data[1]})
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
        add_data_obj = self.env['add.is.nature.evenement']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.destinataire']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.qualite']
        add_data_obj.add_data()
        add_data_obj = self.env['add.is.qualite.autre']
        add_data_obj.add_data()
        return True


class add_is_type_evenement(models.TransientModel):
    _name = 'add.is.type.evenement'
    _description = u"is.type.evenement"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.type.evenement']
        type_data1 = self.env.ref('is_eig12.is_type_evenement_1', False)
        type_data2 = self.env.ref('is_eig12.is_type_evenement_2', False)
        type_data3 = self.env.ref('is_eig12.is_type_evenement_3', False)
        type_data4 = self.env.ref('is_eig12.is_type_evenement_4', False)
        add_dict1 = {
            'name': 'Situation exceptionnelle',
            'description': u'Evènement ou dysfonctionnement grave pouvant affecter l’accompagnement des personnes accompagnées ou menacer leur santé, sécurité ou bien-être.',
            'code': 'SE',
        }
        add_dict2 = {
            'name': u'Information préoccupante',
            'description': u'Information à la cellule départementale sur la situation d’un mineur ou d’une personne vulnérable, bénéficiant ou non d’un accompagnement, pouvant laisser craindre que sa santé, sa sécurité ou sa moralité sont en danger ou risque de l’être ou que les conditions de son éducation ou développement sont gravement compromises ou en risque de l’être.',
            'code': 'IP',
        }
        add_dict3 = {
            'name': u'Signalement au Procureur',
            'description': u'Transmission à l’autorité judiciaire de l’ensemble des documents écrits concernant des faits graves, des éléments de danger avérés, compromettant le développement du mineur et sollicitant une mesure de protection judiciaire.',
            'information_speciale': u"Attention : l'applicatif n'envoie pas automatiquement un courrier aux autorités judiciaires. En cas de signalement aux autorités judiciaires, il est nécessaire d'imprimer le document pdf intitulé 'signalement' généré dans les 'pièces-jointes' de l'applicatif et de l'envoyer par fax à l'autorité judiciaire correspondante. Également, une information préoccupante est automatiquement envoyée au Conseil Départemental, par mail.",
            'code': 'SP',
        }
        add_dict4 = {
            'name': u'Situation exceptionnelle pour public d’AMI ou de CHU',
            'description': u'Evènement ou dysfonctionnement grave pouvant affecter l’accompagnement des personnes accompagnées ou menacer leur santé, sécurité ou bien-être.',
            'code': 'SEA',
        }
        
        if type_data1:
            exist_ids = add_data_obj.search([('name', '=', type_data1.name)])
            if not exist_ids:
                add_data_obj.create(add_dict1)
            else:
                for e in exist_ids:
                    e.write(add_dict1)
        if type_data2:
            exist_ids = add_data_obj.search([('name', '=', type_data2.name)])
            if not exist_ids:
                add_data_obj.create(add_dict2)
            else:
                for e in exist_ids:
                    e.write(add_dict2)
        if type_data3:
            exist_ids = add_data_obj.search([('name', '=', type_data3.name)])
            if not exist_ids:
                add_data_obj.create(add_dict3)
            else:
                for e in exist_ids:
                    e.write(add_dict3)
        if type_data4:
            exist_ids = add_data_obj.search([('name', '=', type_data4.name)])
            if not exist_ids:
                add_data_obj.create(add_dict4)
            else:
                for e in exist_ids:
                    e.write(add_dict4)
        return True


class add_is_nature_evenement(models.TransientModel):
    _name = 'add.is.nature.evenement'
    _description = u"Initialisation Nature Evènement "

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.nature.evenement']
        type_data1 = self.env.ref('is_eig12.is_type_evenement_1', False)
        type_data2 = self.env.ref('is_eig12.is_type_evenement_2', False)
        type_data3 = self.env.ref('is_eig12.is_type_evenement_3', False)
        type_data4 = self.env.ref('is_eig12.is_type_evenement_4', False)
        add_list = [
            [u"Absence imprévue de plusieurs professionnels, mettant en difficulté l’effectivité de l’accompagnement ou la sécurité des personnes accueillies", 1],
            [u"Autre (accident ou incident lié à une erreur ou à un défaut de soin ou de surveillance)", 2],
            [u"Autre (évènement en santé environnementale)", 3],
            [u"Autre (évènement relatif à l’accompagnement des usagers)", 4],
            [u"Autre (évènement relatif au fonctionnement et organisation de l’établissement)", 5],
            [u"Comportements violents de la part d’usagers à l’égard d’autres usagers", 6],
            [u"Comportements violents de la part d’usagers à l’égard de professionnels", 7],
            [u"Conflits sociaux ou menaces de conflits sociaux pouvant entraîner un risque pour l’usager", 8],
            [u"Décès accidentel ou consécutif à un défaut de surveillance ou de prise en charge de la personne", 9],
            [u"Défaillance technique significative et durable", 10],
            [u"Difficultés relationnelles récurrentes avec la famille entraînant une perturbation de l’organisation ou du fonctionnement de la structure", 11],
            [u"Disparition(s) inquiétante(s) de personne(s) accueillie(s) (services de police ou gendarmeries alertés)", 12],
            [u"Epidémie", 13],
            [u"Erreur d’identité dans la délivrance d’un médicament", 14],
            [u"Fugue(s) inquiétante(s) de personne(s) accueillie(s) (services de police ou gendarmeries alertés)", 15],
            [u"Intoxication", 16],
            [u"Intrusion informatique", 17],
            [u"Légionnelles", 18],
            [u"Maladie infectieuse", 19],
            [u"Maltraitances non précisées", 20],
            [u"Manquements graves au règlement du lieu d’hébergement ou d’accueil qui compromettent la prise en charge", 21],
            [u"Mise en danger par dérive sectaire et radicalisation", 22],
            [u"Négligences graves ou erreurs successives", 23],
            [u"Non-respect de la prescription médicale, erreur dans la dispensation, la préparation ou l’administration", 24],
            [u"Présentation de faux diplômes", 26],
            [u"Sinistre ou évènement météorologique exceptionnel", 27],
            [u"Suicide", 28],
            [u"Turn-over du personnel ou grève, mettant en difficulté l’effectivité de l’accompagnement ou la sécurité des personnes accueillies", 29],
            [u"Vacance de poste prolongée, notamment d’encadrement, difficulté de recrutement", 30],
            [u"Violences médicales ou médicamenteuses", 31],
            [u"Vols récurrents à l’encontre des résidents, si dépôt de plainte", 32],
        ]
        common_list = [
            [u"Actes de malveillance au sein de la structure", 33],
            [u"Autre (évènement relatif à la sécurité des biens et des personnes)", 34],
            [u"Tentative de suicide", 35],
            [u"Violences physiques", 36],
            [u"Violences psychologiques et morales", 37],
            [u"Violences sexuelles", 38],
        ]
        chu_list = [
            [u"Accident corporel grave", 39],
            [u"Autre (évènements relatifs aux victimes présumées)", 40],
            [u"Décès", 41],
            [u"Défaillances techniques graves", 42],
            [u"Epidémie - Propagation de parasites", 43],
            [u"Explosions ou incendie ou inondation", 44],
            [u"Fugues ou disparition de personnes accueillies > à 48 H", 45],
            [u"Intoxication alimentaire si plusieurs personnes sont concernées", 46],
            [u"Négligences graves de l’entourage", 47],
            [u"Racket", 48],
            [u"Trafic au sein de l’établissement", 49],
            [u"Vols récurrents et /ou qualifiés à l’encontre des autres résidents et ou des salariés ou des bénévoles", 50],
        ]
        if type_data1 and type_data2 and type_data3:
            for data in add_list:
                nature_ids = add_data_obj.search([('name', '=', data[0])])
                if not nature_ids:
                    create_id = add_data_obj.create({'name': data[0], 'code': data[1]})
                    type_data1.is_nature_ids = [(4,create_id.id)]
                    type_data2.is_nature_ids = [(4,create_id.id)]
                    type_data3.is_nature_ids = [(4,create_id.id)]
                else:
                    for n in nature_ids:
                        n.write({'name': data[0], 'code': data[1]})
                    type_data1.is_nature_ids = [(4,nature_ids.ids[0])]
                    type_data2.is_nature_ids = [(4,nature_ids.ids[0])]
                    type_data3.is_nature_ids = [(4,nature_ids.ids[0])]
        if type_data1 and type_data2 and type_data3 and type_data4:
            for data in common_list:
                nature_ids = add_data_obj.search([('name', '=', data[0])])
                if not nature_ids:
                    create_id = add_data_obj.create({'name': data[0], 'code': data[1]})
                    type_data1.is_nature_ids = [(4,create_id.id)]
                    type_data2.is_nature_ids = [(4,create_id.id)]
                    type_data3.is_nature_ids = [(4,create_id.id)]
                    type_data4.is_nature_ids = [(4,create_id.id)]
                else:
                    for n in nature_ids:
                        n.write({'name': data[0], 'code': data[1]})
                    type_data1.is_nature_ids = [(4,nature_ids.ids[0])]
                    type_data2.is_nature_ids = [(4,nature_ids.ids[0])]
                    type_data3.is_nature_ids = [(4,nature_ids.ids[0])]
                    type_data4.is_nature_ids = [(4,nature_ids.ids[0])]
        if type_data4:
            for data in chu_list:
                nature_ids = add_data_obj.search([('name', '=', data[0])])
                if not nature_ids:
                    create_id = add_data_obj.create({'name': data[0], 'code': data[1]})
                    type_data4.is_nature_ids = [(4,create_id.id)]
                else:
                    for n in nature_ids:
                        n.write({'name': data[0], 'code': data[1]})
                    type_data4.is_nature_ids = [(4,nature_ids.ids[0])]
        return True


class add_is_destinataire(models.TransientModel):
    _name = 'add.is.destinataire'
    _description = u"Initialisation Destinataires"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.destinataire']
        add_list = [
            u"Media",
            u"Famille/représentant légal de la (des) personne(s) faisant l’objet de l’IP",
            u"Famille/représentant légal d'autre(s) usager(s) concerné(s)",
            u"Autorité judiciaire",
            u"Cellule de l'enfance",
            u"Usager / Patient / Résident",
        ]
        for data in add_list:
            destinataire_ids = add_data_obj.search([('name', '=', data)])
            if not destinataire_ids:
                add_data_obj.create({'name': data})
        return True


class add_is_qualite(models.TransientModel):
    _name = 'add.is.qualite'
    _description = u"Initialisation Qualité"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.qualite']
        add_list = [
            "Usager",
            "Famille",
            "Autre",
        ]
        for data in add_list:
            qualite_ids = add_data_obj.search([('name', '=', data)])
            if not qualite_ids:
                add_data_obj.create({'name': data})
        return True


class add_is_qualite_autre(models.TransientModel):
    _name = 'add.is.qualite.autre'
    _description = u"Initialisation Qualité Autre"

    @api.multi
    def add_data(self):
        add_data_obj = self.env['is.qualite.autre']
        add_list = [
            "Usager",
            "Famille",
            "Professionnel",
            "Autre",
        ]
        for data in add_list:
            qualite_ids = add_data_obj.search([('name', '=', data)])
            if not qualite_ids:
                add_data_obj.create({'name': data})
        return True


