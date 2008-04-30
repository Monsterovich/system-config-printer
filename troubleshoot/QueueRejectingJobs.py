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
from base import *
from base import _
class QueueRejectingJobs(Question):
    def __init__ (self, troubleshooter):
        Question.__init__ (self, troubleshooter, "Queue rejecting jobs?")
        solution = gtk.VBox ()
        solution.set_border_width (12)
        solution.set_spacing (12)
        label = gtk.Label ('<span weight="bold" size="larger">' +
                           _("Queue Rejecting Jobs") + '</span>')
        label.set_alignment (0, 0)
        label.set_use_markup (True)
        solution.pack_start (label, False, False, 0)
        self.label = gtk.Label ()
        self.label.set_alignment (0, 0)
        self.label.set_line_wrap (True)
        solution.pack_start (self.label, False, False, 0)
        solution.set_border_width (12)

        troubleshooter.new_page (solution, self)

    def display (self):
        answers = self.troubleshooter.answers
        if not answers['cups_queue_listed']:
            return False

        if answers['is_cups_class']:
            queue = answers['cups_class_dict']
        else:
            queue = answers['cups_printer_dict']

        rejecting = queue['printer-type'] & cups.CUPS_PRINTER_REJECTING
        if not rejecting:
            return False

        if answers['cups_printer_remote']:
            attrs = answers['remote_cups_queue_attributes']
            reason = attrs['printer-state-message']
        else:
            reason = queue['printer-state-message']

        text = (_("The queue `%s' is rejecting jobs.") % answers['cups_queue'])

        if reason:
            text += ' ' + _("The reason given is: `%s'.") % reason

        if not answers['cups_printer_remote']:
            text += "\n\n"
            text += _("To make the queue accept jobs, select the "
                      "`Accepting Jobs' checkbox in the `Settings' "
                      "tab for the printer in the printer administration "
                      "tool.") + ' ' + TEXT_start_print_admin_tool

        self.label.set_text (text)
        return True

    def can_click_forward (self):
        return False
