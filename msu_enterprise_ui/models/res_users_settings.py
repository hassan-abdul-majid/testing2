# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsersSettings(models.Model):
    _inherit = 'res.users.settings'

    homemenu_config = fields.Json(string="Home Menu Configuration", readonly=True)
    color_scheme = fields.Selection(
        selection=[
            ('system', 'System'),
            ('light', 'Light'),
            ('dark', 'Dark'),
        ],
        string="Color Scheme",
        default='system',
        required=True,
    )
