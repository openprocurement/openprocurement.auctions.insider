# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import context_unpack
from openprocurement.auctions.dgf.utils import check_award_status

from openprocurement.auctions.flash.models import AUCTION_STAND_STILL_TIME
from openprocurement.auctions.insider.constants import (
    STAGE_TIMEDELTA,
    SERVICE_TIMEDELTA,
    BESTBID_TIMEDELTA,
    SEALEDBID_TIMEDELTA,
    SERVICE_TIMEDELTA
)
from barbecue import chef

from urllib import quote
from base64 import b64encode

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def generate_auction_url(request, bid_id=None):
    auction_module_url = request.registry.auction_module_url
    auction_id = request.validated['auction']['id']
    if bid_id:
        auction_id = request.validated['auction_id']
        signature = quote(b64encode(request.registry.signer.signature('{}_{}'.format(auction_id,bid_id))))
        return '{}/insider-auctions/{}/login?bidder_id={}&signature={}'.format(auction_module_url, auction_id, bid_id, signature)
    return '{}/insider-auctions/{}'.format(auction_module_url, auction_id)


def check_auction_status(request):
    auction = request.validated['auction']
    if auction.awards:
        awards_statuses = set([award.status for award in auction.awards])
    else:
        awards_statuses = set([""])
    if not awards_statuses.difference(set(['unsuccessful', 'cancelled'])):
        LOGGER.info('Switched auction {} to {}'.format(auction.id, 'unsuccessful'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_unsuccessful'}))
        auction.status = 'unsuccessful'
    if auction.contracts and auction.contracts[-1].status == 'active':
        LOGGER.info('Switched auction {} to {}'.format(auction.id, 'complete'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_complete'}))
        auction.status = 'complete'


def check_status(request):
    auction = request.validated['auction']
    now = get_now()
    for award in auction.awards:
        check_award_status(request, award, now)
    if auction.status == 'active.tendering' and auction.enquiryPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        auction.auctionUrl = generate_auction_url(request)
        return
    elif auction.status == 'active.awarded':
        standStillEnds = [
            a.complaintPeriod.endDate.astimezone(TZ)
            for a in auction.awards
            if a.complaintPeriod.endDate
        ]
        if not standStillEnds:
            return
        standStillEnd = max(standStillEnds)
        if standStillEnd <= now:
            check_auction_status(request)


def create_awards(request):
    auction = request.validated['auction']
    auction.status = 'active.qualification'
    now = get_now()
    auction.awardPeriod = type(auction).awardPeriod({'startDate': now})
    valid_bids = [bid for bid in auction.bids if bid['status'] != 'invalid']
    bids = chef(valid_bids, auction.features or [], [], True)

    for bid, status in zip(bids, ['pending.verification', 'pending.waiting']):
        bid = bid.serialize()
        award = type(auction).awards.model_class({
            '__parent__': request.context,
            'bid_id': bid['id'],
            'status': status,
            'date': now,
            'value': bid['value'],
            'suppliers': bid['tenderers'],
            'complaintPeriod': {'startDate': now}
        })
        if award.status == 'pending.verification':
            award.signingPeriod = award.paymentPeriod = award.verificationPeriod = {'startDate': now}
            request.response.headers['Location'] = request.route_url('{}:Auction Awards'.format(auction.procurementMethodType), auction_id=auction.id, award_id=award['id'])
        auction.awards.append(award)


def invalidate_empty_bids(auction):
    for bid in auction['bids']:
        if not bid.get('value') and bid['status'] == "active":
            bid['status'] = 'invalid'


def merge_auction_results(auction, request):
    if 'bids' not in auction:
        return
    for auction_bid in request.validated['data']['bids']:
        for bid in auction['bids']:
            if bid['id'] == auction_bid['id']:
                bid.update(auction_bid)
                break
    request.validated['data']['bids'] = auction['bids']


def calc_auction_end_time(stages, start):
    return start + stages * STAGE_TIMEDELTA + SERVICE_TIMEDELTA + SEALEDBID_TIMEDELTA + BESTBID_TIMEDELTA + AUCTION_STAND_STILL_TIME