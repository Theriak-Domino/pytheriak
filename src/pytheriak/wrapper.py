import subprocess
import re
import numpy as np
from pathlib import Path


class TherCaller():
    @staticmethod
    def output_block_finder(theriak_output: list, start_key: str, end_key: str, end_with_subtitle: bool = False):
        """ Used in TherCaller.call_theriak()
        Scans the "theriak_output" (in-lines) for a block of interest starting with "start_key" and ending with "end_key" (not included)
        Start and end keys can be a subtitle in the theriak output, demarked with:
         -------------
        "a subtitle":
         -------------
        Or alternatively a line below a subtitle demarked block.

        Stripping the processed output and saving the residual, results in a significant performance increase (from micro- to nano-seconds),
        from the second scan on. Testet with %%timeit on 27.12.2022, in comparison to only extracting a block of interest of n lines after a key.

        Args:
            theriak_output (list): theriak output with lines as list entries.
            start_key (str): String marking the start of an output block of interest.
            end_key (str): String marking the end of an output block of interest.
            end_with_subtitle (bool, optional): If block of interest end with a subtitle, idx of "end_key" -3 is taken as block end.
                                                 (subtitle always preceded by two linebreaks and "----")

        Returns:
            block (list): The block of interest
            residual_output (list): The residual theriak_output, starting with the "end_key"
        """
        start_idx = theriak_output.index(start_key)
        end_idx = theriak_output.index(end_key)

        if end_with_subtitle:
            block = theriak_output[start_idx:end_idx-3]
        else:
            block = theriak_output[start_idx:end_idx]

        residual_output = theriak_output[end_idx:]
        return block, residual_output

    @staticmethod
    def extract_solution_subblocks(block_phases: list, verbose: bool = True):
        """Used in Rock.add_minerals()

        Args:
            block_phases (list): block_phases from blocks (splitted theriak output)
            verbose (bool): turn on/off verbose mode, if False no Warnings will be printed, if activities do not match.

        Returns:
            dict: Dict with phase name (only solution phases) as keys, and output-lines of that corresponding phase in subblocks (list)
        """
        block_solution_phases = {}
        solution_phase_list = []

        # solution phases are marked bijectively by "  0" followed by the solution number in this block
        start_key = "   0"
        start_indices = [idx for idx, line in enumerate(block_phases) if line.startswith(start_key)]
        # shift start_idx and append last line as last end_idx
        end_indices = start_indices[1:]
        end_indices.append(len(block_phases))

        for start_idx, end_idx in zip(start_indices, end_indices):
            solution_subblock = block_phases[start_idx:end_idx]

            # if minimisation failed, subblock layout changes!
            # check for "activity test", if present remove additional lines.
            if any("activity test:" in line for line in solution_subblock):
                cut_idx = solution_subblock.index(" ")
                solution_subblock = solution_subblock[:cut_idx]
                # replace the "**" marks with "  ", so that the solution subblock can be treated like one of a succesful minimisation afterwards.
                solution_subblock = [string.replace("**", "  ") for string in solution_subblock]
                if verbose:
                    print("WARNING: Minimisation might have failed. End-member activities of solutions might be wrong.")

            # filter out lines containing info about site occupancy or element fractions (e.g. XMg, Al(pfu))
            # the lines containing end-member fractions and activities are the only ones ending with a double-space "  "
            # this is represented with the regex pattern: "Any digit""Space""Space""End of string" = "\d\s\s$"
            solution_subblock = [line for line in solution_subblock if len(re.findall(pattern=r"\d\s\s$", string=line)) == 1]

            # extract solution name from first line / 3rd entry of the solution subblock
            solution_name = solution_subblock[0].split()[2]
            solution_phase_list.append(solution_name)
            block_solution_phases[solution_name] = solution_subblock

        return block_solution_phases

    def __init__(self, programs_dir: str, database: str, theriak_version: str, verbose: bool = True):
        """Creates a TherCaller intance.
        For calling theriak, the theriak.ini file must be copied from the programs folder to the working directory.

        Args:
            programs_dir (str): Path to the Programs directory of TheriakDomino
            database (str): Name of the database
            theriak_version (str): version of theriak, lookup in programs folder.

        """

        self.theriak_exe = Path(programs_dir) / "theriak"
        self.database = database

        self.theriak_version = theriak_version

        self.verbose_mode = verbose

    def call_theriak(self, pressure: int, temperature: int, bulk: str):
        """Execute theriak.exe and returns the OUT as string.

        Args:
            pressure (int): Pressure in [bar].
            temperature (int): Temperature in [deg C]
            bulk (str): Bulk composition in the THERIN format. Elements in capital letters (e.g. SI, AL) and moles in brackets.

        Returns:
            str: Theriak output.
        """
        self.pressure = pressure
        self.temperature = temperature

        # create theriak input for subprocess.run(), "\n" is interpreted as "enter"
        self.theriak_input = self.database + "\n" + "no\n"

        # write THERIN
        self.therin_PT = "    " + str(temperature) + "    " + str(pressure)
        self.therin_bulk = "1   " + bulk + "    *"

        with open("THERIN", "w") as therin_file:
            therin_file.write(self.therin_PT)
            therin_file.write("\n")
            therin_file.write(self.therin_bulk)

        # call theriak
        out = subprocess.run([self.theriak_exe],
                             input=self.theriak_input,
                             encoding="utf-8",
                             capture_output=True)

        theriak_output = out.stdout

        return theriak_output

    def check_minimisation(self, theriak_output: str):
        """Checks for theriak calls with failed minimisation.
        If and only if a minimisation fails, this will be marked in the theriak output by "**" before the activities of EM in solutions.
        Additionally below the activities block the "** activity test:" is listed for the failed solution phases.

        This function checks for a succesful minimisation.
        For debugginng assistance it prints the THERIN, where the minimisation failed.

        Args:
            theriak_output (str): The output of a theriak call, equiv to the OUT file.

        Returns:
            bool: State, if theriak call gave resultet in a succesful minimisation.
        """
        substring_if_minimisation_fail = "activity test"

        if substring_if_minimisation_fail in theriak_output:
            if self.verbose_mode is True:
                print("WARNING: Minimisation possibly failed. For the following THERIN:")
                print(self.therin_PT)
                print(self.therin_bulk)

            return False

        elif substring_if_minimisation_fail not in theriak_output:
            return True

    def read_theriak(self, theriak_output: str):
        """Reads theriak output
        Information of interest is extracted as blocks, which then can be further processed by other methods.

        Args:
            theriak_output (str): Theriak out from TherCaller.call_theriak

        Returns:
            dict: blocks, a dict containing the extracted block of interest from the theriak output
            list: element_list, element-idx list globally valid for all compositional data
            bool: output_line_overflow
            bool: fluids_stable
        """
        theriak_output = theriak_output.splitlines()

        # extract blocks of interest from theriak output
        # 1) bulk rock composition
        start_key_bulk = " composition:        N           N             mol%"
        end_key_bulk = " considered phases:"
        block_bulk, residual_output = TherCaller.output_block_finder(theriak_output, start_key_bulk, end_key_bulk, True)

        # 2) G_system
        start_key_Gsys = " equilibrium assemblage:"
        end_key_Gsys = "         phase                   N         mol%                                   x              x         activity       act.(x)"
        block_Gsys, residual_output = TherCaller.output_block_finder(residual_output, start_key_Gsys, end_key_Gsys, False)

        # 3) equilibrium assemblage, stable phases
        start_key_phases = "         phase                   N         mol%                                   x              x         activity       act.(x)"
        end_key_phases = " volumes and densities of stable phases:"
        block_phases, residual_output = TherCaller.output_block_finder(residual_output, start_key_phases, end_key_phases, True)

        # 4) volume and densities of stable phases
        start_key_volume = " volumes and densities of stable phases:"
        # choose end_key_volume, so that always present independent if fluids are stable or not (this will affect the text of the theriak output)
        end_key_volume = " compositions of stable phases [ mol% ]:"
        # don't pass the residual output here, because the fluid block comes before end_key_volume in the theriak output
        block_volume, residual_output_NOT_TO_USE = TherCaller.output_block_finder(residual_output, start_key_volume, end_key_volume, True)

        # 5) gases and fluids
        start_key_fluid = "  gases and fluids       N       volume/mol  volume[ccm]               wt/mol       wt [g]              density [g/ccm]"
        end_key_fluid = " H2O content of stable phases:"
        try:
            block_fluid, residual_output = TherCaller.output_block_finder(residual_output, start_key_fluid, end_key_fluid, True)
            fluids_stable = True
        # catch the ValueError, when no stable fluid phases predicted the block_fluid wont show in theriak output.
        except ValueError:
            if self.verbose_mode:
                print("WARNING: No fluid phase stable at given P-T-X. Water-sat. conditions not fulfilled.")
            # set a state, to disable adding fluids to the rock later on. Set an empty list as placeholder instead of the fluid block.
            fluids_stable = False
            block_fluid = []

        # 6) phase compositions; elements in moles in stable phases + in total system (=bulk)
        start_key_elements = " elements in stable phases:"
        end_key_elements = " elements per formula unit:"
        block_elements, residual_output = TherCaller.output_block_finder(residual_output, start_key_elements, end_key_elements, False)

        # 7) phase composition: elements per formula unit
        start_key_composition = " elements per formula unit:"
        end_key_composition = " activities of all phases:"
        block_composition, residual_output = TherCaller.output_block_finder(residual_output, start_key_composition, end_key_composition, True)

        # 8) activities of all phases: delta_G above stable plain
        start_key_deltaG = " activities of all phases:"
        end_key_deltaG = " chemical potentials of components:"
        block_deltaG, residual_output = TherCaller.output_block_finder(residual_output, start_key_deltaG, end_key_deltaG, True)

        # 9) chemical potential of components
        # ## future addition.

        # 10) extract subblocks from block_phases for end-member properties of solution phases
        solution_subblocks = TherCaller.extract_solution_subblocks(block_phases=block_phases, verbose=self.verbose_mode)

        blocks = {"block_bulk": block_bulk,
                  "block_Gsys": block_Gsys,
                  "block_phases": block_phases,
                  "block_solutions": solution_subblocks,
                  "block_volume": block_volume,
                  "block_fluid": block_fluid,
                  "block_elements": block_elements,
                  "block_composition": block_composition,
                  "block_deltaG": block_deltaG}

        # check for line overflow: ("elements in bulk" > 10) in "elements in stable phases:"
        # if last line in compostion block starts with an indendation, then there is line overflow in the output
        output_line_overflow = False
        if block_composition[-1].startswith("                    "):
            # pass this as a state attribute to the rock object
            output_line_overflow = True

        # create element list, idx of list are globally value for all compositions (bulk, minerals, fluids) in theriak output
        element_list = block_elements[3].split()
        # catch a second line of elements in output
        if output_line_overflow:
            additional_elements = block_elements[4].split()
            element_list += additional_elements
        # drop last element "E" (only for testing in theriak)
        element_list = element_list[:-1]

        return blocks, element_list, output_line_overflow, fluids_stable

    def create_rock(self, blocks: dict, output_line_overflow: bool, fluids_stable: bool):
        rock = Rock(pressure=self.pressure, temperature=self.temperature)
        rock.add_therin_to_reproduce(PT=self.therin_PT, bulk=self.therin_bulk)
        rock.add_bulk_rock_composition(block_bulk=blocks["block_bulk"])
        rock.add_g_system(block_Gsys=blocks["block_Gsys"])
        rock.add_bulk_density(block_volume=blocks["block_volume"])
        rock.add_minerals(block_volume=blocks["block_volume"], block_solutions=blocks["block_solutions"], block_composition=blocks["block_composition"],
                          block_elements=blocks["block_elements"], output_line_overflow=output_line_overflow, verbose=self.verbose_mode)
        if fluids_stable:
            rock.add_fluids(block_fluid=blocks["block_fluid"], block_solutions=blocks["block_solutions"], block_composition=blocks["block_composition"],
                            block_elements=blocks["block_elements"], output_line_overflow=output_line_overflow)
        rock.add_deltaG(block_deltaG=blocks["block_deltaG"])
        rock.add_g_system_per_mol()

        return rock

    def minimisation(self, pressure: int, temperature: int, bulk: str, return_failed_minimisation: bool = False):
        """Perform a minimisation of the Gibbs free energy of the system at given P-T-X conditions.
        Encapsulates: call_theriak --> check_minimisation --> read_theriak --> create_rock

        Args:
            pressure (int): Pressure in bar
            temperature (int): Temperature in °C
            bulk (str): Bulk rock composition in the Theriak-Domino format. Element in caps, followed by moles/mol percent in brackets: "E(10.3)".
            return_failed_minimisation (bool, optional): Whether a possibly failed minimisation is returned or not. Defaults to False.

        Returns:
            rock(pytheriak.Rock): A pytheriak.Rock object encapsulating the results of the minimisation.
            element_list (list): element_list, element-idx list globally valid for all compositional data.
        """
        # A composition of call_theriak --> check_minimisation --> read_theriak; returning a rock, ele_list
        theriak_output = TherCaller.call_theriak(self, pressure=pressure, temperature=temperature, bulk=bulk)
        minimisation_state = TherCaller.check_minimisation(self, theriak_output=theriak_output)
        if return_failed_minimisation:
            # overwrite minimisation_state
            minimisation_state = True

        if minimisation_state:
            blocks, element_list, output_line_overflow, fluids_stable = TherCaller.read_theriak(self, theriak_output=theriak_output)
            rock = TherCaller.create_rock(self, blocks=blocks, output_line_overflow=output_line_overflow, fluids_stable=fluids_stable)

            return rock, element_list

        else:
            # for a failed minimisation return the raw theriak output. And an empty list instead of the element_list
            return theriak_output, []

    def check_for_corrupted_bulk(self, bulk: str):
        """Checks if bulk has an non-zero amount of all elemetns in the system.
        If this is not the case, theriak will remove the element from the bulk. Resulting in an unwanted reduction of the systems components.
        In this case the element_idx list would no longer be globally valid!

        Args:
            bulk (str): A bulk in the THERIN format

        Returns:
            bool: TRUE, if bulk is valid, FALSE for corrupted bulk.
        """
        matches = re.findall(pattern=r"\(0\)", string=bulk)
        matches += (re.findall(pattern=r"0.0+\)", string=bulk))

        if len(matches) == 0:
            return True
        else:
            if self.verbose_mode:
                print("WARNING: Corrupted bulk, THERIN bulk (str) contains an element which is 0.")
            return False


class Rock:
    """_summary_
    A "Rock" is defined by 3 parameters: (P, T, bulk composition).
    Rock()-instances are created by TherCaller.call_theriak() as the result of a Gibb's Energy minimisation done by theriak.

    Returns:
        _type_: _description_
    """
    @staticmethod
    def get_mineral_list(block_volume: list):
        """Used in add_minerals()
        Reads block_volume and extract names of all stable phases in output
        IMPORTANT: names are temporary names, dependent of database and solid solution composition in specific output!

        Args:
            block_volume (list): block_volume from blocks (splited theriak output --> generated by TherCaller.call_theriak())

        Returns:
            list: list of temp_names
        """
        # get start and end idx of lines containing mineral names
        # start always 5th line
        start_idx = 5
        # end "total of solids..." - 1
        str.startswith
        end_entry = [i for i in block_volume if i.startswith("  total of solids")][0]
        end_idx = block_volume.index(end_entry) - 1
        # get mineral names, always the first entry of each relevant line in block
        temp_name_list = [temp_name.split()[0] for temp_name in block_volume[start_idx:end_idx]]
        # temp_name, because this name is dependent on database and solid solution composition
        return temp_name_list

    @staticmethod
    def get_fluid_list(block_fluid: list):
        """Used in add_fluids()
        Reads block_fluid and extract names of all stable fluid phases in output

        Args:
            block_fluid (list): block_fluid from blocks (splitted theriak output --> generated by TherCaller.call_theriak())

        Returns:
            list: list of fluid phase names
        """
        # start and end idx: end is depending on number of phases, always up to the last entry in block
        start_idx = 2
        # get mineral names, always the first entry of each relevant line in block
        fluid_name_list = [temp_name.split()[0] for temp_name in block_fluid[start_idx:]]
        # for fluids temp name is kept.
        return fluid_name_list

    def __init__(self, pressure: int, temperature: int):
        """Creates a Rock() instance.
        pressure and temperature are assigned during initialisation.
        They can be taken directly from the TherCaller.call_theriak() input
        All other Rock().attributes are populated by seperate methods further on.

        Args:
            pressure (int): Pressure in bar
            temperature (int): Temperature in degree Celsius
        """
        self.mineral_assemblage = []
        self.fluid_assemblage = []
        self.mineral_delta_G = None
        self.g_system = None
        self.pressure = pressure
        self.temperature = temperature
        self.bulk_composition_moles = None
        self.bulk_composition_mol_percent = None

    def __dir__(self):
        """Overwrite dir() to only return objects attriubutes holding thermodynamic state properties.

        Returns:
            (list): List of Rock-attrs holding state properties of minimised system.
        """
        return ["mineral_assemblage",
                "fluid_assemblage",
                "mineral_delta_G",
                "g_system",
                "g_system_per_mol_of_input",
                "pressure",
                "temperature",
                "bulk_composition_moles",
                "bulk_composition_mol_percent",
                "therin_PT",
                "therin_bulk"]

    def add_therin_to_reproduce(self, PT: str, bulk: str):
        """Passes THERIN strings from the TherCaller.call-theriak() to the Rock object

        Args:
            PT (str): THERIN first line
            bulk (str): THERIN second line
        """
        self.therin_PT = PT
        self.therin_bulk = bulk

    def add_bulk_rock_composition(self, block_bulk: list):
        # extract relevant lines
        # first 3 are title,
        # ending blanks lines and the "E" composition were removed by the TherCaller.output_block_finder(),since: end_with_subtitle=True.
        block_bulk = block_bulk[3:]
        # extract 2nd entry, n moles in bulk
        bulk_mol_list = [n.split()[2] for n in block_bulk]
        # convert to str --> float
        bulk_mol_list = [float(n) for n in bulk_mol_list]
        # extract 4th entry, mol% in bulk
        bulk_mol_percent_list = [n.split()[4] for n in block_bulk]
        # convert to str --> float
        bulk_mol_percent_list = [float(n) for n in bulk_mol_percent_list]

        self.bulk_composition_moles = bulk_mol_list
        self.bulk_composition_mol_percent = bulk_mol_percent_list

    def add_g_system(self, block_Gsys: list):
        """Reads G(System) from respective theriak output block and saves it to self.g_system

        Args:
            block_Gsys (list): block_Gsys from blocks (splitted theriak output --> generated by TherCaller.call_theriak())
        """
        # get 8th line from block_Gsys output block, contains G(System)
        g_system_line = block_Gsys[7]
        # get the 5th entry, G(System) value
        g_system = g_system_line.split()[5]
        # transfrom str --> float
        g_system = float(g_system)

        self.g_system = g_system

    def add_g_system_per_mol(self):
        composition_list = self.bulk_composition_moles
        sum_mol_input_elements = np.sum(composition_list)
        # divide the g_system by the molar sum of all inputed elements;
        # doing this makes the g_sys independent from the absolute input used (depends on personal format choice)
        self.g_system_per_mol_of_input = self.g_system / sum_mol_input_elements

    def add_bulk_density(self, block_volume: list):
        """Reads the bulk density of solid phases form te respective theriak output block.
        Attention: Depending on the activated melt model, melts can be included in solid phases, therefore affecting also bulk density.

        Args:
            block_volume (list): block_volume from blocks (splitted theriak output --> generated by TherCaller.call_theriak())
        """
        bulk_properties_line = [line for line in block_volume if line.startswith("  total of solids")][0]
        bulk_density = bulk_properties_line.split()[-1]
        # transform str --> float
        bulk_density = float(bulk_density)

        self.bulk_density = bulk_density

    def add_minerals(self, block_volume: list, block_solutions: list, block_composition: list,
                     block_elements: list, output_line_overflow: bool, verbose: bool = True):
        temp_name_list = Rock.get_mineral_list(block_volume=block_volume)

        for temp_name in temp_name_list:
            mineral = Mineral(phase_name=temp_name)
            mineral.add_phase_properties(block_volume=block_volume, temp_name=temp_name)
            mineral.add_composition_apfu(block_composition=block_composition,
                                         temp_name=temp_name,
                                         output_line_overflow=output_line_overflow)
            mineral.add_composition_moles(block_elements=block_elements,
                                          temp_name=temp_name,
                                          output_line_overflow=output_line_overflow)

            if temp_name in block_solutions.keys():
                mineral.add_endmember_properties(solution_phase_subblock=block_solutions[temp_name])

            self.mineral_assemblage.append(mineral)

    def add_fluids(self, block_fluid: list, block_solutions: list, block_composition: list,
                   block_elements: list, output_line_overflow: bool):
        fluid_name_list = Rock.get_fluid_list(block_fluid=block_fluid)

        for fluid_name in fluid_name_list:
            fluid = Fluid(phase_name=fluid_name)
            fluid.add_phase_properties(block_fluid=block_fluid, temp_name=fluid_name)
            fluid.add_composition_apfu(block_composition=block_composition,
                                       temp_name=fluid_name,
                                       output_line_overflow=output_line_overflow)
            fluid.add_composition_moles(block_elements=block_elements,
                                        temp_name=fluid_name,
                                        output_line_overflow=output_line_overflow)

            if fluid_name in block_solutions.keys():
                fluid.add_endmember_properties(solution_phase_subblock=block_solutions[fluid_name])

            self.fluid_assemblage.append(fluid)

    def add_deltaG(self, block_deltaG: list):
        # remove title
        block_deltaG = block_deltaG[5:]
        # search idx of delimiter stable / metastable phases
        delimiter = block_deltaG.index("--------------------------------------------------------------------")
        block_deltaG = block_deltaG[delimiter+1:]
        metastable_list = [i.split() for i in block_deltaG if (i.startswith(" S") or i.startswith(" P"))]
        # look for the first occurence of "0.00000E+00"
        idx_of_firstZEROS = [i.index("0.00000E+00") for i in metastable_list]
        metastable_list_names = [i[2] for i in metastable_list]
        metastable_list_deltaG = [i[idx + 1] for i, idx in zip(metastable_list, idx_of_firstZEROS)]
        metastable_list_deltaG = [float(i) for i in metastable_list_deltaG]

        mineral_delta_G = dict(zip(metastable_list_names, metastable_list_deltaG))
        self.mineral_delta_G = mineral_delta_G


class Phase:
    def __init__(self, phase_name) -> None:
        self.name = phase_name
        # A Phase is a priori a pure phase, only add_endmember_properties() updates this state attribute to True for solutions.
        self.solution_phase: bool = False

    def add_composition_apfu(self, block_composition: list, temp_name: str, output_line_overflow: bool):
        """_summary_

        Args:
            block_composition (list): block_composition from blocks (splited theriak output)
            temp_name (str): _description_
            element_list (list): _description_
            output_line_overflow (bool): From TherCaller.
        """
        # get list entry (str of an output line), that startswith temp_name
        phase_composition_line = [i for i in block_composition if i.startswith(" " + temp_name)]
        phase_composition = phase_composition_line[0].split()
        if output_line_overflow:
            idx = block_composition.index(phase_composition_line[0])
            additional_line = block_composition[idx + 1]

            phase_composition += additional_line.split()

        # drop first (Phase name) and last ("E"-composition) entry
        phase_composition = phase_composition[1:-1]
        # convert composition to float
        phase_composition = [float(x) for x in phase_composition]

        self.composition_apfu = phase_composition
        # important to also save Oxygen, to calculate Fe3

    def add_composition_moles(self, block_elements: list, temp_name: str, output_line_overflow: bool):
        # get list entry (str of an output line), that startswith temp_name
        phase_composition_line = [i for i in block_elements if i.startswith(" " + temp_name)]
        phase_composition = phase_composition_line[0].split()
        if output_line_overflow:
            idx = block_elements.index(phase_composition_line[0])
            additional_line = block_elements[idx + 1]

            phase_composition += additional_line.split()

        # drop first (Phase name) and last ("E"-composition) entry
        phase_composition = phase_composition[1:-1]
        # convert composition to float
        phase_composition = [float(x) for x in phase_composition]

        self.composition_moles = phase_composition

    def add_endmember_properties(self, solution_phase_subblock: list):
        # update state-attribute to mark phase as solution
        self.solution_phase = True
        # read the solution phase subblock
        lines = [line.split() for line in solution_phase_subblock]
        # get rid off additional entries in the first line (pre-fix, phase, N, mol%)
        first_line = lines[0][5:]
        lines[0] = first_line

        endmember_activities = {}
        endmember_fractions = {}

        for line in lines:
            endmember_name = line[0]
            activity = float(line[-2])
            fraction = float(line[-3])

            endmember_activities[endmember_name] = activity
            endmember_fractions[endmember_name] = fraction

        self.endmember_activities = endmember_activities
        self.endmember_fractions = endmember_fractions


class Mineral(Phase):
    def add_phase_properties(self, block_volume: list, temp_name: str):
        # get list entry (str of an output line), that startswith temp_name
        phase_properties_line = [i for i in block_volume if i.startswith("  " + temp_name)]
        phase_properties_line = phase_properties_line[0].split()
        # extract the physical properties by indexing
        self.n = float(phase_properties_line[1])
        self.vol = float(phase_properties_line[3])
        self.vol_percent = float(phase_properties_line[4])
        self.density = float(phase_properties_line[-1])


class Fluid(Phase):
    def add_phase_properties(self, block_fluid: list, temp_name: str):
        # get list entry (str of an output line), that startswith temp_name
        phase_properties_line = [i for i in block_fluid if i.startswith("  " + temp_name)]
        phase_properties_line = phase_properties_line[0].split()
        # extract the physical properties by indexing
        self.n = float(phase_properties_line[1])
        self.vol = float(phase_properties_line[3])
        self.density = float(phase_properties_line[-1])
