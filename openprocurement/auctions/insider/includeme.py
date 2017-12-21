from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.insider.models import DGFInsider
from openprocurement.auctions.insider.adapters import AuctionInsiderConfigurator


def includeme(config):
    config.add_auction_procurementMethodType(DGFInsider)
    config.scan("openprocurement.auctions.insider.views")
    config.registry.registerAdapter(AuctionInsiderConfigurator, (IAuction, IRequest),
                                    IContentConfigurator)
