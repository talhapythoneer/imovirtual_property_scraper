import scrapy
from scrapy.crawler import CrawlerProcess
from random import randrange

url = "https://www.imovirtual.com/comprar/apartamento/aveiro/?search%5Bfilter_enum_rooms_num%5D%5B0%5D=1&search" \
      "%5Border%5D=filter_float_price%3Aasc&search%5Bregion_id%5D=1&search%5Bsubregion_id%5D=5 "


class Playbook(scrapy.Spider):
    name = "PostcodesSpider"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'ExtractedData.csv',
        'CONCURRENT_REQUESTS': '1',
        # 'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def start_requests(self):
        yield scrapy.Request(url=url + "&nrAdsPerPage=72",
                             callback=self.parse, dont_filter=True,
                             headers={
                                 'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                               "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                             },
                             )

    def parse(self, response):
        links = response.css("header.offer-item-header > h3 > a::attr(href)").extract()
        for link in links:
            yield scrapy.Request(url=link,
                                 callback=self.parse2, dont_filter=True,
                                 headers={
                                     'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                                   "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                                 },
                                 )

        nextPage = response.css("li.pager-next > a::attr(href)").extract_first()
        if nextPage:
            yield scrapy.Request(url=nextPage,
                                 callback=self.parse, dont_filter=True,
                                 headers={
                                     'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                                   "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                                 },
                                 )

    def parse2(self, response):
        title = response.css("h1[data-cy='adPageAdTitle']::text").extract_first()

        location = response.css("div[aria-label='Endereço'] > a::text").extract_first()
        if not location:
            location = ""

        price = response.css("strong[data-cy='adPageHeaderPrice']::text").extract_first()
        if not price:
            price = ""

        priceM2 = response.css("div[aria-label='Preço por metro quadrado']::text").extract_first()
        if not priceM2:
            priceM2 = ""

        area = response.css("div[aria-label='Área útil (m²)'] > div:nth-of-type(2)::text").extract_first()
        if not area:
            area = ""

        toppology = response.css("div[aria-label='Tipologia'] > div:nth-of-type(2)::text").extract_first()
        if not toppology:
            toppology = ""

        bedrooms = response.css("div[aria-label='Casas de Banho'] > div:nth-of-type(2)::text").extract_first()
        if not bedrooms:
            bedrooms = ""

        condition = response.css("div[aria-label='Condição'] > div:nth-of-type(2)::text").extract_first()
        if not condition:
            condition = ""
        listingID = response.css("script#__NEXT_DATA__::text").extract_first()
        listingID = listingID.split(r'"ad_id":"')[-1].split(r'",')[0]
        # listingID = listingID.split(" ")[-1].strip()

        agencyName = response.css("a.css-1jrsoxk.e1uw9mmq0::text").extract_first()
        if not agencyName:
            agencyName = ""

        img = response.css("picture:nth-of-type(1) > img::attr(src)").extract_first()
        yield {
            "Title": title.strip(),
            "Price": price.strip(),
            "Price/M2": priceM2.strip(),
            "AreaM2": area.strip(),
            "Topology": toppology.strip(),
            "Bedrooms": bedrooms.strip(),
            "Condition": condition.strip(),
            "Location": location.strip(),
            "AgencyName": agencyName.strip(),
            "ListingID": listingID,
            "ImageURL": img,
            "DetailsPage": response.url
        }

process = CrawlerProcess()
process.crawl(Playbook)
process.start()
