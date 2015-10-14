#    Copyright 2015 Geoscience Australia
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from __future__ import absolute_import, division, print_function
from builtins import *

import numpy as np
from cubeaccess.core import Coordinate, Variable, DataArray, StorageUnitSet
from cubeaccess.storage import NetCDF4StorageUnit
from cubeaccess.storage.utils import coord2index


class TestStorageUnit(object):
    def __init__(self, coords, vars):
        self.coordinates = coords
        self.variables = vars

    def get(self, name, **kwargs):
        if name in self.variables:
            var = self.variables[name]
            coords = [self.get(dim, **kwargs).values for dim in var.coordinates]
            shape = [coord.shape[0] for coord in coords]
            result = np.empty(shape, var.dtype)
            return DataArray(result, coords=coords, dims=var.coordinates)

        if name in self.coordinates:
            coord = self.coordinates[name]
            data = np.linspace(coord.begin, coord.end, coord.length, dtype=coord.dtype)
            index = coord2index(data, kwargs.get(name, None))
            data = data[index]
            return DataArray(data, coords=[data], dims=[name])

        raise RuntimeError("unknown variable")


ds1 = TestStorageUnit({
    't': Coordinate(np.int, 100, 400, 4),
    'y': Coordinate(np.float32, 0, 9.5, 20),
    'x': Coordinate(np.float32, 9, 0, 10)
}, {
    'B10': Variable(np.float32, np.nan, ('t', 'y', 'x'))
})
ds2 = TestStorageUnit({
    't': Coordinate(np.int, 500, 600, 3),
    'y': Coordinate(np.float32, 5, 14.5, 20),
    'x': Coordinate(np.float32, 4, -5, 10)
}, {
    'B10': Variable(np.float32, np.nan, ('t', 'y', 'x'))
})


def test_netcdf():
    files = [
        "/short/v10/dra547/injest_examples/multiple_band_variables/LS7_ETM_NBAR_P54_GANBAR01-002_089_078_2015_152_-26.nc",
        "/short/v10/dra547/injest_examples/multiple_band_variables/LS7_ETM_NBAR_P54_GANBAR01-002_089_078_2015_152_-27.nc",
        "/short/v10/dra547/injest_examples/multiple_band_variables/LS7_ETM_NBAR_P54_GANBAR01-002_089_078_2015_153_-26.nc",
        "/short/v10/dra547/injest_examples/multiple_band_variables/LS7_ETM_NBAR_P54_GANBAR01-002_089_078_2015_153_-27.nc",
        "/short/v10/dra547/injest_examples/multiple_band_variables/LS7_ETM_NBAR_P54_GANBAR01-002_089_078_2015_154_-26.nc",
        "/short/v10/dra547/injest_examples/multiple_band_variables/LS7_ETM_NBAR_P54_GANBAR01-002_089_078_2015_154_-27.nc"
    ]

    mds = StorageUnitSet([NetCDF4StorageUnit(filename) for filename in files])
    print(mds.get('band2'))

    # print(mds.coordinates)
    # print(mds.variables)


def test_storage_unit_set():
    mds = StorageUnitSet([ds1, ds2])

    assert(mds.coordinates['t'].begin == 100)
    assert(mds.coordinates['t'].end == 600)
    assert(mds.coordinates['t'].length == 11)

    assert(mds.coordinates['x'].begin == 9)
    assert(mds.coordinates['x'].end == -5)
    assert(mds.coordinates['x'].length == 15)

    assert(mds.coordinates['y'].begin == 0)
    assert(mds.coordinates['y'].end == 14.5)
    assert(mds.coordinates['y'].length == 30)

    assert(np.allclose(mds.get('x', x=slice(-2, 5)).values, np.linspace(5, -2, 8)))
    assert(np.allclose(mds.get('y', y=slice(-2.5, 5.5)).values, np.linspace(0, 5.5, 12)))

    # print('x:', mds.get('x'))
    # print('y:', mds.get('y'))
    # print('t:', mds.get('t'))
    # print('B10', mds.get('B10'))
