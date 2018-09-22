import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name='sortedwalk',
  version='0.1',
  description='Recursively traverse files in a root directory.',
  url='http://github.com/shotesmagotes/sortedwalk',
  author='Shota Makino',
  author_email='shota.makino@yahoo.com',
  license='MIT',
  long_description=long_description,
  packages=setuptools.find_packages(),
  zip_safe=False
)