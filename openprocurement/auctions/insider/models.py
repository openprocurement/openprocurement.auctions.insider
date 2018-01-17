# -*- coding: utf-8 -*-
from datetime import timedelta
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types.serializable import serializable
from zope.interface import implementer
from openprocurement.api.models import (
    Model,
    ListType
)

from openprocurement.api.utils import calculate_business_date
from openprocurement.api.models import (
    get_now,
    Value,
    Period,
    TZ,
    SANDBOX_MODE
)
from openprocurement.auctions.core.models import IAuction
from openprocurement.auctions.flash.models import COMPLAINT_STAND_STILL_TIME
from openprocurement.auctions.dgf.models import (
    DGFFinancialAssets as BaseAuction,
    get_auction, Bid as BaseBid,
    Organization,
    AuctionAuctionPeriod as BaseAuctionPeriod,
    DGF_PLATFORM_LEGAL_DETAILS,
    rounding_shouldStartAfter,
)

from openprocurement.auctions.insider.utils import generate_auction_url, calc_auction_end_time
from openprocurement.auctions.insider.constants import (
    DUTCH_PERIOD,
    QUICK_DUTCH_PERIOD,
    NUMBER_OF_STAGES
)


class AuctionAuctionPeriod(BaseAuctionPeriod):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        auction = self.__parent__
        if auction.status not in ['active.tendering', 'active.auction']:
            return
        if self.startDate and get_now() > calc_auction_end_time(NUMBER_OF_STAGES, self.startDate):
            start_after = calc_auction_end_time(NUMBER_OF_STAGES, self.startDate)
        elif auction.enquiryPeriod and auction.enquiryPeriod.endDate:
            start_after = auction.enquiryPeriod.endDate
        else:
            return
        return rounding_shouldStartAfter(start_after, auction).isoformat()

    def validate_startDate(self, data, startDate):
        auction = get_auction(data['__parent__'])
        if not auction.revisions and not startDate:
            raise ValidationError(u'This field is required.')


class Bid(BaseBid):
    tenderers = ListType(ModelType(Organization), required=True, min_size=1, max_size=1)

    class Options:
        roles = {
            'create': whitelist('tenderers', 'status', 'qualified', 'eligible'),
            'edit': whitelist('status', 'tenderers'),
        }

    def validate_value(self, data, value):
        if isinstance(data['__parent__'], Model):
            auction = data['__parent__']
            if not value:
                return
            if auction.get('value').currency != value.currency:
                raise ValidationError(u"currency of bid should be identical to currency of value of auction")
            if auction.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of auction")

    @serializable(serialized_name="participationUrl", serialize_when_none=False)
    def participation_url(self):
        if not self.participationUrl and self.status == "active":
            request = get_auction(self).__parent__.request
            url = generate_auction_url(request, bid_id=str(self.id))
            return url


@implementer(IAuction)
class Auction(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    procurementMethodType = StringType(default="dgfInsider")
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    auctionPeriod = ModelType(AuctionAuctionPeriod, required=True, default={})
    minimalStep = ModelType(Value)

    def initialize(self):
        if not self.enquiryPeriod:
            self.enquiryPeriod = type(self).enquiryPeriod.model_class()
        if not self.tenderPeriod:
            self.tenderPeriod = type(self).tenderPeriod.model_class()
        now = get_now()
        self.tenderPeriod.startDate = self.enquiryPeriod.startDate = now
        pause_between_periods = self.auctionPeriod.startDate - (self.auctionPeriod.startDate.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1))
        self.enquiryPeriod.endDate = calculate_business_date(self.auctionPeriod.startDate, -pause_between_periods, self).astimezone(TZ)
        time_before_tendering_end = (self.auctionPeriod.startDate.replace(hour=9, minute=30, second=0, microsecond=0) + DUTCH_PERIOD) - self.enquiryPeriod.endDate
        self.tenderPeriod.endDate = calculate_business_date(self.enquiryPeriod.endDate, time_before_tendering_end, self)
        if SANDBOX_MODE and self.submissionMethodDetails and 'quick' in self.submissionMethodDetails:
            self.tenderPeriod.endDate = (self.enquiryPeriod.endDate + QUICK_DUTCH_PERIOD).astimezone(TZ)
        self.auctionPeriod.startDate = None
        self.auctionPeriod.endDate = None
        self.date = now
        self.documents.append(type(self).documents.model_class(DGF_PLATFORM_LEGAL_DETAILS))

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def auction_minimalStep(self):
        return Value(dict(amount=0))

    @serializable(serialized_name="tenderPeriod", type=ModelType(Period))
    def tender_Period(self):
        if self.tenderPeriod and self.auctionPeriod.startDate:
            end_date = calculate_business_date(self.auctionPeriod.startDate, DUTCH_PERIOD, self)
            if SANDBOX_MODE and self.submissionMethodDetails and 'quick' in self.submissionMethodDetails:
                end_date = self.auctionPeriod.startDate + QUICK_DUTCH_PERIOD
            if self.auctionPeriod.endDate and self.auctionPeriod.endDate <= self.tenderPeriod.endDate:
                end_date = self.auctionPeriod.endDate.astimezone(TZ)
            self.tenderPeriod.endDate = end_date
        return self.tenderPeriod

    @serializable(serialize_when_none=False)
    def next_check(self):
        if self.suspended:
            return None
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.enquiryPeriod and self.enquiryPeriod.endDate:
            checks.append(self.enquiryPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.auction' and self.auctionPeriod and self.auctionPeriod.startDate and not self.auctionPeriod.endDate:
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(NUMBER_OF_STAGES, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(NUMBER_OF_STAGES, self.auctionPeriod.startDate).astimezone(TZ))
        elif not self.lots and self.status == 'active.qualification':
            for award in self.awards:
                if award.status == 'pending.verification':
                    checks.append(award.verificationPeriod.endDate.astimezone(TZ))
                elif award.status == 'pending.payment':
                    checks.append(award.paymentPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.awarded' and not any([
                i.status in self.block_complaint_status
                for i in self.complaints
            ]) and not any([
                i.status in self.block_complaint_status
                for a in self.awards
                for i in a.complaints
            ]):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod.endDate
            ]
            for award in self.awards:
                if award.status == 'active':
                    checks.append(award.signingPeriod.endDate.astimezone(TZ))

            last_award_status = self.awards[-1].status if self.awards else ''
            if standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
        if self.status.startswith('active'):
            from openprocurement.api.utils import calculate_business_date
            for complaint in self.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, self))
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self))
            for award in self.awards:
                for complaint in award.complaints:
                    if complaint.status == 'claim' and complaint.dateSubmitted:
                        checks.append(calculate_business_date(complaint.dateSubmitted, COMPLAINT_STAND_STILL_TIME, self))
                    elif complaint.status == 'answered' and complaint.dateAnswered:
                        checks.append(calculate_business_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self))
        return min(checks).isoformat() if checks else None


DGFInsider = Auction
