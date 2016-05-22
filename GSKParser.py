from sgmllib import SGMLParser
from MovieInfo import MovieDetailInfo
from MovieInfo import MovieReview
import re
import cx_Oracle


class DoubanMovieCatalogParser(SGMLParser):

    def __init__(self):
        super().__init__()
        self.movie_info_list = []
        self.current_movie_info = None
        self.is_movie_list_div = False      # e.g. <div class="mod-list movie-list" id="movie">
        self.is_button_span = False
        self.movie_list_level = 0

    def start_div(self, attr):
        if self.is_movie_list_div:
            self.movie_list_level += 1

        if match_attr(attr, "class", "pl2"):
            self.is_movie_list_div = True

    def end_div(self):
        if self.is_movie_list_div and self.movie_list_level == 0:
            self.is_movie_list_div = False

        if self.is_movie_list_div:
            self.movie_list_level -= 1

    def start_span(self, attr):
        if self.is_movie_list_div:
            if match_attr(attr, "class", "gact"):
                self.is_button_span = True

    def end_span(self):
        if self.is_button_span:
            self.is_button_span = False

    def start_a(self, attr):
        if self.is_movie_list_div and not self.is_button_span:
            movie_url = find_attr(attr, "href")
            self.movie_info_list.append(movie_url)

    def get_results(self):
        return self.movie_info_list

    def feed(self, data):
        self.movie_info_list.clear()
        super().feed(data)


class DoubanMoviePageParser(SGMLParser):
    def __init__(self, movie_id):
        super().__init__()

        self.movie_detail = MovieDetailInfo()
        self.movie_detail.set_id(movie_id)
        self.current_info = ""

        self.is_title = False

        self.is_movie_info_div = False
        self.is_movie_info = False

        self.is_rate_detail_div = False
        self.rate_div_level = 0
        self.is_rate = False
        self.is_voter_num = False
        self.is_rate_detail = False

        self.is_abstract_div = False
        self.is_abstract = False

        self.is_awards_ul = False
        self.current_award = []

        self.is_neighbor_div = False
        self.is_neighbor_dd = False

        self.is_review_div = False
        self.review_url = ""

    def start_div(self, attr):
        if match_attr(attr, "id", "info"):
            self.is_movie_info_div = True
        if match_attr(attr, "class", "related-info"):
            self.is_abstract_div = True
        if match_attr(attr, "class", "recommendations-bd"):
            self.is_neighbor_div = True
        if match_attr(attr, "class", "review-more"):
            self.is_review_div = True

        if self.is_rate_detail_div:
            self.rate_div_level += 1
        if match_attr(attr, "class", "rating_wrap clearbox"):
            self.is_rate_detail_div = True

    def end_div(self):
        if self.is_movie_info_div:
            self.is_movie_info_div = False
            if self.is_movie_info:
                self.start_br(None)

        if self.rate_div_level == 0 and self.is_rate_detail_div:
            self.is_rate_detail_div = False

        if self.is_rate_detail_div:
            self.rate_div_level -= 1

        if self.is_abstract_div:
            self.is_abstract_div = False
            if self.is_abstract:
                self.is_abstract = False
        if self.is_neighbor_div:
            self.is_neighbor_div = False
            if self.is_neighbor_dd:
                self.is_neighbor_dd = False
        if self.is_review_div:
            self.is_review_div = False

    def start_dd(self, attr):
        if self.is_neighbor_div:
            self.is_neighbor_dd = True

    def end_dd(self):
        if self.is_neighbor_dd:
            self.is_neighbor_dd = False

    def start_a(self, attr):
        if self.is_neighbor_dd:
            neighbor_id = find_attr(attr, "href")
            self.movie_detail.add_neighbor(neighbor_id)
        if self.is_review_div:
            review_url = find_attr(attr, "href")
            self.review_url = review_url

    def start_strong(self, attr):
        if self.is_rate_detail_div:
            self.is_rate = True

    def end_strong(self):
        if self.is_rate:
            self.is_rate = False

    def start_span(self, attr):
        if match_attr(attr, "property", "v:itemreviewed"):
            self.is_title = True
        if self.is_movie_info_div:
            self.is_movie_info = True
        if self.is_rate_detail_div:
            if match_attr(attr, "property", "v:votes"):
                self.is_voter_num = True
            if match_attr(attr, "class", "rating_per"):
                self.is_rate_detail = True
        if self.is_abstract_div:
            self.is_abstract = match_attr(attr, "property", "v:summary")

    def end_span(self):
        if self.is_title:
            self.is_title = False
        if self.is_voter_num:
            self.is_voter_num = False
        if self.is_rate_detail:
            self.is_rate_detail = False
        if self.is_abstract:
            self.is_abstract = False

    def start_br(self, attr):
        if self.is_movie_info:
            self.is_movie_info = False
            self.movie_detail.add_detail_info(self.current_info)
            self.current_info = ""

    def start_ul(self, attr):
        self.is_awards_ul = match_attr(attr, "class", "award")

    def end_ul(self):
        if self.is_awards_ul:
            self.is_awards_ul = False
            self.movie_detail.add_award(self.current_award)

    def handle_data(self, data):
        if self.is_title:
            self.movie_detail.set_name(data)
        if self.is_movie_info:
            self.current_info += data
        if self.is_rate:
            self.movie_detail.set_rate(data)
        if self.is_voter_num:
            self.movie_detail.set_voter_num(data)
        if self.is_rate_detail:
            self.movie_detail.add_rate_detail(data)
        if self.is_abstract:
            self.movie_detail.add_abstract(data)
        if self.is_awards_ul:
            self.current_award.append(data)

    def feed(self, data):
        super().feed(self.__replace_illegal_tags__(data))

    @staticmethod
    def __replace_illegal_tags__(content):
        illegal_br_pattern = re.compile("<br/>")
        return illegal_br_pattern.sub("<br>", content)


class DoubanReviewCatalogParser(SGMLParser):
    def __init__(self):
        super().__init__()
        self._review_url_list = []
        self.is_review_div = False

    def start_h3(self, attr):
        self.is_review_div = True

    def end_h3(self):
        if self.is_review_div:
            self.is_review_div = False

    def start_a(self, attr):
        if self.is_review_div:
            is_title = find_attr(attr, "title")
            attr_class = find_attr(attr, "class")
            if is_title and attr_class != "review-hd-avatar":
                review_url = find_attr(attr, "href")
                self._review_url_list.append(review_url)

    def get_results(self):
        return self._review_url_list

    def feed(self, data):
        self._review_url_list.clear()
        super().feed(data)


class DoubanReviewPageParser(SGMLParser):
    def __init__(self, movie_id, review_id):
        super().__init__()
        self.movie_id = movie_id
        self.review_id = review_id

        self.review_info = MovieReview()
        self.review_info.set_id(review_id)
        self.review_info.set_movie_id(movie_id)

        self.is_review_div = False
        self.review_content = ""

        self.is_useful_div = False
        self.is_useful = False
        self.is_useless = False
        self.is_rate = False
        self.is_author = False
        self.is_time = False

    def start_div(self, attr):
        if match_attr(attr, "property", "v:description"):
            self.is_review_div = True
        if match_attr(attr, "class", "main-panel-useful"):
            self.is_useful_div = True

    def end_div(self):
        if self.is_review_div:
            self.is_review_div = False
            self.review_info.set_review(self.review_content)
        if self.is_useful_div:
            self.is_useful_div = False

    def start_em(self, attr):
        if self.is_useful_div:
            if match_attr(attr, "id", "ucount%su" % self.review_id):
                self.is_useful = True
            if match_attr(attr, "id", "ucount%sl" % self.review_id):
                self.is_useless = True

    def end_em(self):
        if self.is_useful:
            self.is_useful = False
        if self.is_useless:
            self.is_useless = False

    def start_span(self, attr):
        if match_attr(attr, "property", "v:rating"):
            self.is_rate = True
        if match_attr(attr, "property", "v:reviewer"):
            self.is_author = True
        if match_attr(attr, "property", "v:dtreviewed"):
            self.is_time = True

    def end_span(self):
        if self.is_rate:
            self.is_rate = False
        if self.is_author:
            self.is_author = False
        if self.is_time:
            self.is_time = False

    def handle_data(self, data):
        if self.is_review_div:
            self.review_content += data
        if self.is_useful:
            self.review_info.set_useful(data)
        if self.is_useless:
            self.review_info.set_useless(data)
        if self.is_rate:
            if data != "None":
                self.review_info.set_rate(data)
        if self.is_author:
            self.review_info.set_author(data)
        if self.is_time:
            self.review_info.set_time(data)


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

if __name__ == '__main__':
    # parser = DoubanMovieCatalogParser()
    # with open("爱情电影主页.html", "r", encoding="utf-8") as page:
    #     pageContent = page.read()
    #     parser.feed(pageContent)
    #     movieInfoList = parser.get_results()
    #     print(movieInfoList)

    # parser = DoubanMoviePageParser("https://movie.douban.com/subject/19944106/?from=tag")
    # with open("泰坦尼克号.html", "r", encoding="utf-8") as page:
    #     pageContent = page.read()
    #     parser.feed(pageContent)
    #     print(parser.movie_detail)

    parser = DoubanReviewCatalogParser()
    with open("resources/纽约纽约全部影评.html", "r", encoding="utf-8") as page:
        pageContent = page.read()
        parser.feed(pageContent)
        reviewUrlList = parser.get_results()
        print("%d reviews found. " % len(reviewUrlList))
        print(reviewUrlList)

    # parser = DoubanReviewPageParser("1292722", "1729154")
    # with open("泰坦尼克号影评.html", "r", encoding="utf-8") as page:
    #     pageContent = page.read()
    #     parser.feed(pageContent)
    #     print(parser.review_info)
