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
    def check_for_corrupted_bulk(bulk: str):
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
            print("WARNING: Corrupted bulk, THERIN bulk (str) contains an element which is 0.")
            return False

    def __init__(self, programs_dir: str, database: str, theriak_version: str, cwd: str):
        """Creates a TherCaller intance.
        For calling theriak, the theriak.ini file must be copied from the programs folder to the working directory.

        Args:
            programs_dir (str): Path to the Programs directory of TheriakDomino
            database (str): Name of the database
            theriak_version (str): version of theriak, lookup in programs folder.

        """
        self.cwd = Path(cwd)

        self.theriak_exe = Path(programs_dir) / "theriak"
        self.database = database

        self.theriak_version = theriak_version

        # create theriak input for subprocess.run(), "\n" is interpreted as "enter"
        self.theriak_input = self.database + "\n" + "no\n"

    def call_theriak(self, pressure: int, temperature: int, bulk: str):
        # write THERIN
        self.therin_PT = "    " + str(temperature) + "    " + str(pressure)
        self.therin_bulk = "1   " + bulk + "    *"

        with open(self.cwd / "THERIN", "w") as therin_file:
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
        If and only if a minimisation fails, this will be marked in the theriak output by "**" before the activities of Em in solutions.
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
            print("WARNING: Detected a failed minimisation. For the following THERIN:")
            print(self.therin_PT)
            print(self.therin_bulk)

            return False

        elif substring_if_minimisation_fail not in theriak_output:
            return True

    def read_theriak(self, theriak_output: str, pressure: int, temperature: int):
        theriak_output = theriak_output.splitlines()

        """
        extract blocks of interest from theriak output
        """
        # 1) bulk rock composition
        start_key_bulk = " composition:        N           N             mol%"
        end_key_bulk = " considered phases:"
        block_bulk, residual_output = TherCaller.output_block_finder(theriak_output, start_key_bulk, end_key_bulk, True)

        # 2) G_system
        start_key_Gsys = " equilibrium assemblage:"
        end_key_Gsys = "         phase                   N         mol%                                   x              x         activity       act.(x)"
        block_Gsys, residual_output = TherCaller.output_block_finder(residual_output, start_key_Gsys, end_key_Gsys, False)

        # 3) volume and densities of stable phases
        start_key_volume = " volumes and densities of stable phases:"
        # choose end_key_volume, so that always present independent if fluids are stable or not (this will affect the text of the theriak output)
        end_key_volume = " compositions of stable phases [ mol% ]:"
        # don't pass the residual output here, because the fluid block comes before end_key_volume in the theriak output
        block_volume, residual_output_NOT_TO_USE = TherCaller.output_block_finder(residual_output, start_key_volume, end_key_volume, True)

        # 4) gases and fluids
        start_key_fluid = "  gases and fluids       N       volume/mol  volume[ccm]               wt/mol       wt [g]              density [g/ccm]"
        end_key_fluid = " H2O content of stable phases:"
        try:
            block_fluid, residual_output = TherCaller.output_block_finder(residual_output, start_key_fluid, end_key_fluid, True)
            fluids_stable = True
        # ctach the ValueError, when no stable fluid phases predicted the block_fluid wont show in theriak output.
        except ValueError:
            print("WARNING: No fluid phase stable at given P-T-X. Water-sat. conditions not fulfilled.")
            # set a state, to disabkle adding fluids to the rock later on. Set an empty list as placeholder instead of the fluid block.
            fluids_stable = False
            block_fluid = []

        # 5) elements in system; all elements in system/phases and their idx for phase / bulk composition
        start_key_elements = " elements in stable phases:"
        end_key_elements = " elements per formula unit:"
        block_elements, residual_output = TherCaller.output_block_finder(residual_output, start_key_elements, end_key_elements, False)

        # 6) phase composition: elements per formula unit
        start_key_composition = " elements per formula unit:"
        end_key_composition = " activities of all phases:"
        block_composition, residual_output = TherCaller.output_block_finder(residual_output, start_key_composition, end_key_composition, True)

        # 7) activities of all phases: delta_G above stable plain
        start_key_deltaG = " activities of all phases:"
        end_key_deltaG = " chemical potentials of components:"
        block_deltaG, residual_output = TherCaller.output_block_finder(residual_output, start_key_deltaG, end_key_deltaG, True)

        # 8) chemical potential of components
        # ## OPTIONAL, to be discussed if necessary.

        blocks = [block_bulk, block_Gsys, block_volume, block_fluid, block_elements, block_composition, block_deltaG]

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

        """
        Create Rock
        """
        rock = Rock(pressure=pressure, temperature=temperature)
        rock.add_therin_to_reproduce(PT=self.therin_PT, bulk=self.therin_bulk)
        rock.add_bulk_rock_composition(block_bulk=blocks[0])
        rock.add_g_system(block_Gsys=blocks[1])
        rock.add_minerals(block_volume=blocks[2], block_composition=blocks[5], element_list=element_list, output_line_overflow=output_line_overflow)
        if fluids_stable:
            rock.add_fluids(block_fluid=blocks[3], block_composition=blocks[5], element_list=element_list, output_line_overflow=output_line_overflow)
        rock.add_deltaG(block_deltaG=blocks[6])
        rock.add_g_system_per_mol()
        return rock, theriak_output, blocks, element_list


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
        self.bulk_composition_n = None
        self.bulk_composition_mol_percent = None

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

        self.bulk_composition_n = bulk_mol_list
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
        composition_list = self.bulk_composition_n
        sum_mol_input_elements = np.sum(composition_list)
        # divide the g_system by the molar sum of all inputed elements;
        # doing this makes the g_sys independent from the absolute input used (depends on personal format choice)
        self.g_system_per_mol_of_input = self.g_system / sum_mol_input_elements

    def add_minerals(self, block_volume: list, block_composition: list, element_list: list, output_line_overflow: bool):
        temp_name_list = Rock.get_mineral_list(block_volume=block_volume)

        for temp_name in temp_name_list:
            mineral = Mineral(phase_name=temp_name)
            mineral.add_phase_properties(block_volume=block_volume, temp_name=temp_name)
            mineral.add_composition(block_composition=block_composition,
                                    temp_name=temp_name,
                                    element_list=element_list,
                                    output_line_overflow=output_line_overflow)

            self.mineral_assemblage.append(mineral)

    def add_fluids(self, block_fluid: list, block_composition: list, element_list: list, output_line_overflow: bool):
        fluid_name_list = Rock.get_fluid_list(block_fluid=block_fluid)

        for fluid_name in fluid_name_list:
            fluid = Fluid(phase_name=fluid_name)
            fluid.add_phase_properties(block_fluid=block_fluid, temp_name=fluid_name)
            fluid.add_composition(block_composition=block_composition,
                                  temp_name=fluid_name, element_list=element_list,
                                  output_line_overflow=output_line_overflow)

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
        # try:
        #     metastable_list_deltaG = [i[1].split()[0] for i in metastable_list]
        #     print("!!!! METASTABLE LIST correct !!!")
        #     print(metastable_list)
        # except IndexError:
        #     print("!!!! METASTABLE LIST FAIL !!!")
        #     print(metastable_list)
        #     print("!!!! block_deltaG !!!")
        #     print(block_deltaG)
        metastable_list = np.array([metastable_list_names, metastable_list_deltaG])
        metastable_list = np.transpose(metastable_list).tolist()
        self.mineral_delta_G = metastable_list


class Phase:
    def __init__(self, phase_name) -> None:
        self.name = phase_name

    def add_composition(self, block_composition: list, temp_name: str, element_list: list, output_line_overflow: bool):
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
        # create dict in the from {"element name": "apfu", ..., "O": 6.0000, "Si": 2.0000, ...}
        # phase_composition = dict(zip(element_list, phase_composition))

        self.composition = phase_composition
        # important to also save Oxygen, to calculate Fe3


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