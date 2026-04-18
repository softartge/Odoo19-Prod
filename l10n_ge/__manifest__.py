{
    "name": "Georgian - Accounting",
    "version": "2.1.0",
    "category": "Accounting/Localizations/Account Charts",
    "description": """
    This is the base module to manage the accounting chart for Georgia in Odoo
    ==========================================================================

    Georgia accounting basic charts and localizations
    -------------------------------------------------
    Activates:

    - Chart of Accounts
    - Taxes
    - Tax Reports
    - Banks
    - Curencies
        """,
    "countries": ['ge'],
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts",
        "accountant",
        "currency_rate_live",
        "stock",
        "purchase",
        "sale_management",
    ],
    "auto_install": ['accountant'],
    "data": [
        "data/res_bank.xml",
        "data/res_currency.xml",
        "data/system_data.xml",
        ],

'installable': True,
'author': 'SofArt Ltd.',
'website': 'https://www.softart.ge',
'license': 'LGPL-3',
}

