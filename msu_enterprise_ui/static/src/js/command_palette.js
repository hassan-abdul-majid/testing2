/** @odoo-module **/

/**
 * MSU Enterprise UI — Command palette open/close motion
 * ----------------------------------------------------------------------------
 * OWL removes the dialog immediately on close, so a CSS fade-out never plays
 * unless we keep the overlay in the DOM for one animation frame cycle.
 *
 * Only the command palette is delayed. Other dialogs stay instant. No
 * transform is applied to `.modal-dialog` (that caused the sideways jump).
 */

import { CommandPalette } from "@web/core/commands/command_palette";
import { dialogService } from "@web/core/dialog/dialog_service";
import { patch } from "@web/core/utils/patch";

const PALETTE_CLOSE_MS = 200;

function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

patch(dialogService, {
    start(env, { overlay }) {
        const wrappedOverlay = {
            add(component, props, options = {}) {
                const remove = overlay.add(component, props, options);
                if (props.subComponent !== CommandPalette) {
                    return remove;
                }
                let closing = false;
                return () => {
                    if (closing) {
                        return;
                    }
                    const palette = document.querySelector(".o_dialog:has(.o_command_palette)");
                    if (!palette || prefersReducedMotion()) {
                        closing = true;
                        return remove();
                    }
                    closing = true;
                    palette.classList.add("msu-palette-closing");
                    window.setTimeout(remove, PALETTE_CLOSE_MS);
                };
            },
        };
        return super.start(env, { overlay: wrappedOverlay });
    },
});
