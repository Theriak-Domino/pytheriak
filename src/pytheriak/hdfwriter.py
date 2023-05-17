import h5py
from pathlib import Path
from datetime import date


class HDF5writer:
    def __init__(self, path_parent: str, filename: str) -> None:
        self.hdffile_path = Path(path_parent, filename + ".hdf5")

    def write_file(self, rock_collection: list, element_list: list, init_parameters_TherCaller, author_name: str = "unknown author"):
        """_summary_

        Args:
            rock_collection (list): _description_
            element_list (list): _description_
            init_parameters_TherCaller (pytheriak.wrapper.TherCaller): _description_
            author_name (str, optional): _description_. Defaults to "unknown author".
        """
        with h5py.File(self.hdffile_path, "w") as hdf_file:
            hdf_file.attrs["date"] = str(date.today())
            hdf_file.attrs["author"] = author_name

            hdf_file.attrs["theriak_version"] = init_parameters_TherCaller.theriak_version
            hdf_file.attrs["theriak_database"] = init_parameters_TherCaller.database

            hdf_file.attrs["global element idx (bulk, phases)"] = element_list

            for rock in rock_collection:
                # create a hdf_group for a Rock()-instance
                rock_group = hdf_file.create_group(str(rock))
                # save THERIN strings, to reproduce the minimisation
                rock_group.attrs["THERIN_PT"] = rock.therin_PT
                rock_group.attrs["THERIN_bulk"] = rock.therin_bulk

                # save physical params as attributes
                rock_group.attrs["P"] = int(rock.pressure)
                rock_group.attrs["T"] = int(rock.temperature)
                rock_group.attrs["G_system"] = float(rock.g_system)
                rock_group.attrs["G_system_per_mol_of_input"] = float(rock.g_system_per_mol_of_input)
                # save compositional data (bulk) as dataset, element_list acts as globally valid look-up table for idx --> element
                rock_group.create_dataset("bulk_composition_in_mol", data=rock.bulk_composition_moles)
                rock_group.create_dataset("bulk_composition_in_mol_percent", data=rock.bulk_composition_mol_percent)

                # make a sub-group for mineral_assemblage of the Rock()
                mineral_assemblage = rock_group.create_group("mineral_assemblage")

                for mineral in rock.mineral_assemblage:
                    mineral_group = mineral_assemblage.create_group(mineral.name)

                    # save physical params as attributes
                    mineral_group.attrs["n_moles"] = mineral.n
                    mineral_group.attrs["volume"] = mineral.vol
                    mineral_group.attrs["volume_percent_of_total_solids"] = mineral.vol_percent
                    mineral_group.attrs["density"] = mineral.density
                    # save mineral composition as dataset, element_list acts as globally valid look-up table for idx --> element
                    mineral_group.create_dataset("phase_composition_apfu", data=mineral.composition_apfu)
                    mineral_group.create_dataset("phase_composition_moles", data=mineral.composition_moles)

                # make a sub-group for fluid_assemblage of the Rock()
                fluid_assemblage = rock_group.create_group("fluid_assemblage")

                for fluid in rock.fluid_assemblage:
                    fluid_group = fluid_assemblage.create_group(fluid.name)

                    # save physical params as attributes
                    fluid_group.attrs["n_moles"] = fluid.n
                    fluid_group.attrs["volume"] = fluid.vol
                    fluid_group.attrs["density"] = fluid.density

                    fluid_group.create_dataset("phase_composition_apfu", data=fluid.composition_apfu)
                    fluid_group.create_dataset("phase_composition_moles", data=fluid.composition_moles)

                # save deltaG of all metastable minerals for the Rock()
                metastable_minerals_dataset = rock_group.create_dataset("delta_G_meta-stable_minerals", data=list(rock.mineral_delta_G.values()))
                metastable_minerals_dataset.attrs["mineral_names"] = list(rock.mineral_delta_G.keys())
                metastable_minerals_dataset.attrs["unit"] = "joules"
