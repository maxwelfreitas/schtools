# -*- coding: utf-8 -*-
from ._websearch import SCHWebSearch

class GoogleSearch(SCHWebSearch):

    def __init__(self, config):
        super().__init__(config)
        self.search_url = "https://www.google.com/search?q="
        self.search_results = []
        self.search_query = None