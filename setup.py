from setuptools import setup

APP_NAME = "django-invoice2"
VERSION = '0.1'

setup(
    name=APP_NAME,
    version=VERSION,
    description='Pluggable django invoicing app',
    packages=[
        'invoice',
        'invoice.utils',
        'invoice.exports',
        'invoice.test_data'
    ],
    include_package_data=True,

    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    license="GPL v3",
    url='http://pypi.python.org/pypi/{0}/'.format(APP_NAME),
    keywords="django invoice pdf",

    install_requires=[
        "django>=1.8",
    ],
)
