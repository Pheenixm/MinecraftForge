import os
import sys
import fnmatch
import shlex
import difflib
import time

def cmdsplit(args):
    if os.sep == '\\':
        args = args.replace('\\', '\\\\')
    return shlex.split(args)
                    
def cleanDirs(path):
    if not os.path.isdir(path):
        return
 
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                cleanDirs(fullpath)
 
    files = os.listdir(path)
    if len(files) == 0:
        os.rmdir(path)
        
def main():
    print("Creating patches")
    mcp = os.path.normpath(sys.argv[1])
    forge_dir = os.path.normpath(sys.argv[2])
    patchd = os.path.normpath(os.path.join(forge_dir, 'patches'))
    base = os.path.normpath(os.path.join(mcp, 'src_base'))
    work = os.path.normpath(os.path.join(mcp, 'src_work'))
    
    for path, _, filelist in os.walk(work, followlinks=True):
        for cur_file in fnmatch.filter(filelist, '*.java'):
            file_base = os.path.normpath(os.path.join(base, path[len(work)+1:], cur_file)).replace(os.path.sep, '/')
            file_work = os.path.normpath(os.path.join(work, path[len(work)+1:], cur_file)).replace(os.path.sep, '/')
            
            fromlines = open(file_base, 'U').readlines()
            tolines = open(file_work, 'U').readlines()
            
            patch = ''.join(difflib.unified_diff(fromlines, tolines, '../' + file_base[len(mcp)+1:], '../' + file_work[len(mcp)+1:], '', '', n=3))
            patch_dir = os.path.join(patchd, path[len(work)+1:])
            patch_file = os.path.join(patch_dir, cur_file + '.patch')
            
            if len(patch) > 0:
                print patch_file[len(patchd)+1:]
                patch = patch.replace('\r\n', '\n')
                
                if not os.path.exists(patch_dir):
                    os.makedirs(patch_dir)
                with open(patch_file, 'wb') as fh:
                    fh.write(patch)
            else:
                if os.path.isfile(patch_file):
                    print("Deleting empty patch: %s"%(patch_file))
                    os.remove(patch_file)
                    

    cleanDirs(patchd)
    
if __name__ == '__main__':
    main()