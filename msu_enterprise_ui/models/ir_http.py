# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _post_logout(cls):
        super()._post_logout()
        request.future_response.set_cookie('color_scheme', max_age=0)

    def session_info(self):
        info = super().session_info()
        user = self.env.user
        if user and not user._is_public():
            settings = self.env['res.users.settings']._find_or_create_for_user(user)
            info['color_scheme_preference'] = settings.color_scheme or 'system'
        else:
            info['color_scheme_preference'] = 'system'
        return info
