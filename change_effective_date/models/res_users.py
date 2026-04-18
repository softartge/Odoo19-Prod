from odoo import models ,fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    change_effective_date = fields.Boolean(
        string='Change Effective Date Privilege',
        help='Enable this option to allow the user to change the effective date on stock transfers and update valuation accordingly.'
    )
    is_admin_settings = fields.Boolean(
        string='Is Admin Settings Group',
        compute='_compute_is_admin_settings',
        store=False
    )
   
    def _compute_is_admin_settings(self):
        admin_group = self.env.ref('base.group_system')
        for user in self:
            # Use has_group to correctly check group membership (includes implied groups)
            user.is_admin_settings = user.has_group('base.group_system')
            