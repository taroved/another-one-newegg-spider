
from scrapy.contrib.loader.processor import Compose, Join, TakeFirst, MapCompose
from scrapy.contrib.loader import ItemLoader

from neweggs.items import NeweggItem


def skip_empty_price(price_pieces):
    if len(price_pieces) < 2:
        return None
    else:
        return price_pieces


class NeweggProcessor(ItemLoader):
    default_item_class = NeweggItem

    default_output_processor = TakeFirst()
    title_out = Compose(TakeFirst(), unicode.strip)
    image_out = Compose(TakeFirst(),
                        lambda x, loader_context: loader_context.get('image_tpl') % x)
    price_out = Compose(
        skip_empty_price, Join(''), lambda x: x.replace('USD', '$'))
