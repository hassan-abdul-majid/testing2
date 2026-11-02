/** @odoo-module **/

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { cookie } from "@web/core/browser/cookie";
import { user } from "@web/core/user";

import { switchColorSchemeItem } from "./color_scheme_menu_items";

const serviceRegistry = registry.category("services");
const userMenuRegistry = registry.category("user_menuitems");

export const colorSchemeService = {
    dependencies: ["ui", "orm"],

    start(env, { ui, orm }) {
        userMenuRegistry.add("color_scheme.switch", switchColorSchemeItem);
        return {
            async switchToColorScheme(scheme) {
                cookie.set("color_scheme", scheme);
                try {
                    await orm.write("res.users", [user.userId], { color_scheme: scheme });
                } catch {
                    // Cookie still applies if the preference write is denied.
                }
                ui.block();
                browser.location.reload();
            },
        };
    },
};
serviceRegistry.add("color_scheme", colorSchemeService);
