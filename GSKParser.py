from sgmllib import SGMLParser
import re


def match_attr(attr, t_name, t_value):
    for name, value in attr:
        if name == t_name and value == t_value:
            return True
    return False


def find_attr(attr, t_name):
    for name, value in attr:
        if name == t_name:
            return value
    return None


class GSKPageParser(SGMLParser):
    HOME_URL = "https://health.gsk-china.com"

    def __init__(self):
        super().__init__()
        self._journal_url_list = []
        self._issue_url_list = []
        self._paper_url_list = []

        self._is_journal_ul = False

        self._is_issue_div = False
        self._issue_div_level = 0
        self._is_issue_ul = False
        self._is_issue_a = False

        self._is_paper_li = False
        self._is_paper_h3 = False

    def get_journals(self):
        return self._journal_url_list

    def get_issues(self):
        return self._issue_url_list

    def get_papers(self):
        return self._paper_url_list

    def start_div(self, attr):
        if self._is_issue_div:
            self._issue_div_level += 1

        if match_attr(attr, "class", "list"):
            self._is_issue_div = True

    def end_div(self):
        if self._issue_div_level == 0 and self._is_issue_div:
            self._is_issue_div = False

        if self._is_issue_div:
            self._issue_div_level -= 1

    def start_ul(self, attr):
        if self._is_issue_div:
            self._is_issue_ul = True
        if match_attr(attr, "class", "sub-nav elsevier-nav"):
            self._is_journal_ul = True

    def end_ul(self):
        if self._is_issue_ul:
            self._is_issue_ul = False
        if self._is_journal_ul:
            self._is_journal_ul = False

    def start_li(self, attr):
        if match_attr(attr, "name", "record"):
            self._is_paper_li = True

    def end_li(self):
        if self._is_paper_li:
            self._is_paper_li = False

    def start_h3(self, attr):
        if self._is_paper_li:
            self._is_paper_h3 = True

    def end_h3(self):
        if self._is_paper_h3:
            self._is_paper_h3 = False

    def start_a(self, attr):
        if self._is_journal_ul:
            journal_url = find_attr(attr, "href")
            if journal_url is not None:
                self._journal_url_list.append(self.HOME_URL + journal_url)
        if self._is_issue_ul:
            issue_url = find_attr(attr, "href")
            if issue_url is not None:
                self._issue_url_list.append(self.HOME_URL + issue_url)
        if self._is_paper_h3:
            paper_url = find_attr(attr, "href")
            if paper_url is not None:
                self._paper_url_list.append(self.HOME_URL + paper_url)

    def feed(self, data):
        self._issue_url_list.clear()
        self._journal_url_list.clear()
        self._paper_url_list.clear()
        super().feed(data)


class GSKPaperParser(SGMLParser):
    def __init__(self):
        super().__init__()

        self._is_abstract_div = False
        self._is_abstract_p = False
        self._abstract = ""

        self._is_title_h3 = False
        self._title = ""

    def get_abstract(self):
        return self._title, self._abstract

    def start_div(self, attr):
        if match_attr(attr, "class", "txt"):
            self._is_abstract_div = True

    def end_div(self):
        if self._is_abstract_div:
            self._is_abstract_div = False

    def start_p(self, attr):
        if self._is_abstract_div:
            self._is_abstract_p = True

    def end_p(self):
        if self._is_abstract_p:
            self._abstract += "\r\n"
            self._is_abstract_p = False

    def start_h3(self, attr):
        self._is_title_h3 = True

    def end_h3(self):
        if self._is_title_h3:
            self._is_title_h3 = False

    def handle_data(self, data):
        if self._is_abstract_p:
            self._abstract += data.strip()
        if self._is_title_h3:
            self._title = data

    def feed(self, data):
        self._abstract = ""
        self._title = ""
        super().feed(data)
