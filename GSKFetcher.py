ROOT_URL = "https://health.gsk-china.com/service-and-tools/elsevier"


class GSKSpider:
    def __init__(self):
        self.visited = self._init_context()

    def _init_context(self):
        return None

    def _get_joural_list(self):
        return []

    def _get_issue_list(self, journal):
        return []

    def _get_paper_list(self, journal, issue):
        return []

    def _arrange_fetchers(self, url_list):
        return []

    def start(self):
        journal_list = self._get_joural_list()
        for jounal in journal_list:
            issue_list = self._get_issue_list(jounal)
            
        pass
