# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#   Ria Gupta <ria18405@iiitd.ac.in>
#


import logging

from requests.structures import CaseInsensitiveDict
from grimoire_elk.enriched.enrich import metadata, DEFAULT_PROJECT
from grimoirelab_toolkit.datetime import str_to_datetime
from .scmsenrich import ScmsEnrich

logger = logging.getLogger(__name__)


class ScmsTwitterEnrich(ScmsEnrich):

    def get_field_author(self):
        return "user"

    def get_sh_identity(self, item, identity_field=None):
        identity = {}
        identity['username'] = None
        identity['email'] = None
        identity['name'] = None

        if identity_field is None:
            identity_field = self.get_field_author()

        tweet = item  # by default a specific user dict is expected
        if isinstance(item, dict) and 'data' in item:
            tweet = item['data']

        if identity_field in tweet:
            identity['username'] = tweet[identity_field]['screen_name']
            identity['name'] = tweet[identity_field]['name']
        return identity

    def get_identities(self, item):
        """ Return the identities from an item """

        item = item['data']
        user = self.get_sh_identity(item)

        yield user

    def get_item_project(self, eitem):
        """ Get project mapping enrichment field.

        Twitter mappings is pretty special so it needs a special
        implementacion.
        """

        project = None
        eitem_project = {}
        ds_name = self.get_connector_name()  # data source name in projects map

        if ds_name not in self.prjs_map:
            return eitem_project

        for tag in eitem['hashtags_analyzed']:
            # lcanas: hashtag provided in projects.json file should not be case sensitive T6876
            tags2project = CaseInsensitiveDict(self.prjs_map[ds_name])
            if tag in tags2project:
                project = tags2project[tag]
                break

        if project is None:
            project = DEFAULT_PROJECT

        eitem_project = {"project": project}

        eitem_project.update(self.add_project_levels(project))

        return eitem_project

    @metadata
    def get_rich_item(self, item):
        eitem = {}
        self.copy_raw_fields(self.RAW_FIELDS_COPY, item, eitem)

        # The real data
        tweet = item['data']

        if 'text' in tweet:
            eitem['body'] = tweet['text']
        # data fields to copy
        copy_fields = ["id"]
        for f in copy_fields:
            if f in tweet:
                eitem[f] = tweet[f]
            else:
                eitem[f] = None

        # Date fields
        eitem["created_at"] = str_to_datetime(tweet["created_at"]).isoformat()

        # data fields to copy from user
        copy_fields = ["created_at", "description", "name"]
        for f in copy_fields:
            if f in tweet['user']:
                eitem["user_" + f] = tweet['user'][f]
            else:
                eitem["user_" + f] = None

        eitem['data_source'] = "Twitter"

        eitem['hashtags_analyzed'] = []
        for tag in tweet['entities']['hashtags']:
            eitem['hashtags_analyzed'].append(tag['text'])

        eitem['context'] = eitem['hashtags_analyzed']

        eitem.update(self.get_grimoire_fields(item["metadata__updated_on"], "tweet"))

        if self.sortinghat:
            eitem.update(self.get_item_sh(item))

        if self.prjs_map:
            eitem.update(self.get_item_project(eitem))

        self.add_repository_labels(eitem)
        self.add_metadata_filter_raw(eitem)
        return eitem
