import argparse
from functools import reduce

from offer_listing import OfferListing


def main(base_url: str, keyword: str):
    s = OfferListing(base_url)
    l = s.find_word(keyword)
    l = list(set(l))
    ss = reduce(lambda a, o: a + "\n" + o.toJSON(), l, '')
    with open('result_' + keyword, 'w') as f:
        f.write(ss)


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('base_search')
    args.add_argument('keyword')
    argv = args.parse_args()

    main(argv.base_search, argv.keyword)
