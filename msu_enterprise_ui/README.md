# MSU Enterprise UI

A **standalone** Odoo 18 **Community** module that brings the **Enterprise**
navigation experience — the full-screen **Home Menu** app launcher, the morphing
menu toggle, the white Enterprise navbar and the Enterprise button colors — to
Community, **without modifying any core file**. Install to enable, uninstall to
fully revert.

---

## 1. Community vs Enterprise — how the UI is actually built

Researched directly against the code in this workspace:

- Community: `odoo18.0/addons/web/static/src/webclient/**`
- Enterprise: `odoo_18.0+e.../odoo/addons/web_enterprise/static/src/webclient/**`

| Area | Community (`web`) | Enterprise (`web_enterprise`) |
|------|-------------------|-------------------------------|
| **Landing screen** | Loads the first app directly (`WebClient._loadDefaultApp`) | Shows a **full-screen Home Menu** (`WebClientEnterprise._loadDefaultApp → home_menu.toggle(true)`) |
| **App launcher** | "Apps" button opens a plain **dropdown list** | `HomeMenu` component: responsive **grid of app cards** with search, keyboard nav, drag-reorder |
| **Home Menu wiring** | none | `home_menu` **service** registers a `menu` client action that renders `HomeMenu`; `toggle()` switches grid ↔ current action |
| **Menu toggle** | `oi oi-apps` icon inside a `Dropdown` | Animated **3×3 grid SVG** (`.o_menu_toggle`) that morphs into a back-arrow when inside an app, beside the app brand name/icon |
| **Navbar color** | Solid brand purple, white text | White bar, gray rounded entries, hover `$o-gray-200` (`navbar.variables.scss`) |
| **Brand colors** | `$o-brand-primary: #71639e` | Mauve `#714B67` + teal action `#017e84` |
| **App cards** | none | Layered soft shadows, `hover → translateY(-2px)`, `active → scale(.98)` |

**Key takeaways used here**

1. The Home Menu is **not** just CSS — it is a `service` + client action + OWL
   component + a NavBar that talks to that service. To truly match Enterprise we
   re-implement those, using only public `@web` APIs (all the helpers —
   `computeAppsAndMenuItems`, `reorderApps`, `standardActionServiceProps`,
   `ControllerNotFoundError` — exist in Community).
2. Native theme variables are declared `!default` and bundled from
   `**/*.variables.scss` into `web._assets_primary_variables`, so re-declaring
   them re-themes native components cleanly.
3. The top navbar dropdowns already switch on hover once open (native
   `dropdown_group`/`dropdown_nesting`) — no custom hover hack is needed (an
   earlier attempt at auto-open-on-hover was removed because it fought the
   native close logic).

---

## 2. Implementation strategy

| Requirement | Approach | File |
|-------------|----------|------|
| Full-screen Home Menu | Port the Enterprise `home_menu` **service** (registers `menu` action) | `js/home_menu_service.js` |
| App-grid launcher | Port the `HomeMenu` **component** (search, keyboard nav, drag) + template | `js/home_menu.js`, `xml/home_menu.xml` |
| Morphing menu toggle + brand | **Patch** `NavBar` + extend `web.NavBar` template in place | `js/navbar.js`, `xml/navbar.xml` |
| Home Menu as landing | **Patch** `WebClient._loadDefaultApp → home_menu.toggle(true)` | `js/webclient.js` |
| White Enterprise navbar | Override `$o-navbar-*` variables | `scss/variables.scss` |
| Enterprise button colors | Override `$o-brand-primary`/`$o-action` (mauve + teal) | `scss/variables.scss` |
| Home-menu look + gradient | Grid, elevated cards, ambient background, transparent navbar | `scss/home_menu.scss` |
| Button/dropdown/card/input polish, motion | Additive presentation | `scss/buttons.scss`, `dropdowns.scss`, `controls.scss`, `animations.scss`, `theme.scss` |
| **Dark mode** | User-menu toggle + Theme preference + full dark component SCSS | `js/color_scheme_*.js`, `models/`, `**/*.dark.scss` |
| **Login page styling** | Enterprise gradient background + white card on `/web/login` | `home_menu_background.scss`, `views/webclient_templates.xml` |
| **App reorder persistence** | `homemenu_config` JSON on `res.users.settings` | `models/res_users_settings.py` |
| **Mobile burger menu** | Hide current app when Home Menu is open | `js/burger_menu.js` |
| **PWA share URL** | Share current URL from user menu + mobile burger | `js/share_url.js`, `xml/burger_menu.xml` |
| **Pivot mobile fixes** | Tooltip removal + nested group-by menus on small screens | `js/pivot_renderer.js`, lazy bundle |
| **View polish** | List thead borders, kanban quick-create, notebook tabs | `list_controller.scss`, `kanban_view.scss`, `notebook.scss` |
| **Full Enterprise color system** | Complete `primary_variables.scss` + bootstrap overrides | `scss/primary_variables.scss`, `bootstrap_overridden.scss` |

Only additive OWL `patch`es and template **extensions** are used; no core JS/XML
is overwritten. Theming is driven by SCSS variables + CSS custom properties, with
a dedicated dark bundle (`web.assets_web_dark`) matching the Enterprise pattern.

---

## 3. Module structure

```
msu_enterprise_ui/
├── __init__.py
├── __manifest__.py
├── models/                     # color_scheme user setting + session info
├── views/                      # preferences form + webclient bootstrap
├── README.md
├── static/img/
│   ├── background-light.svg
│   └── background-dark.jpg
└── static/src/
    ├── scss/
    │   ├── variables.scss      # -> web._assets_primary_variables (navbar, brand, radius)
    │   ├── theme.scss          # CSS-var design tokens, scrollbars, reduced-motion
    │   ├── home_menu.scss       # full-screen app grid + gradient background
    │   ├── navbar.scss          # navbar entry indicators, systray polish
    │   ├── buttons.scss         # button states (hover/active/focus/disabled)
    │   ├── dropdowns.scss       # popover elevation + open animation
    │   ├── controls.scss        # cards, inputs, list/kanban, notebook tabs
    │   └── animations.scss      # keyframes, ripple, skeleton shimmer
    ├── xml/
    │   ├── home_menu.xml         # HomeMenu component template
    │   └── navbar.xml            # extends web.NavBar (menu toggle + brand)
        └── js/
            ├── home_menu_service.js  # home_menu service + "menu" client action
            ├── home_menu.js          # HomeMenu OWL component
            ├── navbar.js             # NavBar patch (toggle, brand, home toggle)
            ├── navbar_hover.js       # hover-to-open + auto-close section menus
            ├── fuzzy_search.js       # instant menu search (type anywhere)
            └── webclient.js          # WebClient patch (home menu as landing)
```

---

## 4. Install / uninstall

```bash
# install
./odoo-bin -c config/odoo.conf -d <db> -i msu_enterprise_ui --stop-after-init
# then hard-refresh the browser (Ctrl+Shift+R)

# fully revert
./odoo-bin -c config/odoo.conf -d <db> --uninstall msu_enterprise_ui --stop-after-init
```

No data/models — removing the module restores the stock Community UI.

---

## 5. Performance & compatibility

- The Home Menu reuses Odoo's own action manager, menu service and command
  palette — no extra network calls; app data comes from the already-loaded menu
  tree.
- Motion uses `transform`/`opacity` only and collapses to `0s` under
  `prefers-reduced-motion: reduce`.
- Patches are additive and self-contained; they degrade gracefully if a class
  name changes upstream.
- Responsive: the grid adapts (3 → 4 → 6 columns); on small screens the native
  burger sidebar is preserved and the toggle closes the home menu on tap.
- **Instant menu search** (`fuzzy_search.js`): type any letter key anywhere in
  the backend (outside inputs) to open the command palette with `/` + that
  letter, enabling quick fuzzy menu navigation. Ported from the standalone
  `fuzzy_search` module — uninstall `fuzzy_search` if both are present to avoid
  duplicate listeners.

---

## 6. Maintenance & upgrade notes

- **Dark mode**: toggle **Dark Mode** in the user menu (avatar dropdown), or set
  **Theme → System / Light / Dark** under *My Preferences*. Uses the same
  `color_scheme` cookie + `web.assets_web_dark` bundle as Enterprise. Dark home
  menu uses `background-dark.jpg` (copied from Enterprise).
- **Re-theme**: colors/radii live in `scss/variables.scss` (native vars) and
  `scss/theme.scss` (CSS custom properties). Dark counterparts in `*.dark.scss`.
- **Odoo upgrades**: the JS ports mirror `web_enterprise`. If Odoo changes the
  Home Menu API, diff against `web_enterprise/static/src/webclient/home_menu/*`
  and update `js/home_menu*.js` / `xml/*.xml` accordingly. The navbar patch
  relies on the stable `.o_menu_toggle` / `.o_menu_brand` classes and the
  `web.NavBar` template structure.
- **Disable a piece**: comment its file out of `__manifest__.py`.

---

## 7. Intentionally skipped (Enterprise-only)

These Enterprise features were **not** ported because they depend on licensed
modules or SaaS infrastructure:

- Expiration / subscription panel on Home Menu
- Sysadmin message panel
- Promote Studio / Add Custom Field upsells
- Settings "Enterprise Edition" branding
- `session_info` subscription warnings (`ir_http` licensing fields)
