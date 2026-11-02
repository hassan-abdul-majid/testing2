/** @odoo-module **/

import { browser } from "@web/core/browser/browser";

/**
 * Resolve the effective light/dark scheme from a stored preference.
 * @param {"system"|"light"|"dark"} preference
 * @returns {"light"|"dark"}
 */
export function resolveColorScheme(preference) {
    if (preference === "dark") {
        return "dark";
    }
    if (preference === "light") {
        return "light";
    }
    return browser.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
