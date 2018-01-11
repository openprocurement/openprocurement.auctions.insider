# -*- coding: utf-8 -*-
from openprocurement.auctions.core.adapters import AuctionConfigurator
from openprocurement.auctions.insider.models import DGFInsider
from openprocurement.auctions.core.plugins.awarding.v2.utils import create_awards_insider
from openprocurement.auctions.core.plugins.awarding.v2.models import Award


class AuctionInsiderConfigurator(AuctionConfigurator):
    name = 'Auction Insider Configurator'
    model = DGFInsider
    award_model = Award

    def add_award(self):
        return create_awards_insider(self.request)
