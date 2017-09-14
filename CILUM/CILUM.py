'''
Running this script creates a user interface for running the Central Indiana Land Use Model (CILUM).
Copyright 2017 Indianapolis Metropolitan Planning Organization
'''
from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *
from easygui import enterbox
from subprocess import Popen
import os
from shutil import copy, copytree
import time
from Scripts.util import check_scenario_directory

__version__ = 0.2

master = Tk()
master.wm_title('CILUM {}'.format(__version__)) #Window title

#Create application title
title = Label(master, text = 'Central Indiana Land Use Model', font = ('System', 18, 'bold'), background = '#000f5d', foreground = '#ffe700')
title.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)

#Create Webdings pictures
pics = Label(master, text = 'BBKFFSCCGCCSFFKBB', font = ('Webdings', 18), foreground = '#000f5d')
pics.grid(row = 1, column = 0, columnspan = 2)

#Create label for box for scenario directory entry
current_scenario = Label(master, text = '\nCurrent Scenario:')
current_scenario.grid(row = 3, column = 0, columnspan = 2)

#Create box for scenario directory entry
scenario_box = Entry(master, width = 70)
scenario_box.grid(row = 4, column = 0, columnspan = 2)

os.environ['CILUM'] = scenario_box.get()

################################################### BUTTON COMMANDS ########################################################################

def select_scenario():
    '''
    Opens up a dialog box so the user can select a scenario directory
    '''
    global scenario_box

    #Ask the user for the scenario directory
    scenario_dir = askdirectory(initialdir = os.getcwd(),
                                title = 'Choose Scenario Directory',
                                mustexist = True)

    #Place the name of the directory into the box
    scenario_box.delete(0, END)
    scenario_box.insert(0, scenario_dir)

    #Create environment variable for the scenario directory
    os.environ['CILUM'] = scenario_dir

def create_scenario():
    '''
    Creates a scenario
    '''
    fixed_supply = askyesno('Select Model Type', 'Is the new scenario a fixed-supply scenario?') #Returns a boolean that is TRUE if the scenario is fixed-supply and FALSE otherwise

    year = enterbox(msg = 'What year does the scenario take place in?')
    description = enterbox(msg = 'Provide a description of the scenario')
    
    #Scenario creation window
    creator = Toplevel()
    #creator.wait_window(scenario_type_selector)
    creator.wm_title('Create Scenario')
    creator.attributes('-topmost', True)

    #Create box for base scenario
    base_label = Label(creator, text = 'Base Scenario:')
    base_label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = E + W)

    base_box = Entry(creator, width = 60)
    base_box.grid(row = 0, column = 1, columnspan = 2, padx = 10, sticky = W)

    #Enter default base scenario
    base_box.delete(0, END)
    if fixed_supply:
        base_box.insert(0, r'C:\CILUM\Base\BaseYearFS')
    else:
        base_box.insert(0, r'C:\CILUM\Base\BaseYearVS')

    #Checkbox that indicates whether or not the new scenario is a child of the base scenario
    is_child = BooleanVar()
    child = Checkbutton(creator, text = 'Child of Existing Scenario', variable = is_child)
    child.grid(row = 1, column = 0, columnspan = 2, padx = 10, sticky = W)

    #Create entry box for new scenario location
    dest_label = Label(creator, text = 'New Location:')
    dest_label.grid(row = 2, column = 0, padx = 10, pady = 10, sticky = E + W)

    dest_box = Entry(creator, width = 60)
    dest_box.grid(row = 2, column = 1, columnspan = 2, padx = 10, sticky = W)

    #Create entry box for new scenario name
    name_label = Label(creator, text = 'Scenario Name:')
    name_label.grid(row = 3, column = 0, padx = 10, pady = 10, sticky = E + W)

    name_box = Entry(creator, width = 60)
    name_box.grid(row = 3, column = 1, columnspan = 2, padx = 10, sticky = W)

    def select_base():
        '''
        Selects the base scenario
        '''
        base_dir = askdirectory(initialdir = base_box.get(), title = 'Choose Base Scenario', mustexist = True)
        
        base_box.delete(0, END)
        base_box.insert(0, base_dir)

        if is_child.get(): #If the new scenario is a child of the base scenario, its location is the base scenario
            dest_box.delete(0, END)
            dest_box.insert(0, base_dir)

    def select_dest():
        '''
        Selects the destination of the scenario
        '''
        if is_child.get(): #If the new scenario is a child of the base scenario, its location is the base scenario
            dest_box.delete(0, END)
            dest_box.insert(0, base_box.get())

        else:
            dest_dir = askdirectory(initialdir = base_box.get(), title = 'Choose Scenario Location', mustexist = True)

            dest_box.delete(0, END)
            dest_box.insert(0, dest_dir)

    def create():
        '''
        Creates the new scenario
        '''
        #Make sure that all inputs exist
        if base_box.get() == '':
            showerror('Error', 'Base scenario not specified')
        if dest_box.get() == '':
            showerror('Error', 'New scenario location not specified')
        if name_box.get() == '':
            showerror('Error', 'New scenario name not specified')
        if name_box.get() in ['MODEL', 'FILES']:
            showerror('Error', 'Invalid scenario name')

        old_dir = base_box.get()
        new_dir = os.path.join(dest_box.get(), name_box.get())

        if os.path.isdir(new_dir): #Check if scenario has already been created
            showerror('Error', 'Scenario directory already exists')
        else:
            os.mkdir(new_dir)
            copytree(os.path.join(old_dir, 'FILES'), os.path.join(new_dir, 'FILES'))
            copytree(os.path.join(old_dir, 'MODEL'), os.path.join(new_dir, 'MODEL'))
            copy(os.path.join(old_dir, 'vs_template.ctl'), os.path.join(new_dir, 'vs_template.ctl'))

            with open(os.path.join(new_dir, r'FILES\YEAR.txt'), 'w') as f:
                f.write(year)
                f.close()

            with open(os.path.join(new_dir, 'scenario.txt'), 'w') as f:
                f.write(description)
                f.close()
            
            showinfo('Scenario Creation Complete', 'New scenario {} successfully created'.format(new_dir))
            creator.destroy()

    #Create buttons for actions
    base_selector = Button(creator, text = 'Select Base Scenario', command = select_base)
    base_selector.grid(row = 4, column = 0, padx = 10, pady = 10)

    dest_selector = Button(creator, text = 'Select Scenario Location', command = select_dest)
    dest_selector.grid(row = 4, column = 1, padx = 10, pady = 10)

    main = Button(creator, text = 'Create Scenario', command = create)
    main.grid(row = 4, column = 2, padx = 10, pady = 10)
    
def run_model():
    '''
    Runs the model.
    '''
    global bottom_text
    global scenario_box

    #Read scenario directory
    scenario_dir = scenario_box.get().replace('/', '\\')

    missing_files = check_scenario_directory(scenario_dir)

    if scenario_dir == '':
        showerror('Error', 'Scenario not specified')
    elif len(missing_files) > 0:
        showerror('Error', 'Necessary file(s) missing:\n' + '\n'.join(missing_files))
    else:
        #Define batch file lines
        batch_lines = [r'cd C:\Python27\ArcGIS10.1',
                       r'python C:\CILUM\Scripts\runLand.py "{0}\vs_template.ctl" temp "{0}\MODEL"'.format(scenario_dir), #Run model
                       r'python C:\CILUM\Scripts\MapResults.py', #Place supply and agents into result shapefile
                       r'python C:\CILUM\Scripts\lu2tdm.py', #Convert land use model outputs into travel demand model inputs
                       r'python C:\CILUM\Scripts\WriteSummary.py', #Writes an Excel summary of the results
                       r'python C:\CILUM\Scripts\UpdateEndogVar.py', #Updates endogenous variables
                       r'python C:\CILUM\Scripts\RunCompleted.py'] #Make box pop up that says the run is complete

        #Write batch file
        batch_file = 'C:\CILUM\Scripts\CILUM.bat'
        with open(batch_file, 'w') as batch:
            batch.write('\n'.join(batch_lines))
            batch.close()

        #Execute batch file
        Popen(batch_file)

def run_post_processing():
    '''
    Runs user-specified post-processing
    '''
    ppw = Toplevel() #Post-processing window
    ppw.wm_title('Post-Processing')
    ppw.attributes('-topmost', True)

    #Create entry box for the scenario to use
    scenario_label = Label(ppw, text = 'Scenario:')
    scenario_label.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = E + W)

    scenario_box = Entry(ppw, width = 60) #NOTE: This is different than the main scenario_box.
    scenario_box.grid(row = 0, column = 1, padx = 10, sticky = W)

    instructions = Label(ppw, text = 'Select post-processing scripts to run:')
    instructions.grid(row = 1, column = 0, columnspan = 2, pady = 10)

    #List of checkboxes to decide which post-processing scripts to run
    run_MapResults = BooleanVar()
    MapResults = Checkbutton(ppw, text = 'Map Results', var = run_MapResults)
    MapResults.grid(row = 2, column = 0, columnspan = 2, sticky = W)

    run_lu2tdm = BooleanVar()
    lu2tdm = Checkbutton(ppw, text = 'Create Travel Demand Model Inputs', var = run_lu2tdm)
    lu2tdm.grid(row = 3, column = 0, columnspan = 2, sticky = W)

    run_update_endogvar = BooleanVar()
    update_endogvar = Checkbutton(ppw, text = 'Update Endogenous Variables', var = run_update_endogvar)
    update_endogvar.grid(row = 4, column = 0, columnspan = 2, sticky = W)

    run_WriteSummary = BooleanVar()
    WriteSummary = Checkbutton(ppw, text = 'Write Summary', var = run_WriteSummary)
    WriteSummary.grid(row = 5, column = 0, columnspan = 2, sticky = W)

    def choose_scenario():
        '''
        Selcts a scenario to run post-processing on
        '''
        #Ask the user for the scenario directory
        scenario_dir = askdirectory(initialdir = os.getcwd(),
                                    title = 'Choose Scenario Directory',
                                    mustexist = True)

        scenario_box.delete(0, END)
        scenario_box.insert(0, scenario_dir)

        os.environ['CILUM'] = scenario_dir

    def run_scripts():
        '''
        Runs the selected post-processing scripts
        '''
        scenario_dir = scenario_box.get()
        
        if scenario_dir == '': #Assert that a scenario must be selected
            showerror('Error', 'Scenario not indicated')
        else:
            os.environ['CILUM'] = scenario_dir

            #Check which scripts are selected and run the ones that are
            if run_MapResults.get():
                os.system(r'C:\CILUM\Scripts\MapResults.py')
            if run_lu2tdm.get():
                os.system(r'C:\CILUM\Scripts\lu2tdm.py')
            if run_update_endogvar.get():
                os.system(r'C:\CILUM\Scripts\UpdateEndogVar.py')
            if run_WriteSummary.get():
                os.system(r'C:\CILUM\Scripts\WriteSummary.py')

            showinfo('Post-Processing Complete', 'Post-processing for scenario {} successfully completed'.format(scenario_dir))
            ppw.destroy()

    #Create buttons for actions
    choose_button = Button(ppw, text = 'Select Scenario', command = choose_scenario)
    choose_button.grid(row = 6, column = 0, padx = 10, pady = 10)

    run_button = Button(ppw, text = 'Run Post-Processing', command = run_scripts)
    run_button.grid(row = 6, column = 1, padx = 10, pady = 10)

###############################################################################################################################

#Create scenario selection button
selector = Button(master, text = 'Select Scenario', command = select_scenario)
selector.grid(row = 7, column = 0, pady = 10)

#Create scenario creation button
creator = Button(master, text = 'Create Scenario', command = create_scenario)
creator.grid(row = 8, column = 0, pady = 10)

#Create full model running button
run = Button(master, text = 'Run Model', command = run_model)
run.grid(row = 7, column = 1)

#Create post-processing running button
post = Button(master, text = 'Run Post-Processing', command = run_post_processing)
post.grid(row = 8, column = 1)

mainloop()

