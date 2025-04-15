# -*- coding: utf-8 -*-
class SCHWebSearch:
    
    def __init__(self, config):
        self.config = config
        self.search_results_folder = config['datasets'].get("search_results_data_home")
        print(self.search_results_folder)

    def search(self):
        pass
