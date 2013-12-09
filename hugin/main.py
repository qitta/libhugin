#!/usr/bin/env python
# encoding: utf-8

from hugin.core import Session

if __name__ == '__main__':
    def read_list_async():
        hs = Session(parallel_jobs=15, timeout_sec=5)
##        signal.signal(signal.SIGINT, hs.signal_handler)
        f = open('./hugin/core/testdata/imdbid_small.txt').read().splitlines()
        futures = []
        #f = [2]
        for imdbid in f:
            q = hs.create_query(
                type='movie',
                search_text=True,
                cache=False,
                search_pictures=True,
                language='en',
                retries=5,
                imdbid='{0}'.format(imdbid),
                strategy='deep',  # or flat
                amount=5
            )
            futures.append(hs.submit_async(q))

        while len(futures) > 0:
            for item in futures:
                if item.done():
                    try:
                        t = item.result()
                        for iitem in t:
                            if iitem._result_dict:
                                print(iitem._result_dict['title'])
                    except Exception as e:
                        print('error getting result', e)
                    futures.remove(item)
        hs._cache.close()

    def read_list_sync():
        hs = Session(parallel_jobs=2, timeout_sec=5, parallel_downloads_per_job=5)
        #signal.signal(signal.SIGINT, hs.signal_handler)
        f = open('./hugin/core/testdata/imdbid_huge.txt').read().splitlines()
        #f = ['tt2524674']
        for imdbid in f:
            q = hs.create_query(
                type='movie',
                search_text=True,
                cache=False,
                search_pictures=True,
                language='en',
                retries=5,
                imdbid='{0}'.format(imdbid),
                strategy='deep',  # or flat
                amount=5
            )
            result_list = hs.submit(q)
            #print(100 * '-')
            #pp, *other = hs.get_postprocessing()
            #result_list += custom
            for item in result_list:
                if item.result_dict:
                    print(item)
                    print()
                    print('title:', item._result_dict['title'])
                    print('genre:', item._result_dict['genre'])
                    print('genre_normalized:', item._result_dict['genre_norm'])
                    #print(item._result_dict['plot'])
                    print()
                    print(100 * '-')
        hs._cache.close()
    try:
        read_list_sync()
    except KeyboardInterrupt:
        print('Interrupted by user.')
