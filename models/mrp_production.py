# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_backorder_productions(self, close_mo=True):
        """ Inherit this method to inject paramater in the context so that the creation method be aware about the creation of backorder"""
        return super(MrpProduction,self.with_context(create_backorder=True))._generate_backorder_productions(close_mo=close_mo)

    @api.model
    def create(self, vals):
        # we have to do this to force the creation super method to ignore the auto assignment of the name
        if self.env.context.get('create_backorder',False):
            return super(MrpProduction, self).create(vals)
        vals.update({'name': '/'})
        mrp_production = super(MrpProduction, self).create(vals)
        if not mrp_production.picking_type_id.name_assignment_at_validation:
            mrp_production._assign_name()
        else:
            mrp_production.write({'name': False})
        return mrp_production

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for each in self:
            if each.picking_type_id.name_assignment_at_validation and not each.name:
                each._assign_name()
            elif not each.picking_type_id.name_assignment_at_validation and not each.name:
                # in this case the configuration of assignement was at validation when the user has create the manufacturing order
                # and has been changed before the confirmation of the manufacturing,this is dead end,to prevent that ,we have to get the default sequence
                # of the manufacturing operation in this case
                picking_type_id = self.env['stock.picking.type'].browse(each._get_default_picking_type())
                if picking_type_id:
                    each.name = picking_type_id.sequence_id.next_by_id()
                else:
                    each.name = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
            each.move_raw_ids.write({'name': each.name})
            each.move_finished_ids.write({'name': each.name})
        return res

    def _assign_name(self):
        for each in self:
            if each.picking_type_id:
                each.write({'name': each.picking_type_id.sequence_id.next_by_id()})
            else:
                each.write({'name': self.env['ir.sequence'].next_by_code('mrp.production') or _('New')})

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        """ inherit this method to prevent put NULL value in name because it follow the production order"""
        res = super(MrpProduction,self)._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id=operation_id,
                                           bom_line=bom_line)
        if not res['name']:
            res['name'] = self.env['product.product'].browse(res['product_id']).display_name
        return res

    def _get_move_finished_values(self, product_id, product_uom_qty, product_uom, operation_id=False,
                                  byproduct_id=False, cost_share=0):
        """ inherit this method to prevent put NULL value in name because it follow the production order """
        res = super(MrpProduction,self)._get_move_finished_values(product_id, product_uom_qty, product_uom, operation_id=operation_id,
                                  byproduct_id=byproduct_id, cost_share=cost_share)
        if not res['name']:
            res['name'] = self.env['product.product'].browse(res['product_id']).display_name
        return res

