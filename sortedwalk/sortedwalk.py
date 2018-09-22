import os
import collections
from enum import Enum

class SiblingOpts(Enum):
    OLDER = "older"
    YOUNGER = "younger"
    ALL = "all"

class SortedWalk(object):
    '''Walks through a tree in a sorted fashion.
    '''
    def __init__(self, top, dir_sort, file_sort = None):
        
        if not os.path.isdir(top):
            raise TypeError

        # init sorting funcs
        if file_sort:
            self.file_sort = file_sort
        else:
            self.file_sort = dir_sort

        self.dir_sort = dir_sort

        # init make sure to set
        # and generate abspaths
        self._current_dir = top
        self._queue       = collections.deque([top])
        self._child_dirs  = self.get_children()
        self._top         = top

    @property
    def current_dir(self):
        return self._current_dir

    @current_dir.setter
    def current_dir(self, val):
        # makes sure every assignment
        # is set to a directory
        if not os.path.isdir(val):
            raise TypeError

        # ensure that it is absolute path
        # child paths follow this so this
        # must be maintained
        self._current_dir = os.path.abspath(val)

    def get_children(self, cur = None, isfile = False):
        l = s = None

        if not cur:
            cur = self.current_dir
        
        cur = os.path.abspath(cur)

        if isfile:
            # get all files in directory and use
            # the file sort func
            l = [
                m for m in os.listdir(cur) 
                if os.path.isfile(os.path.join(cur, m))
            ]
            s = self.file_sort
        else:
            # otherwise get all dirs in directory 
            # and use the dir sort
            l = [
                m for m in os.listdir(cur) 
                if not os.path.isfile(os.path.join(cur, m))
            ]
            s = self.dir_sort
        
        # sort list of directories before adding to queue
        # since 
        l.sort(key=s)
    
        return [os.path.join(cur, p) for p in l]
    
    def get_parent(self, cur = None):
        if cur == self._top:
            raise ValueError

        if not cur:
            cur = self.current_dir
        
        cur = os.path.abspath(cur)

        rel = os.path.relpath(cur, self._top)
        if os.pardir in rel:
            raise ValueError

        par = os.path.join(cur, os.pardir)
        return os.path.abspath(par)

    def get_siblings(self, cur = None, relation = SiblingOpts.ALL, isfile = False):
        """Gets the sibling files for the given file.

        Args:
            cur: The file to get sibling files for.
                File in this instance can be a directory 
                or a file.
            relation: The relationship to look for in the
                sibling files. If SiblingOpts.OLDER is 
                specified, all older sibling files will 
                be returned and vice-versa.
            isfile: True returns only files; False returns
                only directories.

        Returns:
            A list containing the sibling files in 
            sorted order from youngest to oldest.
        """
        if not cur:
            cur = self.current_dir

        cur = os.path.abspath(cur)

        # siblings are parent's children
        par = self.get_parent(cur)
        sib = self.get_children(par, isfile = isfile)

        ind = SortedWalk.sortedpathsearch(sib, key = cur, issorted = True)
        
        # sib list is in order of the given key
        # function so it is safe to return slices as is
        if relation == SiblingOpts.OLDER:
            # covers the case that ind > len(sib)
            return sib[ind + 1:]
        elif relation == SiblingOpts.YOUNGER:
            return sib[:ind]
        else:
            return sib[:ind] + sib[ind + 1:]

    def get_cousins(self, cur = None, relation = SiblingOpts.ALL, isfile = False, isflat = False):
        """Get cousin files given a file.

        Returns:
            An array of arrays where each top level
            array denotes a parent directory of the
            current file, and the second level arrays
            denote the children of those parents, or 
            equivalently the cousin files of the given
            file. For example:
                >>> get_cousins(cur = os.getcwd(), relation = SiblingOpts.OLDEST)
                [   
                    [../older_sibling/youngest_sibling, ..., ../older_sibling/oldest_sibling],
                    ...
                    [../oldest_sibling/youngest_sibling, ..., ../oldest_sibling/youngest_sibling]
                ]
                >>> get_cousins(cur = os.getcwd(), relation = SiblingOpts.OLDEST, isFlat = True)
                [
                    ../older_sibling/youngest_sibling, ..., ../older_sibling/oldest_sibling, 
                    ../oldest_sibling/youngest_sibling, ..., ../oldest_sibling/youngest_sibling
                ]
        """
        if not cur:
            cur = self.current_dir

        par = self.get_parent(cur)
        unc = self.get_siblings(par, relation = relation)

        # unc comes in sorted order of youngest to
        # oldest so it is safe to consider them in
        # order
        unflat = [self.get_children(u, isfile = isfile) for u in unc]

        if isflat:
            flat = []
            for uncle_children in unflat:
                flat.extend(uncle_children)
            return flat

        return unflat

    def __iter__(self):
        return self

    def __next__(self):
        cur = None

        try:
            # maintains breadth first search
            cur = self._queue.popleft()
        except IndexError:
            # end of queue
            raise StopIteration
        
        if cur:            
            dirlist = self.get_children(cur)
            fillist = self.get_children(cur, isfile = True)

            # update siblings upon entering new level
            if cur in self._child_dirs:
                self._child_dirs = dirlist
                
            # maintains breadth first search
            self._queue.extend(dirlist)
            self.current_dir = cur

        return (self.current_dir, dirlist, fillist)

    next = __next__

    @staticmethod
    def sortedpathsearch(names, key, sortfunc = None, issorted = False, ispath = True):
        # fix up key to reflect basename
        key = os.path.basename(os.path.normpath(key))

        bn = []

        # if the elements are paths we strip
        # the dirs from the elements
        if ispath:
            if len(names) > 1:
                cp = nt_common_path(names)
            else:
                cp = os.path.basename(names[0])

            # check that all files are in the 
            # same dir while we strip the dir for
            # base names
            bn = [
                os.path.basename(e) for e in names 
                if os.path.basename(e) and cp in os.path.split(e)
            ]

            # names contains dirs or contains a file 
            # that is in a child dir
            if len(names) != len(bn):
                raise TypeError
        else:
            # do this because we mutate bn later on
            # otherwise it will cause unwanted side effect
            # of changing the arg names
            bn = [n for n in names]
            
        if not issorted:
            bn.sort(key = sortfunc)

        for i in range(len(bn)):
            if key == bn[i]:
                return i
        return None

# python2 helper
def nt_common_path(paths):
    sep = '\\'
    altsep = '/'
    curdir = '.'
    
    try:
        drivesplits = [os.path.splitdrive(p.replace(altsep, sep).lower()) for p in paths]
        split_paths = [p.split(sep) for _, p in drivesplits]

        try:
            isabs, = set(p[:1] == sep for d, p in drivesplits)
        except ValueError:
            raise ValueError("Can't mix absolute and relative paths")
        
        if len(set(d for d, p in drivesplits)) != 1:
            raise ValueError("Paths don't have the same drive")
        
        drive, path = os.path.splitdrive(paths[0].replace(altsep, sep))
        common = path.split(sep)
        common = [c for c in common if c and c != curdir]

        split_paths = [[c for c in s if c and c != curdir] for s in split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        for i, c in enumerate(s1):
            if c != s2[i]:
                common = common[:i]
                break
        else:
            common = common[:len(s1)]

        prefix = drive + sep if isabs else drive
        return prefix + sep.join(common)
    except (TypeError, AttributeError):
        raise
