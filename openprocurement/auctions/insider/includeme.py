from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.insider.models import DGFInsider
from openprocurement.auctions.insider.adapters import AuctionInsiderConfigurator
from openprocurement.auctions.insider.constants import VIEW_LOCATIONS


def includeme(config):
    config.add_auction_procurementMethodType(DGFInsider)

    for view_module in VIEW_LOCATIONS:
        config.scan(view_module)

    config.registry.registerAdapter(
        AuctionInsiderConfigurator,
        (IAuction, IRequest),
        IContentConfigurator
    )

