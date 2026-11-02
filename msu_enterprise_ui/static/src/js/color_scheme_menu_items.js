/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { cookie as cookieManager } from "@web/core/browser/cookie";

export function switchColorSchemeItem(env) {
    return {
        type: "switch",
        id: "color_scheme.switch_theme",
        description: _t("Dark Mode"),
        callback: () => {
            const next = cookieManager.get("color_scheme") === "dark" ? "light" : "dark";
            env.services.color_scheme.switchToColorScheme(next);
        },
        isChecked: cookieManager.get("color_scheme") === "dark",
        sequence: 30,
    };
}
