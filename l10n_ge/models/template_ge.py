# Part of Georgian Accounting Localisation. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo.addons.account.models.chart_template import template

class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'


    @template('ge')
    def _get_ge_template_data(self):
        return {
            'name': ('Base COA'),
            'code_digits': '4',
            'property_account_receivable_id': 'ge_1410',
            'property_account_payable_id': 'ge_3110',
            'downpayment_account_id': 'ge_1480',
            }

    @template('ge', 'res.company')
    def _get_ge_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.ge',
                'anglo_saxon_accounting': True,
                'account_storno': 'true',
                'autopost_bills': 'never',
                'cost_method': 'average',
                'account_price_include': 'tax_included',
                'inventory_period': 'manual',
                'inventory_valuation': 'real_time',
                'tax_calculation_rounding_method': 'round_per_line',
                'expense_account_id': 'ge_7210',
                'income_account_id': 'ge_6110',
                'account_default_pos_receivable_account_id': 'ge_1411',
                'income_currency_exchange_account_id': 'ge_8180',
                'expense_currency_exchange_account_id': 'ge_8280',
                'account_journal_early_pay_discount_loss_account_id': 'ge_6120',
                'account_journal_early_pay_discount_gain_account_id': 'ge_8130',
                'income_account_id': 'ge_6110',
                'expense_account_id': 'ge_7210',
                'account_stock_journal_id': 'inventory_valuation',
                'account_stock_valuation_id': 'ge_1610',
                'transfer_account_code_prefix': '1295',
                'cash_account_code_prefix': '1110',
                'bank_account_code_prefix': '1210',
                'deferred_expense_account_id': 'ge_1920',
                'deferred_revenue_account_id': 'ge_4410',



            },
        }

