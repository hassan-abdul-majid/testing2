import { MessagingMenu } from "@mail/core/public_web/messaging_menu";
import { ChannelSelector } from "@mail/discuss/core/web/channel_selector";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

Object.assign(MessagingMenu.components, { ChannelSelector });

const RAIL_ORDER = ["chat", "channel", "meetings", "livechat", "whatsapp"];
const RAIL_ICONS = {
    chat: "fa fa-users",
    channel: "fa fa-hashtag",
    livechat: "fa fa-comments",
    whatsapp: "fa fa-whatsapp",
};

patch(MessagingMenu.prototype, {
    setup() {
        super.setup();
        Object.assign(this.state, { msuFilter: "all" });
    },
    beforeOpen() {
        const res = super.beforeOpen?.(...arguments);
        this.state.msuFilter = "all";
        return res;
    },
    get threads() {
        let threads = super.threads;
        if (this.state.msuFilter === "unread") {
            threads = threads.filter((thread) => thread.isUnread);
        } else if (this.state.msuFilter === "thread") {
            threads = threads.filter((thread) => thread.parent_channel_id);
        }
        return threads;
    },
    get msuRailItems() {
        const labels = {
            chat: _t("Chats"),
            channel: _t("Channels"),
            livechat: _t("Live Chats"),
        };
        const items = this.tabs
            .filter((tab) => tab.id !== "main")
            .map((tab) => ({
                id: tab.id,
                icon: RAIL_ICONS[tab.id] || tab.icon,
                label: labels[tab.id] || tab.label,
                kind: "tab",
            }));
        items.push({
            id: "meetings",
            icon: "fa fa-video-camera",
            label: _t("Meetings"),
            kind: "action",
        });
        items.sort((a, b) => {
            const indexA = RAIL_ORDER.indexOf(a.id);
            const indexB = RAIL_ORDER.indexOf(b.id);
            return (indexA < 0 ? 50 : indexA) - (indexB < 0 ? 50 : indexB);
        });
        return items;
    },
    get msuNewLabel() {
        return this.store.discuss.activeTab === "channel" ? _t("+ Channel") : _t("+ Message");
    },
    get msuSelectorCategory() {
        if (this.state.adding === "channel") {
            return this.store.discuss.channels;
        }
        if (this.state.adding === "whatsapp" && this.store.discuss.whatsapp) {
            return this.store.discuss.whatsapp;
        }
        return this.store.discuss.chats;
    },
    msuTabCounter(tab) {
        if (tab.kind !== "tab") {
            return 0;
        }
        const types = this.store.tabToThreadType(tab.id);
        return Object.values(this.store.Thread.records).filter(
            (thread) =>
                thread.displayToSelf && thread.isUnread && types.includes(thread.channel_type)
        ).length;
    },
    onClickMsuRail(tab) {
        if (tab.kind === "action") {
            this.onClickMsuMeetings();
            return;
        }
        this.onClickNavTab(tab.id);
    },
    onClickMsuMeetings() {
        if (typeof this.onClickStartMeeting === "function") {
            this.onClickStartMeeting();
            return;
        }
        this.store.startMeeting?.();
        this.dropdown.close();
    },
    onClickMsuNew() {
        if (this.store.discuss.activeTab === "channel") {
            this.state.adding = "channel";
            return;
        }
        if (typeof this.onClickNewMessage === "function") {
            this.onClickNewMessage();
            return;
        }
        this.state.adding = "chat";
    },
    onMsuSelectorDone() {
        this.state.adding = false;
        this.dropdown.close();
    },
    onMsuSelectorClose() {
        this.state.adding = false;
    },
    setMsuFilter(filter) {
        this.state.msuFilter = filter;
    },
});
