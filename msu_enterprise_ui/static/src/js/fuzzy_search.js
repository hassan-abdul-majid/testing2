/** @odoo-module **/

/**
 * MSU Enterprise UI — Instant / fuzzy menu search
 * ----------------------------------------------------------------------------
 * Ported from the standalone `fuzzy_search` module (Syn_Project_Managment).
 *
 * Lets users open the command palette and start searching menus by typing any
 * letter key anywhere in the backend — no Ctrl+K required. Typing "s" opens
 * the palette pre-filled with "/s" so menu fuzzy-matching begins immediately.
 *
 * Skips triggering when focus is inside an input, textarea, or contenteditable
 * field, or when a modifier key (Ctrl/Alt/Meta) is held.
 */

import { registry } from "@web/core/registry";

const instantMenuSearchService = {
    dependencies: ["command"],

    start(env) {
        document.addEventListener("keydown", (event) => {
            // Ignore shortcuts and non-printable keys.
            if (event.ctrlKey || event.metaKey || event.altKey) {
                return;
            }
            if (event.key.length !== 1) {
                return;
            }
            // Letters only (a-z, A-Z) — same behaviour as fuzzy_search.
            if (!/^[a-zA-Z]$/.test(event.key)) {
                return;
            }

            const activeElement = document.activeElement;
            if (!activeElement) {
                return;
            }
            if (["INPUT", "TEXTAREA", "SELECT"].includes(activeElement.tagName)) {
                return;
            }
            if (activeElement.isContentEditable) {
                return;
            }

            event.preventDefault();
            env.services.command.openMainPalette({ searchValue: `/${event.key}` });
        });
    },
};

registry.category("services").add("msu_instant_menu_search", instantMenuSearchService);
