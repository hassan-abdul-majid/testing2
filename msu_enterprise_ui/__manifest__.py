{
    'name': 'MSU Enterprise UI',
    'version': '18.0.1.8.9',
    'category': 'Theme/Backend',
    'summary': 'Enterprise-grade navigation & backend UI theme for Odoo Community',
    'description': """
MSU Enterprise UI
=================

A standalone theme that upgrades the Odoo **Community** backend to feel
like the **Enterprise** edition, without modifying any core file.

What it does
------------
- White, modern top navbar with rounded, animated menu entries (Enterprise look).
- Full-screen Home Menu app launcher with Enterprise background images.
- **Dark mode** toggle in the user menu + Theme preference (System / Light / Dark).
- Login page with Enterprise gradient/SVG background and white card.
- Refined button color system with polished hover, active, focus and disabled states.
- Dark-mode component overrides (dropdowns, kanban, list, search, forms, …).
- Smooth dropdown open/close animations and hover-to-open navbar menus (desktop).
- Mobile burger menu + PWA share URL support.
- Instant fuzzy menu search via the command palette.
- Elevation, shadows, larger radii, better spacing and custom scrollbars.

Architecture
------------
- SCSS variable overrides inject into ``web._assets_primary_variables``.
- Dark mode uses ``web.dark_mode_variables`` + ``web.assets_web_dark`` bundles
  (same pattern as Enterprise ``web_enterprise``).
- OWL patches for Home Menu, NavBar, WebClient, BurgerMenu and Pivot (mobile).
- ``color_scheme`` service + user settings for theme persistence.
    """,
    'author': 'Muhammad Sana Ullah',
    'maintainer': 'Muhammad Sana Ullah',
    'depends': ['web'],
    'data': [
        'views/res_users_views.xml',
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            (
                'before',
                'web/static/src/scss/primary_variables.scss',
                'msu_enterprise_ui/static/src/scss/primary_variables.scss',
            ),
            (
                'after',
                'web/static/src/scss/primary_variables.scss',
                'msu_enterprise_ui/static/src/**/*.variables.scss',
            ),
            (
                'after',
                'web/static/src/webclient/navbar/navbar.variables.scss',
                'msu_enterprise_ui/static/src/scss/variables.scss',
            ),
        ],
        'web._assets_secondary_variables': [
            (
                'before',
                'web/static/src/scss/secondary_variables.scss',
                'msu_enterprise_ui/static/src/scss/secondary_variables.scss',
            ),
        ],
        'web._assets_backend_helpers': [
            (
                'before',
                'web/static/src/scss/bootstrap_overridden.scss',
                'msu_enterprise_ui/static/src/scss/bootstrap_overridden.scss',
            ),
        ],
        'web.assets_frontend': [
            'msu_enterprise_ui/static/src/scss/home_menu_background.scss',
            'msu_enterprise_ui/static/src/scss/navbar.scss',
            'msu_enterprise_ui/static/src/scss/login.scss',
        ],
        'web.assets_backend': [
            # --- Enterprise variable-driven styles ---
            'msu_enterprise_ui/static/src/scss/home_menu_background.scss',
            'msu_enterprise_ui/static/src/scss/list_controller.scss',
            'msu_enterprise_ui/static/src/scss/kanban_view.scss',
            'msu_enterprise_ui/static/src/scss/notebook.scss',
            # --- MSU polish layer ---
            'msu_enterprise_ui/static/src/scss/theme.scss',
            'msu_enterprise_ui/static/src/scss/home_menu.scss',
            'msu_enterprise_ui/static/src/scss/navbar.scss',
            'msu_enterprise_ui/static/src/scss/buttons.scss',
            'msu_enterprise_ui/static/src/scss/dropdowns.scss',
            'msu_enterprise_ui/static/src/scss/controls.scss',
            'msu_enterprise_ui/static/src/scss/animations.scss',
            'msu_enterprise_ui/static/src/scss/command_palette.scss',
            'msu_enterprise_ui/static/src/scss/feedback.scss',
            'msu_enterprise_ui/static/src/scss/chrome.scss',
            'msu_enterprise_ui/static/src/scss/badges.scss',
            'msu_enterprise_ui/static/src/scss/discuss.scss',
            'msu_enterprise_ui/static/src/scss/loading_indicator.scss',
            # --- OWL templates ---
            'msu_enterprise_ui/static/src/xml/home_menu.xml',
            'msu_enterprise_ui/static/src/xml/navbar.xml',
            'msu_enterprise_ui/static/src/xml/burger_menu.xml',
            'msu_enterprise_ui/static/src/xml/loading_indicator.xml',
            'msu_enterprise_ui/static/src/xml/chrome.xml',
            'msu_enterprise_ui/static/src/xml/messaging_menu.xml',
            'msu_enterprise_ui/static/src/xml/custom_group_by.xml',
            # --- Behaviour ---
            'msu_enterprise_ui/static/src/js/home_menu.js',
            'msu_enterprise_ui/static/src/js/home_menu_service.js',
            'msu_enterprise_ui/static/src/js/navbar.js',
            'msu_enterprise_ui/static/src/js/navbar_hover.js',
            'msu_enterprise_ui/static/src/js/burger_menu.js',
            'msu_enterprise_ui/static/src/js/fuzzy_search.js',
            'msu_enterprise_ui/static/src/js/command_palette.js',
            'msu_enterprise_ui/static/src/js/webclient.js',
            'msu_enterprise_ui/static/src/js/color_scheme_utils.js',
            'msu_enterprise_ui/static/src/js/color_scheme_menu_items.js',
            'msu_enterprise_ui/static/src/js/color_scheme_service.js',
            'msu_enterprise_ui/static/src/js/share_url.js',
            'msu_enterprise_ui/static/src/js/share_url_burger_menu.js',
            'msu_enterprise_ui/static/src/js/messaging_menu.js',
            'msu_enterprise_ui/static/src/js/custom_group_by.js',
        ],
        'web.assets_backend_lazy': [
            'msu_enterprise_ui/static/src/js/pivot_renderer.js',
            'msu_enterprise_ui/static/src/scss/pivot_renderer.scss',
        ],
        'web.assets_backend_lazy_dark': [
            ('include', 'web.dark_mode_variables'),
            (
                'before',
                'msu_enterprise_ui/static/src/scss/bootstrap_overridden.scss',
                'msu_enterprise_ui/static/src/scss/bootstrap_overridden.dark.scss',
            ),
            (
                'after',
                'web/static/lib/bootstrap/scss/_functions.scss',
                'msu_enterprise_ui/static/src/scss/bs_functions_overridden.dark.scss',
            ),
        ],
        # ========= Dark Mode (Enterprise pattern) =========
        'web.dark_mode_variables': [
            (
                'before',
                'msu_enterprise_ui/static/src/scss/primary_variables.scss',
                'msu_enterprise_ui/static/src/scss/primary_variables.dark.scss',
            ),
            (
                'before',
                'msu_enterprise_ui/static/src/**/*.variables.scss',
                'msu_enterprise_ui/static/src/**/*.variables.dark.scss',
            ),
            (
                'before',
                'msu_enterprise_ui/static/src/scss/secondary_variables.scss',
                'msu_enterprise_ui/static/src/scss/secondary_variables.dark.scss',
            ),
            (
                'after',
                'web/static/src/webclient/navbar/navbar.variables.scss',
                'msu_enterprise_ui/static/src/scss/variables.dark.scss',
            ),
        ],
        'web.assets_web_dark': [
            ('include', 'web.dark_mode_variables'),
            (
                'before',
                'msu_enterprise_ui/static/src/scss/bootstrap_overridden.scss',
                'msu_enterprise_ui/static/src/scss/bootstrap_overridden.dark.scss',
            ),
            (
                'after',
                'web/static/lib/bootstrap/scss/_functions.scss',
                'msu_enterprise_ui/static/src/scss/bs_functions_overridden.dark.scss',
            ),
            'msu_enterprise_ui/static/src/**/*.dark.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': ['web'],
    'license': 'LGPL-3',
}
