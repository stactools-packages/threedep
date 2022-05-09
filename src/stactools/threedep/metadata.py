import datetime
from typing import Optional, Union

from pystac import Asset, Link, MediaType
from stactools.core.io import ReadHrefModifier
from stactools.core.io.xml import XmlElement

from stactools.threedep import utils
from stactools.threedep.constants import DEFAULT_BASE


class Metadata:
    """3DEP file metadata."""

    @classmethod
    def from_href(
        cls, href: str, read_href_modifier: Optional[ReadHrefModifier] = None
    ) -> "Metadata":
        """Creates a metadata from an href to the XML metadata file."""
        xml_element = XmlElement.from_file(href, read_href_modifier)
        return cls(xml_element)

    @classmethod
    def from_product_and_id(
        cls, product: str, id: str, base: Optional[str] = None
    ) -> "Metadata":
        """Creates a Metadata from a product and id."""
        if base is None:
            base = DEFAULT_BASE
        href = utils.path(product, id, extension="xml", base=base)
        return cls.from_href(href)

    def __init__(self, xml: XmlElement):
        """Creates a new metadata object from XML metadata."""
        self.title = xml.find_text_or_throw(
            "./idinfo/citation/citeinfo/title", _missing_element
        )
        self.description = xml.find_text_or_throw(
            "./idinfo/descript/abstract", _missing_element
        )
        self.pubdate = xml.find_text_or_throw(
            "./idinfo/citation/citeinfo/pubdate", _missing_element
        )
        self.begdate = xml.find_text_or_throw(
            "./idinfo/timeperd/timeinfo/rngdates/begdate", _missing_element
        )
        self.enddate = xml.find_text_or_throw(
            "./idinfo/timeperd/timeinfo/rngdates/enddate", _missing_element
        )
        self.current = xml.find_text_or_throw(
            "./idinfo/timeperd/current", _missing_element
        )
        self.rowcount = xml.find_text_or_throw(
            "./spdoinfo/rastinfo/rowcount", _missing_element
        )
        self.colcount = xml.find_text_or_throw(
            "./spdoinfo/rastinfo/colcount", _missing_element
        )
        self.latres = xml.find_text_or_throw(
            "./spref/horizsys/geograph/latres", _missing_element
        )
        self.longres = xml.find_text_or_throw(
            "./spref/horizsys/geograph/longres", _missing_element
        )
        tiff_href = xml.find_text_or_throw(
            "./distinfo/stdorder/digform/digtopt/onlinopt/computer/networka/networkr",
            _missing_element,
        )
        parts = tiff_href.split("/")[-5:]
        # Some metadata have a 'current' or 'historical' in the path, some don't.
        if parts[2] == "TIFF":
            self.product = parts[1]
        else:
            self.product = parts[0]
        self.id = parts[3]

    @property
    def stac_id(self) -> str:
        """Returns the STAC ID of this metadata.

        This is the id plus the product, e.g. if the filename of the tif is
        "USGS_1_n40w105.tif", then the STAC id is "n40w105-1".
        """
        return "{}-{}".format(self.id, self.product)

    @property
    def publication_datetime(self) -> Optional[datetime.datetime]:
        """Returns the collection publication datetime."""
        if self.current == "publication date":
            return _format_date(self.pubdate)
        else:
            raise NotImplementedError

    @property
    def start_datetime(self) -> Optional[datetime.datetime]:
        """Returns the start datetime for this record.

        This can be a while ago, since the national elevation dataset was
        originally derived from direct survey data.
        """
        return _format_date(self.begdate)

    @property
    def end_datetime(self) -> Optional[datetime.datetime]:
        """Returns the end datetime for this record."""
        return _format_date(self.enddate, end_of_year=True)

    @property
    def spatial_resolution(self) -> float:
        """Returns the nominal ground sample distance from these metadata."""
        if self.product == "1":
            return 30
        elif self.product == "13":
            return 10
        else:
            raise NotImplementedError

    def data_asset(self, base: Optional[str] = DEFAULT_BASE) -> Asset:
        """Returns the data asset (aka the tiff file)."""
        return Asset(
            href=self.asset_href_with_extension(base, "tif"),
            title=self.title,
            description=None,
            media_type=MediaType.COG,
            roles=["data"],
        )

    def metadata_asset(self, base: Optional[str] = DEFAULT_BASE) -> Asset:
        """Returns the data asset (aka the tiff file)."""
        return Asset(
            href=self.asset_href_with_extension(base, "xml"),
            media_type=MediaType.XML,
            roles=["metadata"],
        )

    def thumbnail_asset(self, base: Optional[str] = DEFAULT_BASE) -> Asset:
        """Returns the thumbnail asset."""
        return Asset(
            href=self.asset_href_with_extension(base, "jpg"),
            media_type=MediaType.JPEG,
            roles=["thumbnail"],
        )

    def gpkg_asset(self, base: Optional[str] = DEFAULT_BASE) -> Asset:
        """Returns the geopackage asset."""
        description = (
            "Spatially-referenced polygonal footprints of the source data used "
            "to assemble the DEM layer. The attributes of each source dataset, "
            "such as original spatial resolution, production method, and date "
            "entered into the standard DEM, are linked to these footprints."
        )
        return Asset(
            href=self.asset_href_with_extension(base, "gpkg", id_only=True),
            media_type=MediaType.GEOPACKAGE,
            roles=["metadata"],
            description=description,
        )

    def via_link(self, base: Optional[str] = DEFAULT_BASE) -> Link:
        """Returns the via link for this file."""
        return Link("via", self.asset_href_with_extension(base, "xml"))

    @property
    def region(self) -> str:
        """Returns this objects 3dep "region".

        Region is defined as a 10x10 lat/lon box that nominally contains this item.
        E.g. for n41w106, the region would be n40w110. This is used mostly for
        creating subcatalogs for STACBrowser.
        """
        import math

        n_or_s = self.id[0]
        lat = float(self.id[1:3])
        if n_or_s == "s":
            lat = -lat
        lat = math.floor(lat / 10) * 10
        e_or_w = self.id[3]
        lon = float(self.id[4:])
        if e_or_w == "w":
            lon = -lon
        lon = math.floor(lon / 10) * 10
        return f"{n_or_s}{abs(lat)}{e_or_w}{abs(lon)}"

    def asset_href_with_extension(
        self, base: Optional[str], extension: str, id_only: bool = False
    ) -> str:
        if base is None:
            base = DEFAULT_BASE
        return utils.path(
            self.product, self.id, base=base, extension=extension, id_only=id_only
        )


def _format_date(
    date: str, end_of_year: bool = False
) -> Union["datetime.datetime", None]:
    if len(date) == 4:
        year = int(date)
        if end_of_year:
            month = 12
            day = 31
        else:
            month = 1
            day = 1
        if year < 1800 or year > datetime.date.today().year:
            return None  # There's some bad metadata in the USGS records
        else:
            return datetime.datetime(
                year, month, day, 0, 0, 0, tzinfo=datetime.timezone.utc
            )
    elif len(date) == 8:
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        return datetime.datetime(
            year, month, day, 0, 0, 0, tzinfo=datetime.timezone.utc
        )
    else:
        return None


def _missing_element(xpath: str) -> Exception:
    raise ValueError(f"missing required element: {xpath}")
