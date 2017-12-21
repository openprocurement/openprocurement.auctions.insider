# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.insider.models import DGFInsider


class AuctionInsiderConfigurator(AuctionConfigurator):
    name = 'Auction Insider Configurator'
    model = DGFInsider