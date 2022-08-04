from setuptools import setup

setup(
    name='conversations',
    version='0.1.0',    
    description='conversations is a tool that helps you find interactional sequences from a collection of annotated time-stamped segments.',
    url='https://github.com/LAAC-LSCP/conversations',
    author='Willian N. Havard',
    author_email='william.havard@gmail.com',
    license='MIT',
    packages=['conversations'],
    install_requires=['pandas'],
    extra_requires=['graphviz'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',        
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
