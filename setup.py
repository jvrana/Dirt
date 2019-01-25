from distutils.core import setup


tests_require = [
    "pytest"
]

install_requires = [
    "pydent",
    "networkx"
]

# setup
setup(
        name='dirtio',
    title='dirtio',
        install_requires=install_requires,
        python_requires='>=3.4',
        tests_require=tests_require,
)
