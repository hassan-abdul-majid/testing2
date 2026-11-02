/** @odoo-module **/

/**
 * MSU Enterprise UI — Navbar menu hover (open on hover, close on leave)
 *
 * Community Dropdown only opens on hover when another item in the same
 * DropdownGroup is already open (`group.isOpen`). Enterprise feels instant
 * because the first top-level section also opens on hover, and everything
 * closes when the pointer leaves the menu zone.
 *
 * This patch:
 *   1. Opens top-level `.o_menu_sections` dropdowns on first hover (desktop).
 *   2. Keeps native behaviour for nested submenus (`hasParent`).
 *   3. Auto-closes all navbar menus when the pointer leaves the menu zone
 *      (section bar + portaled popover), with a short grace delay for gaps.
 */

import { patch } from "@web/core/utils/patch";
import { Dropdown } from "@web/core/dropdown/dropdown";

const CLOSE_DELAY_MS = 130;

function supportsHover() {
    return (
        typeof window.matchMedia === "function" &&
        window.matchMedia("(hover: hover) and (pointer: fine)").matches
    );
}

function isNavbarSectionsToggle(el) {
    return Boolean(el?.closest?.(".o_main_navbar .o_menu_sections"));
}

function isNavbarMenuPopover(el) {
    if (!el?.closest?.(".o-dropdown--menu")) {
        return false;
    }
    // Only treat popovers as part of the navbar menu zone while a section is open.
    return Boolean(document.querySelector(".o_menu_sections [aria-expanded='true']"));
}

function isInNavbarMenuZone(el) {
    return isNavbarSectionsToggle(el) || isNavbarMenuPopover(el);
}

function closeNavbarMenus() {
    for (const toggle of document.querySelectorAll(".o_menu_sections [aria-expanded='true']")) {
        toggle.click();
    }
}

let closeTimer = null;

function cancelScheduledClose() {
    if (closeTimer) {
        clearTimeout(closeTimer);
        closeTimer = null;
    }
}

function scheduleClose() {
    cancelScheduledClose();
    closeTimer = setTimeout(() => {
        closeTimer = null;
        const stillInside = document.querySelector(
            ".o_menu_sections:hover, .o-dropdown--menu:hover"
        );
        if (!stillInside) {
            closeNavbarMenus();
        }
    }, CLOSE_DELAY_MS);
}

if (supportsHover()) {
    document.addEventListener(
        "pointerover",
        (ev) => {
            if (isInNavbarMenuZone(ev.target)) {
                cancelScheduledClose();
            }
        },
        true
    );

    document.addEventListener(
        "pointerout",
        (ev) => {
            if (!isInNavbarMenuZone(ev.target)) {
                return;
            }
            const related = ev.relatedTarget;
            if (related && isInNavbarMenuZone(related)) {
                return;
            }
            scheduleClose();
        },
        true
    );
}

patch(Dropdown.prototype, {
    handleMouseEnter() {
        if (this.props.disabled) {
            return;
        }

        // Top-level navbar section: open immediately on hover (desktop).
        if (supportsHover() && isNavbarSectionsToggle(this.target) && !this.hasParent) {
            cancelScheduledClose();
            this.target.focus();
            this.state.open();
            return;
        }

        return super.handleMouseEnter(...arguments);
    },
});
