# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from markupsafe import Markup, escape

from odoo import _, fields, models


class L10nEsVerifactuPostWarning(models.TransientModel):
    _name = "l10n_es_verifactu_oca.post_warning"
    _description = "Conscious VERI*FACTU invoice emission warning"

    move_ids = fields.Many2many(
        comodel_name="account.move",
        relation="l10n_es_verifactu_oca_warning_move_rel",
        string="Invoices",
        required=True,
    )
    message = fields.Text(string="Warnings", required=True, readonly=True)

    def action_confirm(self):
        self.ensure_one()
        moves = self.move_ids.exists().with_context(skip_verifactu_checks=True)
        if self.env.context.get("verifactu_post_directly"):
            force_post = self.env.context.get("verifactu_force_post", False)
            if force_post:
                moves.auto_post = "no"
            moves._post(not force_post)
            result = False
        else:
            result = moves.action_post()
        audit_message = Markup("<p>%s</p><pre>%s</pre>") % (
            escape(
                _(
                    "The invoice was consciously posted despite the following "
                    "VERI*FACTU warnings:"
                )
            ),
            escape(self.message),
        )
        for move in moves:
            move.message_post(body=audit_message)
        return result or {"type": "ir.actions.act_window_close"}

    def action_cancel(self):
        return {"type": "ir.actions.act_window_close"}
