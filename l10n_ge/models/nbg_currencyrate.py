from odoo import models, fields, api
import requests
import datetime
import logging
import pytz


_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_provider = fields.Selection(
        selection_add=[('nbg', '[GE] National Bank of Georgia')],
        ondelete={'nbg': 'set default'},
        default='nbg'
    )

    def _get_available_currency_providers(self):
        # We call super to get the standard ones, then force 'nbg' in.
        providers = super(ResCompany, self)._get_available_cucrency_providers()
        if 'nbg' not in [p[0] for p in providers]:
            providers.append(('nbg', '[GE] National Bank of Georgia'))
        return providers

    @api.depends('country_id')
    def _compute_currency_provider(self):
        # Run the original logic first
        super(ResCompany, self)._compute_currency_provider()

        for record in self:
            # If the company is in Georgia, force the provider to NBG
            if record.country_id.code == 'ka_GE':
                record.currency_provider = 'nbg'


    @api.model
    def _parse_nbg_data(self, available_currencies):
        """ This method is used to update the currencies by using
        National Bank of Georgia (NBG) service provider. Rates are given
        against GEL.
        """


        available_currency_names = available_currencies.mapped('name')
        currency_rates_entries = []
        rates = {}
        request_url = 'https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json'
        response = requests.get(request_url, timeout=30)

        _logger.info("RESPONSE TYPE: %s", type(response))

        response.raise_for_status()
        data = response.json()
        currency_rates_entries.extend(data[0].get('currencies', []))

        for currency_rate_entry in currency_rates_entries:
            currency_code = currency_rate_entry.get('code')
            rate = currency_rate_entry.get('rate')
            date = currency_rate_entry.get('validFromDate')
            qty = currency_rate_entry.get('quantity')

            date_obj = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').date()

            if currency_code in available_currency_names and rate:
                normalized_rate = float(qty) / float(rate)
                rates[currency_code] = (normalized_rate, date_obj)

        # Include GEL with a fixed rate of 1.0
        rates['GEL'] = (1.0, datetime.datetime.now().date())
        return rates
