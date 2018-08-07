import logging

from pyramid.interfaces import IRequest

from openprocurement.auctions.core.includeme import IContentConfigurator
from openprocurement.auctions.core.interfaces import IAuctionManager

from openprocurement.auctions.insider.models import DGFInsider, IInsiderAuction
from openprocurement.auctions.insider.adapters import (
    AuctionInsiderConfigurator,
    AuctionInsiderManagerAdapter
)
from openprocurement.auctions.insider.constants import (
    VIEW_LOCATIONS, DEFAULT_PROCUREMENT_METHOD_TYPE
)

LOGGER = logging.getLogger(__name__)


def includeme(config, plugin_config=None):
    procurement_method_types = plugin_config.get('aliases', [])
    if plugin_config.get('use_default', False):
        procurement_method_types.append(DEFAULT_PROCUREMENT_METHOD_TYPE)
    for procurementMethodType in procurement_method_types:
        config.add_auction_procurementMethodType(DGFInsider,
                                                 procurementMethodType)

    for view_module in VIEW_LOCATIONS:
        config.scan(view_module)

    config.registry.registerAdapter(
        AuctionInsiderConfigurator,
        (IInsiderAuction, IRequest),
        IContentConfigurator
    )
    config.registry.registerAdapter(
        AuctionInsiderManagerAdapter,
        (IInsiderAuction, ),
        IAuctionManager
    )

    LOGGER.info("Included openprocurement.auctions.insider plugin", extra={'MESSAGE_ID': 'included_plugin'})

    # add accreditation level
    config.registry.accreditations['auction'][DGFInsider._internal_type] = plugin_config['accreditation']
