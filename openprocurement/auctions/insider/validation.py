# -*- coding: utf-8 -*-
from openprocurement.auctions.core.validation import (
    update_logging_context,
    validate_data,
)


def validate_item_data(request, error_handler, **kwargs):
    update_logging_context(request, {'item_id': '__new__'})
    context = request.context
    model = type(context).items.model_class
    validate_data(request, model, "item")


def validate_patch_item_data(request, error_handler, **kwargs):
    update_logging_context(request, {'item_id': '__new__'})
    context = request.context
    model = context.__class__
    validate_data(request, model)
