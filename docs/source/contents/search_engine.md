Search Engine
-------------

uniCMS uses MongoDB as search engine, it was adopted in place of others search engines like Elastic Search or Sorl for the following reasons:

- The documents stored are really small, few kilobytes (BSON storage)
- Collections would be populated on creation/change/deletion events by **on_$event hooks**
- Each entry is composed following a small schema, this would reduce storage usage, increasing general performances at the same time

Technical specifications are available in [MongoDB Official Documentation](https://docs.mongodb.com/manual/core/index-text/).
Some usage example also have been posted [here](https://code.tutsplus.com/tutorials/full-text-search-in-mongodb--cms-24835).

An document would be as follows (see `cms.search.models`)

````
entry = {
            "title": "Papiri, Codex, Libri. La attraverso labora lorem ipsum",
            "heading": "Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.",
            "content_type": "cms.publications.Publication",
            "content_id": "1",
            "image": "/media/medias/2020/test_news_1.jpg",
            "content": "<p>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?</p><p>&lt;h1&gt;This HTML is escaped by default!&lt;/h1&gt;</p><p>&nbsp;</p>",
            "sites": [
                "test.unical.it"
            ],
            "urls": [
                "//test.unical.it/portale/dipartimenti/dimes/contents/news/view/unical-campus-1",
                "//test.unical.it/portale/contents/news/view/unical-campus-1"
            ],
            "tags": [],
            "categories": [
                "Didattica"
            ],
            "indexed": "2020-12-09T15:00:18.151000",
            "published": "2020-11-09T13:24:35",
            "viewed": 0,
            "relevance": 0.5714285714285714,
            "language": "italian",
            "translations": [
                {
                    "language": "english",
                    "title": "gdfg",
                    "subheading": "dfgdfgdf",
                    "content": "<p>dfgdfgdfg</p>"
                }
            ],
            "day": 9,
            "month": 11,
            "year": 2020
        },
````

##### Search Engine CLI

Publication and Page models configures by default some save_hooks, like the search engine indexers.
Search Engine indexes can be rebuilt with a management command (SE cli):

````
# show all the publications of the first November 2020
./manage.py cms_search_content_sync -type cmspublications.Publication -d 1 -y 2020 -m 11 -show

# Purge all the entries, renew and finally show them
./manage.py cms_search_content_sync -y 2020 -type cmspages.Page -purge -insert -show

# purge all the publications published in year 2020
./manage.py cms_search_content_sync -type cmspublications.Publication  -purge -y 2020

# clean up all the Publications posted in December 2020
./manage.py cms_search_content_sync -type cmspublications.Publication -m 12 -y 2020 -purge -insert
````

`cms_search_content_sync` rely on `settings.MODEL_TO_MONGO_MAP` that defines which functions 
are involved respectively for each Model Type.

```
MODEL_TO_MONGO_MAP = {
    'cmspages.Page': 'cms.search.models.page_to_entry',
    'cmspublications.Publication': 'cms.search.models.publication_to_entry'
}
````

##### Search Engine Behavior

Let's suppose we are searching these words upon the previous entry.
These all matches:

- "my blog"
- "than reality"
- "rien la reliti"
- "my!"

These will not match:

- 'rien -"de plus"'
- '"my!"'
- '-nothing'

As we can see symbols like `+` and `-` will exlude or include words.
Specifying "some bunch of words" will match the entire sequence.
