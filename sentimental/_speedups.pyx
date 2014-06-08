def _char_bi_ngrams(unicode text_document, size_t n, unicode pad):
    cdef size_t text_len = len(text_document)

    # add the first bi-ngram.
    cdef list ngrams = [text_document[:n].rjust(2 * n, pad)]

    cdef size_t i
    cdef unicode ngram
    for i in range(n, text_len, n):
        if not i:  # first n-gram.
            ngram = text_document[:n].rjust(2 * n, pad)
        else:
            ngram = text_document[(i - n):(i + n)]

        ngrams.append(ngram)

    # add the last bi-ngram.
    ngrams.append(text_document[text_len - text_len % n:].ljust(2 * n, pad))

    return ngrams
