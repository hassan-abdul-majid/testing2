/** @odoo-module **/

/**
 * MSU Enterprise UI — WebClient patch
 * ----------------------------------------------------------------------------
 * Enterprise shows the Home Menu as the landing screen instead of loading the
 * first app directly. We reproduce that by overriding `_loadDefaultApp` to open
 * the home menu. Additive patch; the stock behaviour is restored on uninstall.
 */

import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";

patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.hm = useService("home_menu");
    },

    /**
     * @override
     */
    _loadDefaultApp() {
        return this.hm.toggle(true);
    },
});
