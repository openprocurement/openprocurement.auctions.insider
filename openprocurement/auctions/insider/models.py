# -*- coding: utf-8 -*-
from datetime import timedelta
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.types import StringType, BooleanType, IntType, DateType, MD5Type
from schematics.types.compound import ModelType
from schematics.transforms import whitelist

from schematics.types.serializable import serializable
from zope.interface import implementer

from openprocurement.auctions.core.constants import (
    DGF_ELIGIBILITY_CRITERIA,
    DGF_PLATFORM_LEGAL_DETAILS,
    DGF_PLATFORM_LEGAL_DETAILS_FROM,
    DGF_ID_REQUIRED_FROM,
    DGF_DECISION_REQUIRED_FROM,
)
from openprocurement.auctions.core.models.schema import (
    Auction as BaseAuction,
    AuctionParameters as BaseAuctionParameters,
    Bid as BaseBid,
    ComplaintModelType,
    Feature,
    IAuction,
    ListType,
    Lot,
    Model,
    Period,
    RectificationPeriod,
    Value,
    dgfCancellation as Cancellation,
    dgfComplaint as Complaint,
    dgfDocument as Document,
    dgfItem as Item,
    get_auction,
    validate_features_uniq,
    validate_items_uniq,
    validate_lots_uniq,
    validate_not_available,
)
from openprocurement.auctions.core.models.roles import (
    dgf_auction_roles,
)
from openprocurement.auctions.core.plugins.awarding.v3.models import (
    Award
)
from openprocurement.auctions.core.plugins.contracting.v3.models import (
    Contract,
)
from openprocurement.auctions.core.utils import (
    rounding_shouldStartAfter_after_midnigth,
    AUCTIONS_COMPLAINT_STAND_STILL_TIME,
    calculate_business_date,
    SANDBOX_MODE,
    get_now,
    TZ,
)

from openprocurement.auctions.insider.constants import (
    DUTCH_PERIOD,
    NUMBER_OF_STAGES,
    QUICK_DUTCH_PERIOD,
    RECTIFICATION_PERIOD_DURATION,
)
from openprocurement.auctions.insider.utils import generate_auction_url, calc_auction_end_time


class AuctionAuctionPeriod(Period):
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
        return rounding_shouldStartAfter_after_midnigth(start_after, auction).isoformat()

    def validate_startDate(self, data, startDate):
        auction = get_auction(data['__parent__'])
        if not auction.revisions and not startDate:
            raise ValidationError(u'This field is required.')


class Bid(BaseBid):
    class Options:
        roles = {
            'create': whitelist('tenderers', 'status', 'qualified', 'eligible'),
            'edit': whitelist('status', 'tenderers'),
        }

    status = StringType(choices=['active', 'draft', 'invalid'], default='active')
    qualified = BooleanType(required=True, choices=[True])
    eligible = BooleanType(required=True, choices=[True])

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


class AuctionParameters(BaseAuctionParameters):
    class Options:
        roles = {
            'create': whitelist('type', 'dutchSteps'),
        }

    type = StringType(choices=['insider'], default='insider')
    dutchSteps = IntType(choices=[10, 20, 30, 40, 50, 60, 70, 80, 90, 99, 100], default=80)


@implementer(IAuction)
class IInsiderAuction(IAuction):
    """Marker interface for Insider auctions"""


@implementer(IInsiderAuction)
class DGFInsider(BaseAuction):
    """Data regarding auction process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""
    class Options:
        roles = dgf_auction_roles
    _procedure_type = "dgfInsider"
    awards = ListType(ModelType(Award), default=list())
    cancellations = ListType(ModelType(Cancellation), default=list())
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    dgfID = StringType()
    dgfDecisionID = StringType()
    dgfDecisionDate = DateType()
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the auction.
    enquiryPeriod = ModelType(Period)  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(Period)  # The period when the auction is open for submissions. The end date is the closing date for auction submissions.
    tenderAttempts = IntType(choices=[1, 2, 3, 4, 5, 6, 7, 8])
    status = StringType(choices=['draft', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    features = ListType(ModelType(Feature), validators=[validate_features_uniq, validate_not_available])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq, validate_not_available])
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_items_uniq])
    suspended = BooleanType()
    merchandisingObject = MD5Type()
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the auction.
    auctionPeriod = ModelType(AuctionAuctionPeriod, required=True, default={})
    auctionParameters = ModelType(AuctionParameters)
    minimalStep = ModelType(Value)

    eligibilityCriteria = StringType(default=DGF_ELIGIBILITY_CRITERIA['ua'])
    eligibilityCriteria_en = StringType(default=DGF_ELIGIBILITY_CRITERIA['en'])
    eligibilityCriteria_ru = StringType(default=DGF_ELIGIBILITY_CRITERIA['ru'])
    rectificationPeriod = ModelType(RectificationPeriod)

    def __acl__(self):
        return [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_auction_award'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_auction_documents'),
        ]

    def initialize(self):
        if not self.enquiryPeriod:
            self.enquiryPeriod = type(self).enquiryPeriod.model_class()
        if not self.tenderPeriod:
            self.tenderPeriod = type(self).tenderPeriod.model_class()
        now = get_now()
        start_date = TZ.localize(self.auctionPeriod.startDate.replace(tzinfo=None))
        self.auctionPeriod.startDate = None
        self.auctionPeriod.endDate = None
        self.tenderPeriod.startDate = self.enquiryPeriod.startDate = now
        pause_between_periods = start_date - (start_date.replace(hour=20, minute=0, second=0, microsecond=0) - timedelta(days=1))
        self.enquiryPeriod.endDate = calculate_business_date(start_date, -pause_between_periods, self).astimezone(TZ)
        time_before_tendering_end = (start_date.replace(hour=9, minute=30, second=0, microsecond=0) + DUTCH_PERIOD) - self.enquiryPeriod.endDate
        self.tenderPeriod.endDate = calculate_business_date(self.enquiryPeriod.endDate, time_before_tendering_end, self)
        if SANDBOX_MODE and self.submissionMethodDetails and 'quick' in self.submissionMethodDetails:
            self.tenderPeriod.endDate = (self.enquiryPeriod.endDate + QUICK_DUTCH_PERIOD).astimezone(TZ)
        self.auctionPeriod.startDate = None
        self.auctionPeriod.endDate = None
        self.date = now
        self.documents.append(type(self).documents.model_class(DGF_PLATFORM_LEGAL_DETAILS))
        if not self.auctionParameters:
            self.auctionParameters = type(self).auctionParameters.model_class()

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'auction':
            role = 'auction_{}'.format(request.method.lower())
        elif request.authenticated_role == 'contracting':
            role = 'contracting'
        else:  # on PATCH of the owner
            now = get_now()
            if self.status == 'active.tendering':
                if now in self.rectificationPeriod:
                    role = 'edit_active.tendering_during_rectificationPeriod'
                else:
                    role = 'edit_active.tendering_after_rectificationPeriod'
            else:
                role = 'edit_{0}'.format(self.status)
        return role

    @serializable(serialized_name='rectificationPeriod', serialize_when_none=False)
    def generate_rectificationPeriod(self):
        """Generate rectificationPeriod only when it not defined"""
        # avoid period generation if
        if (
            # it's already generated
            (
                getattr(self, 'rectificationPeriod', False)
                # and not just present, but actually holds some real value
                and self.rectificationPeriod.startDate is not None
            )
            # or trere's no period on that our code is dependant
            or getattr(self, 'tenderPeriod') is None
        ):
            return
        start = self.tenderPeriod.startDate
        end = calculate_business_date(start, RECTIFICATION_PERIOD_DURATION, self, working_days=True)

        period = RectificationPeriod()
        period.startDate = start
        period.endDate = end

        return period.serialize()

    def validate_documents(self, data, docs):
        if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_PLATFORM_LEGAL_DETAILS_FROM and \
                (docs and docs[0].documentType != 'x_dgfPlatformLegalDetails' or any([i.documentType == 'x_dgfPlatformLegalDetails' for i in docs[1:]])):
            raise ValidationError(u"First document should be document with x_dgfPlatformLegalDetails documentType")

    def validate_value(self, data, value):
        if value.currency != u'UAH':
            raise ValidationError(u"currency should be only UAH")

    def validate_dgfID(self, data, dgfID):
        if not dgfID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_ID_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_dgfDecisionID(self, data, dgfID):
        if not dgfID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_DECISION_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

    def validate_dgfDecisionDate(self, data, dgfID):
        if not dgfID:
            if (data.get('revisions')[0].date if data.get('revisions') else get_now()) > DGF_DECISION_REQUIRED_FROM:
                raise ValidationError(u'This field is required.')

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
                if award.status == 'pending':
                    checks.append(award.verificationPeriod.endDate.astimezone(TZ))
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
            from openprocurement.auctions.core.utils import calculate_business_date
            for complaint in self.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
            for award in self.awards:
                for complaint in award.complaints:
                    if complaint.status == 'claim' and complaint.dateSubmitted:
                        checks.append(calculate_business_date(complaint.dateSubmitted, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
                    elif complaint.status == 'answered' and complaint.dateAnswered:
                        checks.append(calculate_business_date(complaint.dateAnswered, AUCTIONS_COMPLAINT_STAND_STILL_TIME, self))
        return min(checks).isoformat() if checks else None
