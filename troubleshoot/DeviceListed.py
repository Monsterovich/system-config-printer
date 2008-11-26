#!/usr/bin/env python

## Printing troubleshooter

## Copyright (C) 2008 Red Hat, Inc.
## Copyright (C) 2008 Tim Waugh <twaugh@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import cups
import gobject
from timedops import TimedOperation
from base import *
class DeviceListed(Question):
    def __init__ (self, troubleshooter):
        # Is the device listed?
        Question.__init__ (self, troubleshooter, "Choose device")
        page1 = self.initial_vbox (_("Choose Device"),
                                   _("Please select the device you want "
                                     "to use from the list below. "
                                     "If it does not appear in the list, "
                                     "select 'Not listed'."))
        tv = gtk.TreeView ()
        name = gtk.TreeViewColumn (_("Name"),
                                   gtk.CellRendererText (), text=0)
        info = gtk.TreeViewColumn (_("Information"),
                                   gtk.CellRendererText (), text=1)
        uri = gtk.TreeViewColumn (_("Device URI"),
                                  gtk.CellRendererText (), text=2)
        name.set_property ("resizable", True)
        info.set_property ("resizable", True)
        uri.set_property ("resizable", True)
        tv.append_column (name)
        tv.append_column (info)
        tv.append_column (uri)
        tv.set_rules_hint (True)
        sw = gtk.ScrolledWindow ()
        sw.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type (gtk.SHADOW_IN)
        sw.add (tv)
        page1.pack_start (sw, True, True, 0)
        self.treeview = tv
        troubleshooter.new_page (page1, self)

    def display (self):
        self.answers = {}
        answers = self.troubleshooter.answers
        if (answers['printer_is_remote'] or
            answers.get ('cups_printer_remote', False)):
            return False

        model = gtk.ListStore (gobject.TYPE_STRING,
                               gobject.TYPE_STRING,
                               gobject.TYPE_STRING,
                               gobject.TYPE_PYOBJECT)
        self.treeview.set_model (model)
        iter = model.append (None)
        model.set (iter, 0, _("Not listed"), 1, '', 2, '', 3, None)

        devices = {}
        try:
            c = answers['_authenticated_connection']
            p = TimedOperation (c.getDevices, parent=self.troubleshooter.get_window ())
            devices = p.run ()
            devices_list = []
            for uri, device in devices.iteritems ():
                if uri.find (':') == -1:
                    continue

                if device.get('device-class') != 'direct':
                    continue

                name = device.get('device-info', _("Unknown"))
                info = device.get('device-make-and-model', _("Unknown"))
                devices_list.append ((name, info, uri, device))

            devices_list.sort (lambda x, y: cmp (x[0], y[0]))
            for name, info, uri, device in devices_list:
                iter = model.append (None)
                model.set (iter, 0, name, 1, info, 2, uri, 3, device)

        except cups.HTTPError:
            pass
        except cups.IPPError:
            pass
        except RuntimeError:
            pass

        if answers['cups_queue_listed']:
            try:
                printer_dict = answers['cups_printer_dict']
                uri = printer_dict['device-uri']
                device = devices[uri]
                self.answers['cups_device_dict'] = device
            except KeyError:
                pass

            return False

        return True

    def connect_signals (self, handler):
        self.signal_id = self.treeview.connect ("cursor-changed", handler)

    def disconnect_signals (self):
        self.treeview.disconnect (self.signal_id)

    def can_click_forward (self):
        model, iter = self.treeview.get_selection ().get_selected ()
        if iter == None:
            return False
        return True

    def collect_answer (self):
        if not self.displayed:
            return self.answers

        model, iter = self.treeview.get_selection ().get_selected ()
        device = model.get_value (iter, 3)
        if device == None:
            class enum_devices:
                def __init__ (self, model):
                    self.devices = {}
                    model.foreach (self.each, None)

                def each (self, model, path, iter, user_data):
                    uri = model.get_value (iter, 2)
                    device = model.get_value (iter, 3)
                    if device:
                        self.devices[uri] = device

            self.answers['cups_device_listed'] = False
            avail = enum_devices (model).devices
            self.answers['cups_devices_available'] = avail
        else:
            uri = model.get_value (iter, 2)
            self.answers['cups_device_listed'] = True
            self.answers['cups_device_uri'] = uri
            self.answers['cups_device_attributes'] = device

        return self.answers
