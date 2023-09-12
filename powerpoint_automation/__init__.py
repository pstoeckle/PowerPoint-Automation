# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2022 Patrick Stöckle.
# SPDX-License-Identifier: Apache-2.0
"""
Main module.
"""
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "powerpoint-automation"
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
__author__ = "Patrick Stöckle"
__copyright__ = "Patrick Stöckle"
__license__ = "mit"
