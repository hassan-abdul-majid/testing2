from odoo import models, fields, _
from odoo.exceptions import AccessError, UserError


class StudentBasic(models.Model):
    _name = "student.admission"
    _description = "Student Admission"

    student_name = fields.Char(
        string="Student Name",
        required=True,
    )
    student_id = fields.Char(
        string="Student Id",
        required=True,
    )
    stdent_marks = fields.Char(
        string="Student Marks",
        required=True,
    )
    student_attendence = fields.Char(
        string="Student Attendence",
        required=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("admitted", "Admitted"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        required=True,
        copy=False,
    )

    def _check_admission_manager(self):
        if not (
            self.env.user.has_group("student_admission.group_admission_manager")
            or self.env.user.has_group("base.group_system")
        ):
            raise AccessError(_("Only Admission Managers can change admission status."))

    def action_confirm_admission(self):
        self._check_admission_manager()
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only draft admissions can be confirmed."))
        self.write({"state": "admitted"})

    def action_reject_admission(self):
        self._check_admission_manager()
        for record in self:
            if record.state != "draft":
                raise UserError(_("Only draft admissions can be rejected."))
        self.write({"state": "rejected"})
