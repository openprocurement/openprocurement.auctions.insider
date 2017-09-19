# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution
from openprocurement.api.models import get_now
from openprocurement.api.utils import context_unpack
from openprocurement.auctions.core.utils import (
    remove_draft_bids,
)
from openprocurement.auctions.dgf.utils import check_award_status
from barbecue import chef

from urllib import quote
from base64 import b64encode


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def generate_url(request, bid_id=None, auction_id=None):
    auction_module_url = request.registry.auction_module_url
    if bid_id:
        auction_id = request.validated['auction_id']
        signature = quote(b64encode(request.registry.signer.signature(bid_id)))
        return '{}/insider-auctions/{}/login?bidder_id={}&signature={}'.format(auction_module_url, auction_id, bid_id, signature)
    return '{}/insider-auctions/{}'.format(auction_module_url, auction_id)


def check_bids(request):
    auction = request.validated['auction']
    auction.status = 'unsuccessful'
    # if auction.numberOfBids < 2:
    #     if auction.auctionPeriod and auction.auctionPeriod.startDate:
    #         auction.auctionPeriod.startDate = None
    #     auction.status = 'unsuccessful'


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
    if auction.status == 'active.tendering' and auction.tenderPeriod.endDate <= now:
        LOGGER.info('Switched auction {} to {}'.format(auction['id'], 'active.auction'),
                    extra=context_unpack(request, {'MESSAGE_ID': 'switched_auction_active.auction'}))
        auction.status = 'active.auction'
        remove_draft_bids(request)
        check_bids(request)
        # if auction.numberOfBids < 2 and auction.auctionPeriod:
        #     auction.auctionPeriod.startDate = None
        return


def invalidate_bids_under_threshold(auction):
    value_threshold = round(auction['value']['amount'] + auction['minimalStep']['amount'], 2)
    for bid in auction['bids']:
        if not bid.get('value') or bid['value']['amount'] < value_threshold:
            bid['status'] = 'invalid'


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