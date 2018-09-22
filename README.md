# sortedwalk
Generate the files of a root directory like os.walk
but in a sorted order, and with an expanded set of 
functions.

For example, you can retrieve the parent, child, 
sibling, or cousin directories of the current 
directory you are traversing over. 

# Usage

The object produced by sortedwalk is an iterator and
should be used as such to generate the current directory,
the directory names and file names of the current directory.
```
  walk = SortedWalk(input_dir, None)
  for (dirpath, dirnames, filenames) in walk:
    print(dirpath, filenames)
```


