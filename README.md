# Cell-DEVS model of People Evacuating a Room

## Compiling the model
Open a terminal in the main directory with the makefile and enter the command, "make simulator". This will create a bin and a build folder.

## Running the model
Open a terminal in the bin folder and enter commands like this, "./MAIN ../Scenario1.json 10". This command will run the model with scenario 1 for 10 time steps. You can select a different scenario and run it for different amounts of time, though the longest scenario, which is 3, only runs for about 21 time steps before it finishes. To read the log result of the simulation enter the folder "simulation_results" and select the .csv file named "evac". The most recent simulation log is always called "evac.csv".
