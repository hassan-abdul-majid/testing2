/** @odoo-module **/

/**
 * MSU Enterprise UI — NavBar patch
 * ----------------------------------------------------------------------------
 * Turns the Community "Apps" dropdown button into the Enterprise-style menu
 * toggle: an animated 3x3 grid that morphs into a "back" arrow when inside an
 * app, next to the current app's brand name/icon. Clicking it toggles the
 * full-screen Home Menu (via the home_menu service).
 *
 * Implemented as an additive `patch` on the core NavBar plus a template
 * extension (see navbar.xml). No core file is modified.
 */

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useService, useBus } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { useState, useEffect, useRef } from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.hm = useState(useService("home_menu"));
        this.menuAppsRef = useRef("menuApps");
        this.navRef = useRef("nav");
        useBus(this.env.bus, "HOME-MENU:TOGGLED", () => this._updateMenuAppsIcon());
        useBus(this.env.bus, "MENUS:APP-CHANGED", () => this._updateMenuAppsIcon());
        useEffect(() => this._updateMenuAppsIcon());
    },

    get hasBackgroundAction() {
        return this.hm.hasBackgroundAction;
    },

    get isInApp() {
        return !this.hm.hasHomeMenu;
    },

    /**
     * On small screens keep the native burger sidebar; but if the home menu is
     * open, tapping the toggle should close it and reveal the app behind.
     * @override
     */
    _openAppMenuSidebar() {
        if (this.hm.hasHomeMenu) {
            this.hm.toggle(false);
        } else {
            super._openAppMenuSidebar(...arguments);
        }
    },

    /**
     * Sync the toggle icon (grid <-> back arrow), the app brand visibility and
     * the breadcrumb/submenus depending on whether the home menu is shown.
     */
    _updateMenuAppsIcon() {
        const menuAppsEl = this.menuAppsRef.el;
        if (!menuAppsEl) {
            return;
        }
        menuAppsEl.classList.toggle("o_hidden", !this.isInApp && !this.hasBackgroundAction);
        menuAppsEl.classList.toggle(
            "o_menu_toggle_back",
            !this.isInApp && this.hasBackgroundAction
        );
        if (!this.isScopedApp) {
            const title =
                !this.isInApp && this.hasBackgroundAction ? _t("Previous view") : _t("Home menu");
            menuAppsEl.title = title;
            menuAppsEl.ariaLabel = title;
        }

        const navEl = this.navRef.el;
        if (!navEl) {
            return;
        }
        const menuBrand = navEl.querySelector(".o_menu_brand");
        if (menuBrand) {
            menuBrand.classList.toggle("o_hidden", !this.isInApp);
        }
        const menuBrandIcon = navEl.querySelector(".o_menu_brand_icon");
        if (menuBrandIcon) {
            menuBrandIcon.classList.toggle("o_hidden", !this.isInApp);
        }
        const appSubMenus = this.appSubMenus.el;
        if (appSubMenus) {
            appSubMenus.classList.toggle("o_hidden", !this.isInApp);
        }
        const breadcrumb = navEl.querySelector(".o_breadcrumb");
        if (breadcrumb) {
            breadcrumb.classList.toggle("o_hidden", !this.isInApp);
        }
    },

    /**
     * @override
     */
    onAllAppsBtnClick() {
        super.onAllAppsBtnClick(...arguments);
        this.hm.toggle(true);
        this._closeAppMenuSidebar();
    },
});
