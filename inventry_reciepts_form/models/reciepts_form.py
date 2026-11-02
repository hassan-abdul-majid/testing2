from odoo import models, fields


class InventoryForm(models.Model):

    _inherit = "stock.picking"

    hassan_field = fields.Char(
        string="Hassan Abdul Majid"
    )

    personal_name = fields.Char(
        string="Name"
    )

    personal_email = fields.Char(
        string="Email"
    )

    personal_phone = fields.Char(
        string="Phone Number"
    )