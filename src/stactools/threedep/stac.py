from typing import Optional

from pystac import Item
from stactools.core import create
from stactools.core.io import ReadHrefModifier

from stactools.threedep.metadata import Metadata


def create_item(
    href: str,
    read_href_modifier: Optional[ReadHrefModifier] = None,
    base: Optional[str] = None,
) -> Item:
    """Creates a STAC item from an href to an XML metadata file."""
    metadata = Metadata.from_href(href, read_href_modifier)
    return create_item_from_metadata(metadata, read_href_modifier, base)


def create_item_from_product_and_id(
    product: str,
    id: str,
    read_href_modifier: Optional[ReadHrefModifier] = None,
    base: Optional[str] = None,
) -> Item:
    """Creates a STAC item from a product (e.g. "1") and an ID (e.g. "n41w106")."""
    metadata = Metadata.from_product_and_id(product, id)
    return create_item_from_metadata(metadata, read_href_modifier, base)


def create_item_from_metadata(
    metadata: Metadata,
    read_href_modifier: Optional[ReadHrefModifier] = None,
    base: Optional[str] = None,
) -> Item:
    """Creates a STAC item from Metadata."""
    href = metadata.asset_href_with_extension(base, "tif")
    item = create.item(href, read_href_modifier)
    item.id = metadata.stac_id
    end_datetime = metadata.end_datetime
    item.datetime = end_datetime
    item.common_metadata.start_datetime = metadata.start_datetime
    item.common_metadata.end_datetime = metadata.end_datetime
    item.links.append(metadata.via_link(base))
    item.assets["data"] = metadata.data_asset(base)
    item.assets["metadata"] = metadata.metadata_asset(base)
    item.assets["thumbnail"] = metadata.thumbnail_asset(base)
    item.assets["gpkg"] = metadata.gpkg_asset(base)
    item.properties["threedep:region"] = metadata.region
    return item
