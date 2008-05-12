# File: transforms.py
#
# Copyright (c) 2007 by []
# Generator: ArchGenXML Version 1.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """SYSLAB.COM GmbH <info@syslab.com>"""
__docformat__ = 'plaintext'


##code-section init-module-header #fill in your manual code here
from Products.QuickChangeTool.utils import log
WARNING=100
modules = [
    'ReindexObject',             # Standard Portal Reindexer
    'SearchReplace',             # Search and Replace
    ]
g = globals()

transforms = []
for m in modules:
    try:
        ns = __import__(m, g, g, None)
        transforms.append(ns.register())
    except ImportError, e:
        msg = "Problem importing module %s : %s" % (m, e)
        log(msg, severity=WARNING)
    except Exception, e:
        import traceback
        traceback.print_exc()
        log("Raised error %s for %s" % (e, m), severity=WARNING)
##/code-section init-module-header


# Subpackages

# Classes

##code-section init-module-footer #fill in your manual code here
def initialize(engine):
    for transform in transforms:
        engine.registerTransform(transform)
##/code-section init-module-footer

