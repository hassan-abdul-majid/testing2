from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PatientBasic(models.Model):
    _name = "patient.basic"
    _description = "Patient Basic"

    name = fields.Char(
        string="Patient Name",
        required=True
    )

    patient_id = fields.Char(
        string="Patient ID",
        required=True,
        copy=False
    )

    age = fields.Integer(
        string="Age"
    )

    dob = fields.Date(
        string="Date of Birth"
    )

    phone = fields.Char(
        string="Phone"
    )

    blood_group = fields.Selection(
        [
            ("a+", "A+"),
            ("a-", "A-"),
            ("b+", "B+"),
            ("b-", "B-"),
            ("ab+", "AB+"),
            ("ab-", "AB-"),
            ("o+", "O+"),
            ("o-", "O-"),
        ],
        string="Blood Group"
    )

    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender"
    )

    visit_fee = fields.Float(
        string="Visit Fee"
    )

    status = fields.Selection(
        [
            ("admitted", "Admitted"),
            ("discharged", "Discharged"),
        ],
        string="Status",
        default="admitted"
    )

    notes = fields.Text(
        string="Notes"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
        ],
        string="State",
        default="draft",
    )

    def action_approve(self):
        self.write({"state": "approved"})
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Approved",
                "message": "Patient has been approved",
                "type": "success",
            },
        }

    @api.model
    def create(self, vals):

        print("===============")
        print("create function")
        print("===============")
        record = super().create(vals)

        print("Patient created successfully")
        print("ID:", record.id)
        print("Name:", record.name)
        print("Patient Id:", record.patient_id)
        print("Blood Group:", record.blood_group)

        return record

    def write(self, vals):
        print("===============")
        print(" write function ")
        print("===============")

        result = super().write(vals)

        for record in self:
            print("Patient updated successfully")
            print("ID:", record.id)
            print("Name", record.name)
            print("Patient Id:", record.patient_id)
            print("Blood Group:", record.blood_group)

        return result
    
    @api.constrains('visit_fee')
    def _visit_fee(self):
        for record in self:
            if record.visit_fee < 0:
                raise ValidationError("Visit fee cannot be negative")
    
