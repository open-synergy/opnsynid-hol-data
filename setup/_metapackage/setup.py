import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-open-synergy-opnsynid-hol-data",
    description="Meta package for open-synergy-opnsynid-hol-data Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-hol_account_financial_report',
        'odoo11-addon-hol_account_invoice_partner_id',
        'odoo11-addon-hol_account_invoice_subscription_type',
        'odoo11-addon-hol_account_type_data',
        'odoo11-addon-hol_crm_lead_brand',
        'odoo11-addon-hol_crm_lead_status_check_data',
        'odoo11-addon-hol_efaktur',
        'odoo11-addon-hol_fix_signup_token',
        'odoo11-addon-hol_invoice_segmentation_report',
        'odoo11-addon-hol_klik_pajak',
        'odoo11-addon-hol_partner_contact_department_data',
        'odoo11-addon-hol_stripe',
        'odoo11-addon-hol_subscription_disable_track_field',
        'odoo11-addon-hol_subscription_no_schedule_activity',
        'odoo11-addon-hol_subscription_supporting_document',
        'odoo11-addon-hol_subscription_user_info',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
