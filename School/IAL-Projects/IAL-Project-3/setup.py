from setuptools import setup, find_packages

setup(
    name='intruder_alert_system',
    version='1.0.0',
    author='Aditya Sharma, Alexander Laudino',
    author_email='as4108@scarletmail.rutgers.edu, asl172@scarletmail.rutgers.edu',
    description='A probabilistic intruder catch task with bot strategies',
    long_description=open('docs/README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/adityas0911/IAL-Project-2/',
    packages=['bots', 'ship', 'transition'], 
    package_dir={'': 'src'}, 
    py_modules=['main'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'matplotlib',
        'pandas',
        'pygame',
        'tqdm',
        'scipy',
        'plotly',
        'pyyaml',
        'kaleido'
    ],
    extras_require={
        'dev': ['pytest', 'flake8'],
    },
    entry_points={
        'console_scripts': [
        ],
    },
    include_package_data=True,
    zip_safe=False,
)