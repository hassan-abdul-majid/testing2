from odoo import _, Command, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class StoreBill(models.Model):
    _name = "store.bill"
    _description = "Store Customer Bill"
    _order = "id desc"

    name = fields.Char(
        string="Bill Number",
        default="New",
        readonly=True,
        copy=False,
    )

    customer_name = fields.Char(
        string="Customer Name",
        required=True,
    )

    bill_date = fields.Date(
        string="Bill Date",
        default=fields.Date.today,
        required=True,
    )

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=lambda self: self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)],
            order="sequence, id",
            limit=1,
        ),
        domain="[('company_id', '=', company_id)]",
    )

    company_id = fields.Many2one(
        "res.company",
        related="warehouse_id.company_id",
        store=True,
        readonly=True,
    )

    line_ids = fields.One2many(
        "store.bill.line",
        "bill_id",
        string="Bill Products",
    )

    total_amount = fields.Float(
        string="Total Amount",
        compute="_compute_amounts",
        store=True,
    )

    discount_amount = fields.Float(
        string="Discount Amount",
        default=0.0,
    )

    net_amount = fields.Float(
        string="Net Amount",
        compute="_compute_amounts",
        store=True,
    )

    received_amount = fields.Float(
        string="Received Amount",
        default=0.0,
    )

    balance_amount = fields.Float(
        string="Remaining Balance",
        compute="_compute_amounts",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    stock_picking_id = fields.Many2one(
        "stock.picking",
        string="Delivery",
        readonly=True,
        copy=False,
    )

    stock_return_picking_id = fields.Many2one(
        "stock.picking",
        string="Return Transfer",
        readonly=True,
        copy=False,
    )

    @api.depends(
        "line_ids.subtotal",
        "discount_amount",
        "received_amount",
    )
    def _compute_amounts(self):
        for bill in self:
            total = sum(bill.line_ids.mapped("subtotal"))
            net = total - bill.discount_amount

            bill.total_amount = total
            bill.net_amount = net
            bill.balance_amount = net - bill.received_amount

    @api.constrains(
        "discount_amount",
        "received_amount",
        "line_ids",
    )
    def _check_bill_amounts(self):
        for bill in self:
            total = sum(bill.line_ids.mapped("subtotal"))

            if bill.discount_amount < 0:
                raise ValidationError(
                    "Discount cannot be negative."
                )

            if bill.discount_amount > total:
                raise ValidationError(
                    "Discount cannot exceed total amount."
                )

            if bill.received_amount < 0:
                raise ValidationError(
                    "Received amount cannot be negative."
                )

            if bill.received_amount > total - bill.discount_amount:
                raise ValidationError(
                    "Received amount cannot exceed net amount."
                )
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (
                vals.get("state", "draft") != "draft"
                or vals.get("stock_picking_id")
                or vals.get("stock_return_picking_id")
            ):
                raise UserError(
                    _("Bills must be created in draft without stock transfers.")
                )
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("store.bill")
                    or "New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if {
            "state",
            "stock_picking_id",
            "stock_return_picking_id",
        }.intersection(vals):
            raise UserError(
                _("Use the bill actions to change status or process stock transfers.")
            )

        protected_fields = {
            "name",
            "customer_name",
            "bill_date",
            "warehouse_id",
            "line_ids",
            "discount_amount",
            "received_amount",
        }
        if protected_fields.intersection(vals) and any(
            bill.state != "draft" for bill in self
        ):
            raise UserError(_("Confirmed or cancelled bills cannot be edited."))
        return super().write(vals)

    def unlink(self):
        if any(bill.state != "draft" for bill in self):
            raise UserError(_("Confirmed or cancelled bills cannot be deleted."))
        return super().unlink()

    def action_confirm(self):
        for bill in self:
            if bill.state in ("confirmed", "cancelled"):
                continue

            if not self.env.user.has_group("stock.group_stock_user"):
                raise UserError(
                    _(
                        "You need Inventory User access to confirm bills "
                        "and process stock deliveries."
                    )
                )

            if not bill.line_ids:
                raise ValidationError(
                    "Please add at least one product."
                )

            warehouse = bill.warehouse_id
            if not warehouse or not warehouse.out_type_id:
                raise UserError(
                    _("The selected warehouse has no outgoing operation type.")
                )

            quantities_by_product = {}
            for line in bill.line_ids:
                if line.quantity <= 0:
                    raise ValidationError(
                        _("Product quantity must be greater than zero.")
                    )
                if not line.product_id.is_storable:
                    raise ValidationError(
                        _("Only storable Inventory products can be billed.")
                    )
                if (
                    line.product_id.company_id
                    and line.product_id.company_id != warehouse.company_id
                ):
                    raise ValidationError(
                        _("%s belongs to a different company.")
                        % line.product_id.display_name
                    )
                quantities_by_product[line.product_id] = (
                    quantities_by_product.get(line.product_id, 0)
                    + line.quantity
                )

            quant_model = self.env["stock.quant"]
            for product, required_quantity in quantities_by_product.items():
                available_quantity = quant_model._get_available_quantity(
                    product, warehouse.lot_stock_id
                )
                if float_compare(
                    available_quantity,
                    required_quantity,
                    precision_rounding=product.uom_id.rounding,
                ) < 0:
                    raise ValidationError(
                        _(
                            "Not enough stock for %(product)s. "
                            "Available: %(available)s; requested: %(requested)s."
                        )
                        % {
                            "product": product.display_name,
                            "available": available_quantity,
                            "requested": required_quantity,
                        }
                    )

            customer_location = self.env.ref("stock.stock_location_customers")
            picking = self.env["stock.picking"].create(
                {
                    "picking_type_id": warehouse.out_type_id.id,
                    "location_id": warehouse.lot_stock_id.id,
                    "location_dest_id": customer_location.id,
                    "partner_id": False,
                    "origin": bill.name,
                    "company_id": warehouse.company_id.id,
                    "move_ids": [
                        Command.create(
                            {
                                "name": line.product_id.display_name,
                                "product_id": line.product_id.id,
                                "product_uom_qty": line.quantity,
                                "product_uom": line.product_id.uom_id.id,
                                "location_id": warehouse.lot_stock_id.id,
                                "location_dest_id": customer_location.id,
                                "company_id": warehouse.company_id.id,
                            }
                        )
                        for line in bill.line_ids
                    ],
                }
            )
            picking.action_confirm()
            picking.action_assign()

            for move in picking.move_ids:
                if float_compare(
                    move.quantity,
                    move.product_uom_qty,
                    precision_rounding=move.product_uom.rounding,
                ) < 0:
                    raise ValidationError(
                        _(
                            "Stock for %(product)s was reserved only partially. "
                            "The bill was not confirmed."
                        )
                        % {"product": move.product_id.display_name}
                    )

            validation_result = picking.button_validate()
            if validation_result is not True or picking.state != "done":
                raise UserError(
                    _(
                        "The Inventory delivery could not be validated. "
                        "Resolve the transfer requirements and try again."
                    )
                )

            super(StoreBill, bill).write(
                {
                    "stock_picking_id": picking.id,
                    "state": "confirmed",
                }
            )

    def action_cancel(self):
        for bill in self:
            if bill.state == "cancelled":
                continue
            if bill.state != "confirmed":
                raise UserError(_("Only confirmed bills can be cancelled."))
            if not self.env.user.has_group("stock.group_stock_user"):
                raise UserError(
                    _(
                        "You need Inventory User access to cancel bills "
                        "and process stock returns."
                    )
                )
            if not bill.stock_picking_id:
                raise UserError(
                    _(
                        "This bill predates Inventory integration and has no "
                        "delivery to return. It cannot be cancelled automatically."
                    )
                )
            if bill.stock_picking_id.state != "done":
                raise UserError(
                    _("The linked Inventory delivery is not completed.")
                )

            return_wizard = self.env["stock.return.picking"].with_context(
                active_model="stock.picking",
                active_id=bill.stock_picking_id.id,
                active_ids=bill.stock_picking_id.ids,
            ).create({"picking_id": bill.stock_picking_id.id})
            for return_line in return_wizard.product_return_moves:
                return_line.quantity = return_line.move_quantity

            return_action = return_wizard.action_create_returns()
            return_picking = self.env["stock.picking"].browse(
                return_action["res_id"]
            )
            validation_result = return_picking.button_validate()
            if validation_result is not True or return_picking.state != "done":
                raise UserError(
                    _(
                        "The Inventory return could not be validated. "
                        "Resolve the transfer requirements and try again."
                    )
                )

            super(StoreBill, bill).write(
                {
                    "stock_return_picking_id": return_picking.id,
                    "state": "cancelled",
                }
            )


class StoreBillLine(models.Model):
    _name = "store.bill.line"
    _description = "Store Bill Product Line"

    bill_id = fields.Many2one(
        "store.bill",
        string="Bill",
        required=True,
        ondelete="cascade",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('is_storable', '=', True)]",
    )

    quantity = fields.Integer(
        string="Quantity",
        default=1,
        required=True,
    )

    price_unit = fields.Float(
        string="Unit Price",
        required=True,
    )

    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
    )

    available_qty = fields.Float(
        string="Available Stock",
        compute="_compute_available_qty",
        digits="Product Unit of Measure",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price

    @api.model_create_multi
    def create(self, vals_list):
        bill_ids = [vals.get("bill_id") for vals in vals_list if vals.get("bill_id")]
        bills = self.env["store.bill"].browse(bill_ids)
        if any(bill.state != "draft" for bill in bills):
            raise UserError(_("Bill lines can only be added to draft bills."))
        return super().create(vals_list)

    def write(self, vals):
        target_bill = self.env["store.bill"].browse(vals.get("bill_id"))
        if (
            any(line.bill_id.state != "draft" for line in self)
            or (target_bill and target_bill.state != "draft")
        ):
            raise UserError(_("Bill lines on confirmed bills cannot be edited."))
        return super().write(vals)

    def unlink(self):
        if any(line.bill_id.state != "draft" for line in self):
            raise UserError(_("Bill lines on confirmed bills cannot be deleted."))
        return super().unlink()

    @api.depends("product_id", "bill_id.warehouse_id")
    def _compute_available_qty(self):
        quant_model = self.env["stock.quant"]
        for line in self:
            if line.product_id and line.bill_id.warehouse_id:
                line.available_qty = quant_model._get_available_quantity(
                    line.product_id, line.bill_id.warehouse_id.lot_stock_id
                )
            else:
                line.available_qty = 0.0

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit