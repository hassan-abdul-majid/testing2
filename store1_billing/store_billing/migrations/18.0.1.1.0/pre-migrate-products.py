from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    cr.execute("SELECT to_regclass('public.store_product')")
    if not cr.fetchone()[0]:
        return

    cr.execute(
        """
        SELECT store_product.id, store_product.name,
               COUNT(product_product.id), MIN(product_product.id)
          FROM store_product
          LEFT JOIN product_template
            ON EXISTS (
                SELECT 1
                  FROM jsonb_each_text(product_template.name)
                       AS product_name(language, value)
                 WHERE product_name.value = store_product.name
            )
          LEFT JOIN product_product
            ON product_product.product_tmpl_id = product_template.id
         GROUP BY store_product.id, store_product.name
        """
    )
    mappings = cr.fetchall()
    unresolved = [
        name for _legacy_id, name, match_count, _product_id in mappings
        if match_count != 1
    ]
    if unresolved:
        raise RuntimeError(
            "Store Billing upgrade requires exactly one Inventory product "
            "for each legacy product name. Missing or ambiguous names: %s"
            % ", ".join(sorted(set(unresolved)))
        )

    cr.execute(
        "ALTER TABLE store_bill_line "
        "DROP CONSTRAINT IF EXISTS store_bill_line_product_id_fkey"
    )
    cr.executemany(
        """
        UPDATE store_bill_line
           SET product_id = %s
         WHERE product_id = %s
        """,
        [
            (product_id, legacy_id)
            for legacy_id, _name, _match_count, product_id in mappings
        ],
    )

    env = api.Environment(cr, SUPERUSER_ID, {})
    for xml_id in (
        "store_products_menu",
        "store_product_action",
        "store_product_list",
        "store_product_form",
        "store_product_search",
    ):
        record = env.ref(
            "store_billing.%s" % xml_id,
            raise_if_not_found=False,
        )
        if record:
            record.unlink()
