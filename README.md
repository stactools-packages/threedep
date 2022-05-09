# stactools-threedep

- Name: threedep
- Package: `stactools.threedep`
- PyPI: https://pypi.org/project/stactools-threedep/
- Owner: @gadomski
- Dataset homepage: https://www.usgs.gov/core-science-systems/ngp/3dep
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)
  - [scientific](https://github.com/stac-extensions/scientific/)

This package creates STAC items for USGS 3DEP (formerly NED) elevation data.

## Examples

### STAC objects

- [Catalog](examples/catalog.json)
- [Collection](examples/usgs-3dep-1/collection.json)
- [Item](examples/usgs-3dep-1/n41w106-1/n41w106-1.json)

### Command-line usage

Create a catalog for all 3DEP data.
This catalog will contain two collections, one for the 1 arc-second data and one for the 1/3 arc-second data:

```bash
stac threedep create-catalog destination
```

Create a catalog for a single lat+lon id:

```bash
stac threedep create-catalog --asset-id n41w106 examples
```

Download all XML metadata:

```bash
stac threedep download-metadata destination
```

Fetch all available IDs:

```bash
stac threedep fetch-ids
```

Use `stac threedep --help` to see all subcommands and options.
