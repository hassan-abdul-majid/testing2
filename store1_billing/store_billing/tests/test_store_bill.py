from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase
from odoo.tools import float_compare


class TestStoreBillStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)],
            order="sequence, id",
            limit=1,
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Store bill stock test",
                "is_storable": True,
                "list_price": 12.5,
            }
        ).product_variant_id
        cls.quant_model = cls.env["stock.quant"]

    def _create_bill(self, quantity):
        self.quant_model._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, quantity=100
        )
        bill = self.env["store.bill"].create(
            {
                "customer_name": "Stock Test Customer",
                "warehouse_id": self.warehouse.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": quantity,
                            "price_unit": self.product.lst_price,
                        },
                    )
                ],
            }
        )
        return bill

    def _available_quantity(self):
        return self.quant_model._get_available_quantity(
            self.product, self.warehouse.lot_stock_id
        )

    def test_confirm_decrements_stock_once_and_cancel_returns_it(self):
        bill = self._create_bill(5)

        bill.action_confirm()
        self.assertEqual(bill.state, "confirmed")
        self.assertEqual(bill.stock_picking_id.state, "done")
        self.assertEqual(self._available_quantity(), 95)

        bill.action_confirm()
        self.assertEqual(self._available_quantity(), 95)

        bill.action_cancel()
        self.assertEqual(bill.state, "cancelled")
        self.assertEqual(bill.stock_return_picking_id.state, "done")
        self.assertEqual(self._available_quantity(), 100)

        bill.action_cancel()
        self.assertEqual(self._available_quantity(), 100)

    def test_confirmation_rejects_quantity_over_available_stock(self):
        bill = self._create_bill(101)

        with self.assertRaises(ValidationError):
            with self.cr.savepoint():
                bill.action_confirm()

        self.assertEqual(bill.state, "draft")
        self.assertFalse(bill.stock_picking_id)
        self.assertEqual(self._available_quantity(), 100)

    def test_confirmed_bill_cannot_be_forged_or_edited(self):
        bill = self._create_bill(2)

        with self.assertRaises(UserError):
            bill.write({"state": "confirmed"})
        self.assertEqual(bill.state, "draft")
        self.assertEqual(self._available_quantity(), 100)

        bill.action_confirm()
        with self.assertRaises(UserError):
            bill.line_ids.write({"quantity": 3})
        self.assertEqual(bill.line_ids.quantity, 2)
        self.assertEqual(self._available_quantity(), 98)

    def test_bill_amounts_use_the_inventory_product_price(self):
        bill = self._create_bill(4)

        self.assertEqual(bill.line_ids.price_unit, 12.5)
        self.assertEqual(bill.total_amount, 50)
        self.assertEqual(
            float_compare(
                bill.line_ids.available_qty,
                100,
                precision_rounding=self.product.uom_id.rounding,
            ),
            0,
        )
