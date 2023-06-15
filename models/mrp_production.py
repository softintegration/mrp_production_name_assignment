# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, vals):
        # we have to do this to force the creation super method to ignore the auto assignment of the name
        vals.update({'name':'/'})
        mrp_production = super(MrpProduction, self).create(vals)
        if not mrp_production.picking_type_id.name_assignment_at_validation:
            mrp_production._assign_name()
        else:
            mrp_production.write({'name': _('New')})
        return mrp_production

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for each in self:
            if each.picking_type_id.name_assignment_at_validation and each.name == _('New'):each._assign_name()
        return res

    def _assign_name(self):
        for each in self:
            if each.picking_type_id:
                each.write({'name':each.picking_type_id.sequence_id.next_by_id()})
            else:
                each.write({'name':self.env['ir.sequence'].next_by_code('mrp.production') or _('New')})


