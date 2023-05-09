from pytheriak import wrapper, hdfwriter
import h5py
import numpy as np


def create_rockcollection():
    """Generates a test rock collection to be saved as hdf5 file.
    """
    theriak = wrapper.TherCaller(programs_dir="C:\\TheriakDominoWIN\\Programs",
                                 database="ds55HP1_ONLYtestPytheriak.txt",
                                 theriak_version="v28.05.2022",
                                 verbose=True)

    rock1, element_list1 = theriak.minimisation(pressure=5000, temperature=550,
                                                bulk="SI(68.0)TI(0.72)AL(25.18)FE(9.96)MN(0.02)MG(4.50)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")

    rock2, element_list2 = theriak.minimisation(pressure=8000, temperature=600,
                                                bulk="SI(68.0)TI(0.72)AL(25.18)FE(9.96)MN(0.02)MG(4.50)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")

    rock_collection = [rock1, rock2]

    assert element_list1 == element_list2, "Element lists in create_rockcollection() are not equal."

    return theriak, rock_collection, element_list1


def test_write_to_hdf():
    """Saves test rock collection as hdf5 file.
    """
    theriak, rock_collection, element_list = create_rockcollection()

    writer = hdfwriter.HDF5writer(path_parent=".", filename="dataset_test_hdfwriter")
    writer.write_file(rock_collection, element_list, init_parameters_TherCaller=theriak, author_name="test_author")

    print("Created hdf5 file. Test passed.")


def read_hdf_file():
    hdf_file = h5py.File("dataset_test_hdfwriter.hdf5", "r")

    rock_group_names = list(hdf_file.keys())

    return hdf_file, rock_group_names


def test_bulkcomposition(hdf_file, rock_group_names):
    SI = 68.0
    TI = 0.72
    AL = 25.18
    FE = 9.96
    MN = 0.02
    MG = 4.50
    CA = 0.18
    NA = 0.06
    K = 7.74
    H = 100

    element_idx = list(hdf_file.attrs["global element idx (bulk, phases)"])
    bulk_in_mol = list(hdf_file[rock_group_names[0]]["bulk_composition_in_mol"])

    assert bulk_in_mol[element_idx.index("SI")] == SI, "SI in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("TI")] == TI, "TI in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("AL")] == AL, "AL in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("FE")] == FE, "FE in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("MN")] == MN, "MN in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("MG")] == MG, "MG in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("CA")] == CA, "CA in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("NA")] == NA, "NA in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("K")] == K, "K in bulk composition is not correct."
    assert bulk_in_mol[element_idx.index("H")] == H, "H in bulk composition is not correct."


def test_dG_metasatbale_minerals(hdf_file, rock_group_names):
    BENCHMARK_dG_ST_fst_rock1 = 3.01992E+03

    list_metastable_minerals_rock1 = hdf_file[rock_group_names[0]]["delta_G_meta-stable_minerals"].attrs["mineral_names"]
    idx_ST_fst_rock1 = np.where(list_metastable_minerals_rock1 == "ST_fst")[0]

    dG_ST_fst_rock1 = hdf_file[rock_group_names[0]]["delta_G_meta-stable_minerals"][idx_ST_fst_rock1][0]

    assert dG_ST_fst_rock1 == BENCHMARK_dG_ST_fst_rock1, "dG of ST_fst in first rock is not correct. Retrieved was the value: " + str(dG_ST_fst_rock1)


if __name__ == "__main__":
    create_rockcollection()
    test_write_to_hdf()
    hdf_file, rock_group_names = read_hdf_file()
    test_bulkcomposition(hdf_file, rock_group_names)
    test_dG_metasatbale_minerals(hdf_file, rock_group_names)