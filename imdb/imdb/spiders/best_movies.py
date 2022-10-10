import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class BestMoviesSpider(CrawlSpider):
    name = 'best_movies'
    allowed_domains = ['web.archive.org']
    start_urls = [
        'http://web.archive.org/web/20200715000935/https://www.imdb.com/search/title/?groups=top_250&sort=user_rating']
    # user_agent를 settings.py에 직접 추가하는것보다, 여기와 start_requests, 그리고 LinkExtractor(혹은 requests)에 직접 입력해주는 것이 좋음
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'

    def start_requests(self):
        yield scrapy.Request(url='http://web.archive.org/web/20200715000935/https://www.imdb.com/search/title/?groups=top_250&sort=user_rating',
                             headers={
                                 'User-Agent': self.user_agent
                             })

    rules = (
        # rule은 라인바이라인으로 이동하므로 페이지네이션 룰은 마지막에 넣어야함
        # 현재 페이지 내에서 이동하고 싶은 url을 가진 xpath 혹은 css를 찾아서, parse로직을 타도록 함
        Rule(LinkExtractor(restrict_xpaths="//h3[@class='lister-item-header']/a"),
             callback='parse_item', follow=True, process_request='set_user_agent'),
        # 페이지네이션도 rule로 등록해서 사용가능하다
        Rule(LinkExtractor(
            restrict_xpaths="(//a[@class='lister-page-next next-page'])[2]"),
            process_request='set_user_agent')
    )

    # scrapy 2버전 이후로는 spider도 req에 넣어줘야 함. 안그러면 에러
    def set_user_agent(self, request, spider):
        request.headers['User-Agent'] = self.user_agent
        return request

    def parse_item(self, response):
        yield {
            'title': response.xpath("//div[@class='title_wrapper']/h1/text()").get(),
            'year': response.xpath("//span[@id='titleYear']/a/text()").get(),
            'duration': response.xpath("normalize-space((//time)[1]/text())").get(),
            'genre': response.xpath("//div[@class='subtext']/a[1]/text()").get(),
            'rating': response.xpath("//span[@itemprop='ratingValue']/text()").get(),
            'movie_url': response.url,
            'user_agent': response.request.headers['User-Agent'],
        }
