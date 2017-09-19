# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.models import (
    Model, ListType
)
from openprocurement.api.models import Value
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.dgf.models import (
    DGFFinancialAssets as BaseAuction,
    get_auction, Bid as BaseBid,
    Organization
)

from openprocurement.auctions.insider.utils import generate_url


class Bid(BaseBid):
    tenderers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)

    class Options:
        roles = {
            'create': whitelist('tenderers', 'parameters', 'lotValues', 'status', 'qualified', 'eligible'),
        }

    def validate_value(self, data, value):
        if isinstance(data['__parent__'], Model):
            auction = data['__parent__']
            if not value:
                return
            if auction.value.amount > value.amount:
                raise ValidationError(u"value of bid should be greater than value of auction")
            if auction.get('value').currency != value.currency:
                raise ValidationError(u"currency of bid should be identical to currency of value of auction")
            if auction.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of auction")

    @serializable(serialized_name="participationUrl", serialize_when_none=False)
    def participation_url(self):
        if not self.participationUrl and self.status != "draft":
            request = get_auction(self).__parent__.request
            url = generate_url(request, bid_id=self.id)
            return url


@implementer(IAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    procurementMethodType = StringType(default="dgfInsider")
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    minimalStep = ModelType(Value)

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def auction_minimalStep(self):
        return Value(dict(amount=0))

    @serializable(serialized_name="auctionUrl", serialize_when_none=False)
    def auction_url(self):
        if not self.auctionUrl and self.status != "draft" and self.id:
            root = self.__parent__
            request = root.request
            url = generate_url(request, auction_id=self.id)
            return url

DGFInsider = Auction

