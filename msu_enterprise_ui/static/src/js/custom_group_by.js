import { CustomGroupByItem } from "@web/search/custom_group_by_item/custom_group_by_item";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

CustomGroupByItem.components = {
    ...(CustomGroupByItem.components || {}),
    Dropdown,
    DropdownItem,
};
CustomGroupByItem.template = "msu_enterprise_ui.CustomGroupByItem";

patch(CustomGroupByItem.prototype, {
    get msuGroupByFields() {
        return (this.props.fields || []).filter(
            (field) => field.type !== "properties" && !field.isProperty
        );
    },
    get msuAddCustomGroupLabel() {
        return _t("Add Custom Group");
    },
    onMsuAddCustomGroup(fieldName) {
        if (fieldName) {
            this.props.onAddCustomGroup(fieldName);
        }
    },
});
