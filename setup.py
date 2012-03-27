from setuptools import setup, find_packages

setup(
    name = "phizer",
    version = "0.2.1",
    packages = find_packages(),
    install_requires = ['PIL'],
    entry_points = {
        'console_scripts': [
            'phizer = phizer.main:main',
        ],
        },
    author = "Andrew Gwozdziewycz",
    author_email = "apg@okcupid.com",
    description = "Image resizer proxy",
    license = "GPL",
    keywords = "image photo resizer proxy",
    url = "http://github.com/m8apps/phizer",
)
