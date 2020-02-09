# Crawl sites and extract content via Python

These Python modules allow for basic site crawling and ngram extraction.  Ngram analysis can help identify content gaps and a page's ability to rank for keywords, topics, and content contained with.

## Site Crawling

The threaded crawler parses a starting page's HTML and then extracts all internal links from on-page anchors.  Those URLs are added to a queue for crawling and link extraction.  Individual crawl workers pull the next uncrawled URL from the queue, request the page's HTML, extract links and content, and then store the results.

### URL and Domain Parsing

The threaded crawler contains a URL parser to match against sub-domains and other portions of URLs to determine if they should be crawled.

### Redirects

Redirects are not automatically followed - instead each destination URL is added to the queue (if it's on the same domain) for processing later.

## Ngram Extraction

The ngrammer uses common word boundaries (symbols, punctuations, linebreaks) and stop words to extract meaningful ngrams from source content (ngram length can be modified).  Ngrams are generated without begining or ending stop words but can contain internal stop words.  This can help identify complex or longer phrases.
