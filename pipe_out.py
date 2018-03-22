from subprocess import Popen, PIPE, CalledProcessError
import fnmatch

"""pipe_out.py -- run sub process command and parse output to look for specific keywords in output"""

with Popen('ls', stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in p.stdout:
        print(line, end='') # process line here
        line_list.append(line)

if p.returncode != 0:
    raise CalledProcessError(p.returncode, p.args)

else:
    print(line_list)
    error_filtered = fnmatch.filter(line_list, 'pipe_out.py*')
    print('error:', error_filtered)
    success_filtered = fnmatch.filter(line_list, 'dir_compare_db_san.py*')
    print('success:', success_filtered)




