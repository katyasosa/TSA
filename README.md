Twitter Sentiment Analizer
=============================

Установка
-----------
Перед началом работы убедитесь, что у вас установлены Python и менеджер пакетов `pip`. Чтобы
установить все необходимые зависимости, запустите команду

`
pip install requirements.txt
`

Следующая команда компилирует соответствующий код на Cython, необходимый для работы, в C

`
python setup.py build_ext --inplace
`

Данные
--------

- Для работы необходимы данные. Например, собранные проектом [Sentiment140](sentiment140.com). Эти
данные были дополненны собранными самостоятельно, но использовать можно хотя бы только их.

- [abbr.marisa](https://github.com/katyasosa/TSA/blob/master/abbr.marisa) -- бор, который строится по словарю [No slang](http://www.noslang.com/) скриптом
[fetch_noslang.py](https://github.com/katyasosa/TSA/blob/master/sentimental/fetch_noslang.py)
