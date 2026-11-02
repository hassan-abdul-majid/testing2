# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    color_scheme = fields.Selection(
        related='res_users_settings_id.color_scheme',
        readonly=False,
        string="Theme",
        help="System follows your device. Light and Dark stay fixed until you change them.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['color_scheme']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['color_scheme']

    def _msu_resolve_color_scheme(self):
        """Return the stored preference (system/light/dark)."""
        self.ensure_one()
        settings = self.env['res.users.settings']._find_or_create_for_user(self)
        return settings.color_scheme or 'system'

    def preference_save(self):
        from odoo.http import request
        if request and self == request.env.user:
            preference = self._msu_resolve_color_scheme()
            if preference == 'system':
                request.future_response.set_cookie('color_scheme', max_age=0)
            else:
                request.future_response.set_cookie(
                    'color_scheme', preference, max_age=60 * 60 * 24 * 365
                )
        return super().preference_save()
