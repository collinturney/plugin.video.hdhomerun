#!/usr/bin/env python

import json
import os
import sys
import urllib2
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon


class HDHomeRun(object):
    DISCOVER_URL = 'http://ipv4-my.hdhomerun.com/discover'

    def __init__(self, args):
        self._url = args[0]
        self._handle = int(args[1])
        self._addon_path = xbmcaddon.Addon().getAddonInfo("path")
        self._addon_name = xbmcaddon.Addon().getAddonInfo("name")

        self._item_art = {
            'thumb': os.path.join(self._addon_path, 'resources/hdhomerun.png'),
            'icon': os.path.join(self._addon_path, 'resources/hdhomerun.png')
        }

    def list_devices(self):
        xbmc.log("Requesting device list from '{0}'".format(self.DISCOVER_URL))

        try:
            response = urllib2.urlopen(self.DISCOVER_URL)
            devices = json.loads(response.read())
        except:
            self._display_error("Error retrieving device list")
            return

        for device in devices:
            device_name = "HDHomeRun {0} ({1})".format(device['DeviceID'],
                                                       device['LocalIP'])

            list_item = xbmcgui.ListItem(label=device_name)
            list_item.setArt(self._item_art)
            list_item.setInfo('video', {'title': device_name, 'genre': 'TV'})

            lineup_url = device['LineupURL']
            url = self._get_url(action='list_channels', lineup_url=lineup_url)

            xbmcplugin.addDirectoryItem(self._handle, url, list_item, True)

        xbmcplugin.addSortMethod(self._handle,
                                 xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(self._handle)

    def list_channels(self, lineup_url):
        xbmc.log("Requesting channel lineup from '{0}'".format(lineup_url))

        try:
            response = urllib2.urlopen(lineup_url)
            channels = json.loads(response.read())
        except:
            self._display_error("Error retrieving channel list")
            return

        for channel in channels:
            channel_name = "{0} {1}".format(channel['GuideNumber'],
                                            channel['GuideName'])

            list_item = xbmcgui.ListItem(label=channel_name)
            list_item.setInfo('video', {'title': channel_name, 'genre': 'TV'})
            list_item.setArt(self._item_art)
            list_item.setProperty('IsPlayable', 'true')

            channel_url = channel['URL']
            url = self._get_url(action='play_channel', channel_url=channel_url)

            xbmcplugin.addDirectoryItem(self._handle, url, list_item, False)

        xbmcplugin.addSortMethod(self._handle,
                                 xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(self._handle)

    def play_channel(self, path):
        play_item = xbmcgui.ListItem(path=path)
        xbmcplugin.setResolvedUrl(self._handle, True, listitem=play_item)

    def _get_url(self, **kwargs):
        return '{0}?{1}'.format(self._url, urlencode(kwargs))

    def _log_response(self, response):
        xbmc.log("Response code: {0}".format(response.status_code))
        xbmc.log("Response: ")

        for line in response.text.splitlines():
            xbmc.log(line)

    def _display_error(self, message):
        xbmcgui.Dialog().ok(self._addon_name, message)


def router(args):
    hdhr = HDHomeRun(args)

    argstring = sys.argv[2][1:]
    params = dict(parse_qsl(argstring))

    if params:
        action = params['action']

        if action == 'list_channels':
            hdhr.list_channels(params['lineup_url'])
        elif action == 'play_channel':
            hdhr.play_channel(params['channel_url'])
        else:
            raise ValueError('Invalid args: {0}!'.format(argstring))
    else:
        hdhr.list_devices()


if __name__ == '__main__':
    router(sys.argv)
