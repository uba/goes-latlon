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

from netCDF4 import Dataset
import matplotlib.pyplot as plt

# Define path to [lat,lon] grid file
path = './data/goes16-full-disk-lat-lon-2.0km.nc'

# Open using netCDF4 package
nc = Dataset(path)

# Some file informations...
print(nc, nc.variables['lat'], nc.variables['lon'])

# Get all-values
lat_values = nc.variables['lat'][:]
lon_values = nc.variables['lon'][:]

# Show coordinates
plt.figure()
plt.imshow(lat_values)
plt.colorbar()
plt.savefig('./preview/latitudes.png', bbox_inches='tight', pad_inches=0)

plt.figure()
plt.imshow(lon_values)
plt.colorbar()
plt.savefig('./preview/longitudes.png', bbox_inches='tight', pad_inches=0)

plt.show()