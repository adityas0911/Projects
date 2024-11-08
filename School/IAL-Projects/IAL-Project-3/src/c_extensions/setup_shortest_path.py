from setuptools import setup, Extension

module = Extension('shortest_path',
                    sources=['shortest_path.c'])

setup(name='ShortestPath',
      version='1.0',
      description='Shortest path algorithm in C',
      ext_modules=[module])