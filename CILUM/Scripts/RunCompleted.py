from tkMessageBox import *
from Tkinter import *
import os
from subprocess import Popen

Tk().withdraw() #Makes an unnecessary box not appear
scenario_dir = os.environ['CILUM']
summary_file = os.path.join(scenario_dir, r'FILES\{}Summary.xlsx'.format(os.path.split(scenario_dir)[1]))

Popen(summary_file, shell = True)

showinfo(title = 'Run Complete', message = 'Scenario {} run complete'.format(scenario_dir))
