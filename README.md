# Transforms
This poorly named _transforms_ project (should really be called 'commons' or something similiar)
contains three basic file types that are common resources to various protection profile projects.
These three types are:
* XSL Files, in the project's top directory, which transform the protection profile input file into
  various readable html documents
* Schema Files (currently just schema.rng) in the _schemas_ directory, which defines, roughly, the structure of an input file
* Dictionary files, in the _dictionaries_ directory, which include various lists of words that are frequently used by protection
profiles but not recognized by _hunspell_, a spell checker we use.

This project is meant to be used as a submodule to other CC projects. 

## Links
[Help working with Transforms Submodule](https://github.com/commoncriteria/transforms/wiki/Working-with-Transforms-as-a-Submodule)
