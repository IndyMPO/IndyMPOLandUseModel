import os,sys
from subprocess import call

with open(sys.argv[1], 'r') as in_script:
    out_script = open(sys.argv[2].replace("'", '')+'.ctl', 'w')
    for line in in_script:
        out_script.write(line.format(*sys.argv[2:]))
out_script.close()
call(r'C:\Program Files (x86)\Citilabs\CubeLand\CubeLand.exe ' + out_script.name + ' /W=1234')
os.remove(out_script.name)
