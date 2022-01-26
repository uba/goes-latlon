# MIT License
# Copyright (c) 2022 Douglas Uba
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Douglas Uba'
__email__  = 'douglas.uba@inpe.br'

from netCDF4 import Dataset
import numpy as np
import pyproj

# Define KM_PER_DEGREE
KM_PER_DEGREE = 40075.16/360.0

# GOES-16 viewing point (satellite position) height above the Earth
H = 35786023.0

# GOES-16 Spatial Reference System (proj4 format)
G16Proj4String = '+proj=geos +h=35786023.0 \
    +a=6378137.0 +b=6356752.31414 +f=0.00335281068119356027 \
    +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs'

# Lat/Lon WGS84 Spatial Reference System (proj4 string format)
LatLonWGS84Proj4String = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

# GOES-16 Spatial Reference System
G16Proj = pyproj.Proj(G16Proj4String) 

# Lat/Lon WSG84 Spatial Reference System
LatLonWGS84Proj = pyproj.Proj(LatLonWGS84Proj4String)

# Full-disk (FD) properties by resolution (GOES-16)
G16FDNLinesDic = {'0.5' : 21696,    '1.0' : 10848,    '2.0' : 5424, '4.0' : 2712, '10.0' : 1086}
G16FDNColsDic  = {'0.5' : 21696,    '1.0' : 10848,    '2.0' : 5424, '4.0' : 2712, '10.0' : 1086}
G16FDScaleDic  = {'0.5' : 0.000014, '1.0' : 0.000028, '2.0' : 0.000056, '4.0' : 0.000112, '10.0' : 0.000280}
G16FDOffsetDic = {'0.5' : 0.151865, '1.0' : 0.151858, '2.0' : 0.151844, '4.0' : 0.151816, '10.0' : 0.151900}

def GetFullDiskInfos(resolution):
    return G16FDNLinesDic[resolution], G16FDNColsDic[resolution], \
        G16FDScaleDic[resolution], G16FDOffsetDic[resolution]

def BuildLatLonGrid(resolution, path=None):
    # Get full-disk properties
    nlines, ncols, scale, offset = GetFullDiskInfos(resolution)

    # Create satellite-projection coordinates array
    x = np.arange(0, ncols)
    y = np.arange(0, nlines)

    # Apply scale and offset (scanning angle) + H factor = projection coordinates
    x = ((x * scale) - offset) * H
    y = ((y * (-1 * scale)) + offset) * H

    # Create matrix with values
    x, y = np.meshgrid(x, y)

    # Reshape to vector (1-d)
    x = x.reshape(nlines * ncols)
    y = y.reshape(nlines * ncols)

    # Transform
    transformer = pyproj.Transformer.from_proj(G16Proj, LatLonWGS84Proj) # source -> from
    lon, lat = transformer.transform(x, y)

    # Reshape to matrix format
    lat = lat.reshape(nlines, ncols)
    lon = lon.reshape(nlines, ncols)

    lat = np.ma.masked_invalid(lat)
    lon = np.ma.masked_invalid(lon)

    # Export [lat, lon] to file, if requested
    if(path):
        export2file(lat, lon, path)

    return lat, lon

def getScaleOffset(values, n):
    # From: http://james.hiebert.name/blog/work/2015/04/18/NetCDF-Scale-Factors.html
    # stretch/compress data to the available packed range
    max = np.max(values); min = np.min(values)
    scale = (max - min)/(2**n - 1)
    # translate the range to be symmetric about zero
    offset = min + 2**(n - 1) * scale
    return (scale, offset)

def pack(values, scale, offset):
    return np.floor((values - offset)/scale)

def export2file(lat, lon, path):
    nc = Dataset(path, 'w', format='NETCDF4');
    nc.createDimension('size', lat.shape[0])
    latvar = nc.createVariable('lat', 'i2', ('size', 'size'), zlib=True) # i2 -> int16
    lonvar = nc.createVariable('lon', 'i2', ('size', 'size'), zlib=True) # i2 -> int16
    # Pack data using scale and offset
    lat_scale, lat_offset = getScaleOffset(lat, 16) # 16 -> int16 = i2
    lon_scale, lon_offset = getScaleOffset(lon, 16) # 16 -> int16 = i2
    lat_packed = pack(lat, lat_scale, lat_offset)
    lon_packed = pack(lon, lon_scale, lon_offset)
    latvar[:] = lat_packed.astype(np.int16)
    lonvar[:] = lon_packed.astype(np.int16)
    # Adjust meta-data info
    latvar.scale_factor = lat_scale; latvar.add_offset = lat_offset
    lonvar.scale_factor = lon_scale; lonvar.add_offset = lon_offset
    nc.close()
