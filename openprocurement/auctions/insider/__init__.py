from openprocurement.auctions.insider.models import DGFOtherAssets, DGFFinancialAssets


def includeme(config):
    config.add_auction_procurementMethodType(DGFOtherAssets)
    config.scan("openprocurement.auctions.insider.views.other")

    config.add_auction_procurementMethodType(DGFFinancialAssets)
    config.scan("openprocurement.auctions.insider.views.financial")
