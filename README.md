#Simulation in Logistics and Production of perishable products
This simulation model was developed during writing a term paper 
at Julius-Maximilians-Universität of Würzburg in the master program Information Systems. 
It was developed harnessing the `Python` framework `SimPy` for discrete-event simulation.
The following is a step-by-step guide to running a simulation on your own.

After you installed the ``requirements.py`` please follow the following instruction. 

To initiate the simulation parameters, run the simulation and prepare data for analysis you need the following files:
- `simulation.py`
- `annual_demand_generator.py`
- `analysis.py`

### Initate the Simulation

1. First you have to decide on the subsequent parameters for creating the annual demand history:
   - Duration of your simulation (`simulation_duration`)
   - Remaining shelf life of your product at the entity `Wholesaler` (`w`) <br> &rarr;  See first part of equation 2 in term paper (without D_w) 
   - Average demand per time step for normal distribution (`mu`) 
   - Variance for normal distribution (`sigma`) 
2. Open the file `simulation.py` to set up the parameters for `Wholesaler` etc.<br>
   - Set up the parameters of the function `simulate` to your desired values. 
   <br> Note, that for parameters like e.g. `reorder_point` you should use the according equation (see term paper).
   <br> &rarr; Initially the function `simulate` is set up for the **basic scenario** (*Szenario I*; no disruption).
   - In case you want to implement a disruption for entity `manufacturer` follow the structure of the `dict` `mr_attributes`.
   - Choose how many times you want to run the simulation, in order to reduce output randomness.

### Start the Simulation

Once you are done setting up the parameters, start the simulation by running `simulation.py`. <br>
The end of the simulation will be indicated in the console by displaying the needed time to finish the program. 

### Data Preparation for Analysis

Once your simulation run finished successfully you can now perform the data preparation by calculating KPIs <br>
like the mean, standard deviation, confidence interval etc. <br>
The confidence interval is set up as standard for 95%. You can adjust it by adjusting the `var_ci_coefficient` accordingly.