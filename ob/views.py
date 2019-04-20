from django.shortcuts import render
from django.http import HttpResponse
import base64
from django.conf import settings

listing_icons = {
    'debug': b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqBAMAAAA37dRoAAAAG1BMVE'
             b'X//wAAAAAzMwBmZgD//zOZmQDMzADMzDOZmTNXxfsYAAAACXBIWXMA'
             b'AAsTAAALEwEAmpwYAAAAB3RJTUUH4gMJCx41I1cxbgAAALtJREFUKM'
             b'/t0k0OgjAQBeAGSt06RdClFQ9ArHFd8GcNngAlegHj/R1BzQCzceHO'
             b'2ZB8eem8AkL851cTVJz6KadqwqlM2INZlRHbYTygvd2UxSAHALojay'
             b'xlUEmxWihckiECOfZUbKM2SrOZNuGtQZr14TNzssu8UTui5ctgSnvl'
             b'rVpI+/0xOgLXuUSjS9lRJe+IMxdA0Vumr8ILc/rG5E6YGB+VR7KHy2'
             b'rR1j/SOyTW2mfqHHMfoq6+/n8e/oUU2qrAu5AAAAAASUVORK5CYII=',
    'devop': b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqBAMAAAA37dRoAAAAElBMVE'
             b'Uz//8AAAAAMzMAZmYzzMwzmZk9wIupAAAAAWJLR0QAiAUdSAAAAAlw'
             b'SFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB+IDCQsuLnZ0znEAAACkSU'
             b'RBVCjP7ZIxFsIgEEQJbHqXhF7MBfLEA6CYnnj/w7gJ0bcQmhR2bvnf'
             b'MDMLCPGfX03ra1SNNQqnqsVwgJpqh71v625z3EFE1BmhmmCJMoMggE'
             b'IazOk9KpOknDbadmGFnCr8zpll2Q/MKswbw55TmajDsexPUsB8rS0p'
             b'oyAmgoaOxCJMP4XsZHFjdkn3kmlhul5S/RfXDc65RfXoaw8R/OH/8w'
             b'agEhAN51rfnQAAAABJRU5ErkJggg==',
    'onion': b"iVBORw0KGgoAAAANSUhEUgAAACoAAAAqAgMAAAC4rSHIAAAADFBMVE"
             b"UODAxwWXCqh6n/yv1d/+DfAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA"
             b"B3RJTUUH4gIRDBYPgAAikQAAAJJJREFUGNNj+A8HHxiGGvvffgT7bz"
             b"2SuD2SenkkdjwSWx+r+qspcDP/MTBA7foOpJkh7PmP/h+AsdsvApVA"
             b"2QcYJ8DZFxiAgB3C/gBi80PYP0BsfQj7D5AZUA9h/wWyH8D8BTTlA4"
             b"w9gUH+wX4Iu4GB+6+MPVT8g/3/PxDxf0sY7P9/haj/Ihq6//9lpPCZ"
             b"jScMAQuZj3KzxzFIAAAAAElFTkSuQmCC",
    'plain': b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqAgMAAAC4rSHIAAAADFBMVE'
             b'UHBwdfX1+ZmZn+/v43scdGAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA'
             b'B3RJTUUH4gMJCxsm2p6E9QAAAJNJREFUGNNj+A8HHxiGGvvffgT7bz'
             b'2SuD2Sen0kdjx2cST1TyvgZv5jYIDa9f3/FwZmCHv+p/8HYOzuS/8Z'
             b'YOwDjBPg7AsMQMAOYX8Bsfkh7B8gtj6E/QfInFAPYQMtYngA8xfQlA'
             b'8w9gIG/Qf7IewGBu6/svZQ8S/2//9AxZcy2P//CVH/RTR0///LSOEz'
             b'G08YAgCBS5Aw0fodwAAAAABJRU5ErkJggg=='
}

profile_icons = {
    'debug': b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqBAMAAAA37dRoAAAAG1BMVE'
             b'X//wAAAADMzAAzMwCZmQBmZgD//zPMzDOZmTMQUIQZAAAACXBIWXMA'
             b'AAsTAAALEwEAmpwYAAAAB3RJTUUH4gMJCx8mvvJB8QAAAB1pVFh0Q2'
             b'9tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAA2klEQVQo'
             b'z+WSwQ6CMAyGF1DObAPP1BjPEA3nYdQzGLkT4wOAxuDdFxe2sU1YYj'
             b'zbw9J86dr+bRH6R/PayEIzTKfQwRinE3rvKLWFWoI5DcY04Zj17mWt'
             b'6OzF8Xl/6N7tTvEGG8ZUtEmJEmfS02cbwmg1akNY9IUWVpoZVOcFay'
             b'zgPnP4uJkqEFCg7bLiBXItOYBwSEV0NQJilHOzXJECkdpLnaKIYSH1'
             b'1ImiSQ6+9KpsoB6tQPob5MZynwlxilrsO0Cu/OWUDLBwnww1vmrtet'
             b'Tz821Xt6p/u9I3oLsjGyZscpMAAAAASUVORK5CYII=',
    'devop': b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqBAMAAAA37dRoAAAAElBMVE'
             b'Uz//8AAAAzzMwAMzMzmZkAZmZdC+ZMAAAAAWJLR0QAiAUdSAAAAAlw'
             b'SFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB+IDCQsuHcmkr2cAAAAdaV'
             b'RYdENvbW1lbnQAAAAAAENyZWF0ZWQgd2l0aCBHSU1QZC5lBwAAAMNJ'
             b'REFUKM/l0ksOgyAQANAJtnsR3TNo95L2ANDPXpt6/6tUYQSqJE3XnY'
             b'UxL8N8FIC/DCUzaLnYI+Oc9zttZxW51Eyy03qr2rFx5+Iwh5vj1/0x'
             b'Py/X4MiTMCE71eqzIcUzp2I7hg/5Rces2kQhO7BMdKncnFS6BaBAoZ'
             b'RvMEStsVlLxd1shf5THtN2Y4+UwqdYYtaS9pE6qB6Cgg0qAOn9DAX9'
             b'QqYrNvrh2xoKOsUmg9S5M7DWWv5G3EiXuUvXyd8u6RsmmBuBxXqLdA'
             b'AAAABJRU5ErkJggg==',
    'onion': b"iVBORw0KGgoAAAANSUhEUgAAACoAAAAqAgMAAAC4rSHIAAAADFBMVE"
             b"UHBwZuWG6ti67/yf0FEwXuAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA"
             b"B3RJTUUH4gIRDBUDops9eQAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYX"
             b"RlZCB3aXRoIEdJTVBkLmUHAAAArUlEQVQY08XQIQ4CMRAF0N/dBEgQ"
             b"awkGi8PiyhHwXATX5RqgURhuUI7AEdagMCWpqNh06E7T7SYELKNeRv"
             b"zkf1B/Bv/zJdsh20D2rlEle6Ds/4AYGIq8Zj+A0RlCc36N7sbshl2w"
             b"zeAfXf20Hdh9eJosjsmTuaZNzHezBdGtjF6uiO6Imetgs1XsfShsrt"
             b"nWsY1TRK+WXdhQ8NDKzrs6FD85Nj27FazM23r9dfM3D5lhVvd+cZsA"
             b"AAAASUVORK5CYII=",
    'plain': b'iVBORw0KGgoAAAANSUhEUgAAACoAAAAqAgMAAAC4rSHIAAAADFBMVE'
             b'UEBARbW1uhoaH///88Kn54AAAACXBIWXMAAAsTAAALEwEAmpwYAAAA'
             b'B3RJTUUH4gMJCx0ZOqIOTgAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYX'
             b'RlZCB3aXRoIEdJTVBkLmUHAAAAoUlEQVQY08XQsQ3CMBAF0B+MoAAp'
             b'I7AAEgtEMiOwAYsgJetQsULEBBT00KdxJBcpTjL2HdhXITquetW/+4'
             b'eQx+F/vhR7FD9hszvU2YBRrpTRfnwHFmfMJL9DmhX7xjZsx14q11/t'
             b'lSdl0p6jerx30XoTwl7yaRvdy96p2aVDJLOJJd2hZZ+SXbEntqPYax'
             b'QbHwteySYf++hBHIbU3Nuffv4CXElkPsRsAuEAAAAASUVORK5CYII='
}


def get_key():
    if settings.DEBUG is True:
        key = 'debug'
    elif settings.DEV is True:
        key = 'devop'
    elif settings.ONION is True:
        key = 'onion'
    else:
        key = 'plain'
    return key


def image(request):
    data = listing_icons[get_key()]
    return HttpResponse(base64.decodebytes(data),
                        content_type="image/png")


def profile_image(request):
    data = profile_icons[get_key()]
    return HttpResponse(base64.decodebytes(data),
                        content_type="image/png")
