from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext_modules = [Extension("*", ["sentimental/*.pyx"],
                         extra_compile_args=["-O3"])]

setup(
    name="sentimental",
    packages=["sentimental"],
    install_requires=[
        "scikit-learn==0.14.1",
        "marisa-trie==0.6",
        "pandas==0.13.1",
        "numpy==1.8.1",
        "networkx==1.8.1",
        "nltk==2.0.4",
        "joblib==0.7.1",
        "tweepy==2.2",
        "requests==2.2.1",
        "lxml==3.3.5",
    ],
    ext_modules=cythonize(ext_modules)
)
