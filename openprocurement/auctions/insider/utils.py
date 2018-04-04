# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.api.models import get_now, TZ
from openprocurement.api.utils import context_unpack

from openprocurement.auctions.core.models import AUCTION_STAND_STILL_TIME
from openprocurement.auctions.insider.constants import (
    STAGE_TIMEDELTA,
    SERVICE_TIMEDELTA,
    BESTBID_TIMEDELTA,
    SEALEDBID_TIMEDELTA,
    SERVICE_TIMEDELTA
)

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
        request.content_configurator.check_award_status(request, award, now)
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
