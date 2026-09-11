# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

from ..models.account_move import VerifactuValidationError


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def validate_move(self):
        if self.env.context.get("active_model") == "account.move":
            domain = [
                ("id", "in", self.env.context.get("active_ids", [])),
                ("state", "=", "draft"),
            ]
        elif self.env.context.get("active_model") == "account.journal":
            domain = [
                ("journal_id", "=", self.env.context.get("active_id")),
                ("state", "=", "draft"),
            ]
        else:
            return super().validate_move()

        moves = self.env["account.move"].search(domain).filtered("line_ids")
        try:
            moves._raise_verifactu_errors(moves._verifactu_preflight_errors())
            with self.env.cr.savepoint():
                return super().validate_move()
        except VerifactuValidationError as error:
            action = moves._open_verifactu_warning(error)
            action["context"].update(
                {
                    "verifactu_post_directly": True,
                    "verifactu_force_post": self.force_post,
                }
            )
            return action
