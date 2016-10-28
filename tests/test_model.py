# coding=utf-8

import numpy
from datacube.model import BoundingBox, GeoPolygon, GeoBox, CRS, GridSpec


def test_geobox():
    points_list = [
        [(148.2697, -35.20111), (149.31254, -35.20111), (149.31254, -36.331431), (148.2697, -36.331431)],
        [(148.2697, 35.20111), (149.31254, 35.20111), (149.31254, 36.331431), (148.2697, 36.331431)],
        [(-148.2697, 35.20111), (-149.31254, 35.20111), (-149.31254, 36.331431), (-148.2697, 36.331431)],
        [(-148.2697, -35.20111), (-149.31254, -35.20111), (-149.31254, -36.331431), (-148.2697, -36.331431)],
        ]
    for points in points_list:
        polygon = GeoPolygon(points, CRS('EPSG:3577'))
        resolution = (-25, 25)
        geobox = GeoBox.from_geopolygon(polygon, resolution)

        assert abs(resolution[0]) > abs(geobox.extent.boundingbox.left - polygon.boundingbox.left)
        assert abs(resolution[0]) > abs(geobox.extent.boundingbox.right - polygon.boundingbox.right)
        assert abs(resolution[1]) > abs(geobox.extent.boundingbox.top - polygon.boundingbox.top)
        assert abs(resolution[1]) > abs(geobox.extent.boundingbox.bottom - polygon.boundingbox.bottom)


def test_grispec():
    gs = GridSpec(crs=CRS('EPSG:4326'), tile_size=(1, 1), resolution=(-0.1, 0.1), origin=(10, 10))
    poly = GeoPolygon([(10, 12.2), (10.8, 13), (13, 10.8), (12.2, 10)], CRS('EPSG:4326'))
    cells = {index: geobox for index, geobox in list(gs.tiles_inside_geopolygon(poly))}
    assert set(cells.keys()) == {(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)}
    assert numpy.isclose(cells[(2, 0)].coordinates['longitude'].values, numpy.linspace(12.05, 12.95, num=10)).all()
    assert numpy.isclose(cells[(2, 0)].coordinates['latitude'].values, numpy.linspace(10.95, 10.05, num=10)).all()


def test_gridspec_upperleft():
    """ Test to ensure grid indexes can be counted correctly from bottom left or top left
    """
    tile_bbox = BoundingBox(left=1934400.0, top=2414800.0, right=2084400.000, bottom=2264800.000)
    bbox = BoundingBox(left=1934615, top=2379460, right=1937615, bottom=2376460)
    # Upper left - validated against WELD product tile calculator
    # http://globalmonitoring.sdstate.edu/projects/weld/tilecalc.php
    gs = GridSpec(crs=CRS('EPSG:5070'), tile_size=(-150000, 150000), resolution=(-30, 30),
                  origin=(3314800.0, -2565600.0))
    cells = {index: geobox for index, geobox in list(gs.tiles(bbox))}
    assert set(cells.keys()) == {(30, 6)}
    assert cells[(30, 6)].extent.boundingbox == tile_bbox

    gs = GridSpec(crs=CRS('EPSG:5070'), tile_size=(150000, 150000), resolution=(-30, 30),
                  origin=(14800.0, -2565600.0))
    cells = {index: geobox for index, geobox in list(gs.tiles(bbox))}
    assert set(cells.keys()) == {(30, 15)}  # WELD grid spec has 21 vertical cells -- 21 - 6 = 15
    assert cells[(30, 15)].extent.boundingbox == tile_bbox


def test_crs_equality():
    a = CRS("""PROJCS["unnamed",GEOGCS["Unknown datum based upon the custom spheroid",
               DATUM["Not specified (based on custom spheroid)",SPHEROID["Custom spheroid",6371007.181,0]],
               PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],
               PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],
               PARAMETER["false_northing",0],UNIT["Meter",1]]""")
    b = CRS("""PROJCS["unnamed",GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",6371007.181,0]],
               PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Sinusoidal"],
               PARAMETER["longitude_of_center",0],PARAMETER["false_easting",0],
               PARAMETER["false_northing",0],UNIT["Meter",1]]""")
    c = CRS('+a=6371007.181 +b=6371007.181 +units=m +y_0=0 +proj=sinu +lon_0=0 +no_defs +x_0=0')
    assert a == b
    assert a == c
    assert b == c

    assert a != CRS('EPSG:4326')

    a = CRS("""GEOGCS["GEOCENTRIC DATUM of AUSTRALIA",DATUM["GDA94",SPHEROID["GRS80",6378137,298.257222101]],
               PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]""")
    b = CRS("""GEOGCS["GRS 1980(IUGG, 1980)",DATUM["unknown",SPHEROID["GRS80",6378137,298.257222101]],
               PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]""")
    c = CRS('+proj=longlat +no_defs +ellps=GRS80')
    assert a == b
    assert a == c
    assert b == c
