import logging
from odoo import fields,models,api
from odoo.exceptions import  ValidationError
from odoo import _

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    x_effective_date = fields.Datetime(string='Effective Date (Manual)',help="Manually set the effective date for this stock transfer, used for stock valuation and currency conversion.")
    can_change_effective_date = fields.Boolean(
        compute='_compute_can_change_effective_date',store=False,help="Indicates if the current user has permission to change the effective date, based on the 'Change Effective Date Privilege' setting."
    )
    
    # check the checkbox is checked or not
    @api.depends_context('uid')
    def _compute_can_change_effective_date(self):
        current_user = self.env.user
        for rec in self:
            rec.can_change_effective_date = bool(current_user.change_effective_date)
        
    def action_open_effective_date_wizard(self):
        return {
        'type': 'ir.actions.act_window',
        'name': 'Change Effective Date',
        'res_model': 'change.effective.date.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_picking_id': self.id,
        },
        }
    def button_validate(self):
        res = super().button_validate()
        has_valuation_layer_model = 'stock.valuation.layer' in getattr(self.env.registry, 'models', {})
        for picking in self:
            if not picking.x_effective_date:
                raise ValidationError(_("Please set the Effective date before validating the transfer."))
            if picking.x_effective_date:
                picking.write({'date_done': picking.x_effective_date})
                # res = super().button_validate()
                for picking in self:
                    if picking.picking_type_id.code == 'incoming' and picking.purchase_id:
                        # use picking's effective date (not self)
                        effective_date = picking.x_effective_date
                        purchase_id = picking.purchase_id
                        currency_id = purchase_id.currency_id
                        # If the purchase currency is the company currency, no conversion needed
                        company_currency = picking.company_id.currency_id or self.env.company.currency_id
                        if currency_id == company_currency:
                            vendor_currency_rate_at_date = 1.0
                        else:
                            # find the latest rate on or before the effective date
                            rate = self.env['res.currency.rate'].search([
                                ('currency_id', '=', currency_id.id),
                                ('name', '<=', effective_date),
                            ], order='name desc', limit=1)
                            if not rate:
                                # fallback: take the latest available rate for that currency
                                rate = self.env['res.currency.rate'].search([
                                    ('currency_id', '=', currency_id.id),
                                ], order='name desc', limit=1)
                            if not rate:
                                raise ValidationError(_("No exchange rate found for the selected date."))
                            vendor_currency_rate_at_date = rate.inverse_company_rate
                        for move in picking.move_ids:
                            vendor_unit_price = move.purchase_line_id.price_unit 
                            product_qty = move.product_uom_qty
                            total_value = vendor_unit_price*vendor_currency_rate_at_date*product_qty
                            # product_price_in_company_currency = vendor_currency_rate_at_date*vendor_unit_price
                            # move.write({'price_unit': product_price_in_company_currency})
                            # raise ValidationError((f" before validation button method calling {move.price_unit}"))
                            valuation_layer = False
                            if has_valuation_layer_model:
                                valuation_layer = self.env['stock.valuation.layer'].search([
                                    ('stock_move_id', '=', move.id)
                                ], limit=1)
                            else:
                                _logger.warning("Model 'stock.valuation.layer' is not available in the registry; skipping valuation layer update for move %s", move.id)
                            if valuation_layer:
                                valuation_layer.write({
                                    'create_date':effective_date,
                                    'value': total_value,
                                    'unit_cost': total_value/product_qty,
                                })
                                try:
                                    self.env.cr.execute(
                                    "UPDATE stock_valuation_layer SET create_date = %s WHERE id = %s",
                                    (effective_date, valuation_layer.id) 
                                    )
                                    self.env.cr.commit()
                                except Exception as e:
                                    raise ValidationError(_(F"Error while updating the create_date: {e}"))
                                if has_valuation_layer_model:
                                    update_valuation_layer = self.env['stock.valuation.layer'].browse(valuation_layer.id)
                        # raise ValidationError((f"product name  is {move.product_id.name} product quantity is {move.product_uom_qty} and product price is {vendor_unit_price} and the total value in INR {total_value}"))
                    # raise ValidationError((f"currency id is {rate.inverse_company_rate}"))
                    elif picking.picking_type_id.code == 'outgoing':
                        effective_date = picking.x_effective_date
                        for move in picking.move_ids:
                            valuation_layer = False
                            if has_valuation_layer_model:
                                valuation_layer = self.env['stock.valuation.layer'].search([
                                    ('stock_move_id', '=', move.id)
                                ], limit=1)
                            else:
                                _logger.warning("Model 'stock.valuation.layer' is not available in the registry; skipping valuation layer update for move %s", move.id)

                            if valuation_layer:
                                self.env.cr.execute("""
                                    UPDATE stock_valuation_layer 
                                    SET create_date = %s 
                                    WHERE id = %s
                                """, (effective_date, valuation_layer.id))
                                self.env.cr.commit()
        return res