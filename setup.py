from setuptools import setup

setup(
    name="django-invoice2",
    version="0.1.1",
    description='Pluggable django invoicing app',
    packages=[
        'invoice',
        'invoice.exports',
        'invoice.migrations',
        'invoice.templatetags',
        'invoice.utils',
    ],
    package_data={
        "invoice": [
            "static/invoice/*",
            "templates/admin/invoice/invoice/*.html",
            "templates/invoice/*.html",
            "locale/*/LC_MESSAGES/*",
        ]
    },
    include_package_data=True,

    author='Tomas Peterka',
    author_email='prestizni@gmail.com',
    license="MIT",
    keywords="django invoice pdf",
    url="https://github.com/katomaso/django-invoice",
    install_requires=[
        "django>=1.8",
        "reportlab",
    ],
)
