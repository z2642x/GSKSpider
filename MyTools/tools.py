import gzip
import http.cookiejar
import re
import urllib.error
import urllib.parse
import urllib.request

__name__ = "MyTools"


class URLTool:
    @staticmethod
    def get_url_opener(header, proxy_ip="", proxy_port="", need_cookie=False):
        proxy_handler = None
        if proxy_ip != "" and proxy_port != "":
            proxy = {"http": "http://%s:%s" % (proxy_ip, proxy_port)}
            proxy_handler = urllib.request.ProxyHandler(proxy)

        if need_cookie:
            cookie_processor = urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
            if proxy_handler is not None:
                opener = urllib.request.build_opener(cookie_processor, proxy_handler)
            else:
                opener = urllib.request.build_opener(cookie_processor)
        else:
            if proxy_handler is not None:
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()

        # header_list = []
        # for key, value in header.items():
        #     elem = (key, value)
        #     header_list.append(elem)
        opener.addheaders = header
        return opener

    @staticmethod
    def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
        import zlib
        try:               # so on top of all there's this workaround:
            return zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return zlib.decompress(data)

    @staticmethod
    def get_response_content(url_response):
        content_encoding = url_response.getheader('Content-Encoding')
        if content_encoding is not None and 'gzip' in content_encoding:
            page_content = gzip.decompress(url_response.read())
        else:
            try:
                page_content = gzip.decompress(url_response.read())
            except OSError:
                try:
                    page_content = URLTool.deflate(url_response.read())
                except:
                    page_content = url_response.read()
        page_content = page_content.decode('utf-8')
        return page_content

    @staticmethod
    def get_page_content(opener, url, data=None):
        try:
            url_response = opener.open(url, data)
            content_encoding = url_response.getheader('Content-Encoding')
            if content_encoding is not None and 'gzip' in content_encoding:
                page_content = gzip.decompress(url_response.read())
            else:
                page_content = url_response.read()
            # page_content = gzip.decompress(url_response.read())
            page_content = page_content.decode('utf-8', "replace")
            return page_content
        except UnicodeDecodeError as e:
            print(e)
            print("Error occured when fetching %s" % url)
            return None

    @staticmethod
    def add_keyword_to_suffix(keywords, parameter_type, logic):
        if keywords is None:
            return ""

        if logic is not None and len(logic) < len(keywords) - 1:
            raise IndexError

        suffix = ""
        if isinstance(keywords, list):
            suffix += "(" * len(keywords) + "\"" + keywords[0] + "\"" + parameter_type + ")"
        if isinstance(keywords, str):
            suffix += "(" + "\"" + keywords + "\"" + parameter_type + ")"
        i = 1
        if logic is not None:
            while i < len(keywords):
                suffix += " " + logic[i] + " \"" + keywords[i] + "\"" + parameter_type + ")"
        return suffix

    @staticmethod
    def get_host_url(url):
        host_pattern = re.compile("http://(\w+\.){2}\w+")
        is_matched = re.search(host_pattern, url)
        if is_matched is not None:
            return is_matched.group()
        return ""


class HTMLTool:
    @staticmethod
    def remove_html_marks(html_str):
        remove_pattern = re.compile("</?b>")
        plain_str = remove_pattern.sub("", html_str)
        return plain_str

    @staticmethod
    def download_resource(response, filename):
        data = response.read()
        with open(filename, 'wb') as content:
            content.write(data)

    @staticmethod
    def is_legal_page_url(url, illegal_suffix):
        if not (url.startswith("http") or url.startswith("/")):
            return False
        for suffix in illegal_suffix:
            if url.endswith(suffix):
                return False
        return True


class FileTool:
    @staticmethod
    def make_directory(dir_path):
        import os
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
