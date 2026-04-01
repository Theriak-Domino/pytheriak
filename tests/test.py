import unittest
from pytheriak import wrapper, hdfwriter
from pytheriak.wrapper import Rock
import h5py
import numpy as np

from pathlib import Path

# ## TEST DATA
block_volume = [' volumes and densities of stable phases:',
                ' ---------------------------------------',
                '',
                '  solid phases           N       volume/mol  volume[ccm]    vol%  |    wt/mol       wt [g]      wt %  | density [g/ccm]',
                '  ------------                                                    |                                   |                ',
                '  PLC1_abh             4.5568     101.0292     460.3719   18.6276 |   263.3673    1200.1176   17.0845 |     2.606844',
                '  WM02V_mu             6.9877     140.3973     981.0603   39.6957 |   399.4503    2791.2564   39.7354 |     2.845143',
                '  GTT01_gr             0.0581     121.7314       7.0783    0.2864 |   472.0965      27.4510    0.3908 |     3.878183',
                '  BI05_ann             0.3682     152.5480      56.1744    2.2729 |   478.8624     176.3368    2.5103 |     3.139094',
                '  CHL_daph             1.5982     212.9668     340.3604   13.7717 |   666.7608    1065.6075   15.1696 |     3.130821',
                '  q                   20.4768      22.8894     468.7023   18.9646 |    60.0843    1230.3350   17.5146 |     2.624982',
                '  sph                  0.9253      55.8222      51.6549    2.0901 |   196.0405     181.4055    2.5824 |     3.511876',
                '  cz                   0.7749     136.8505     106.0522    4.2911 |   454.3573     352.1037    5.0124 |     3.320099',
                '                                             ----------  -------- |              ----------  -------- |   ----------',
                '  total of solids                             2471.4548  100.0000 |               7024.6136  100.0000 |     2.842299',
                ' ',
                '',
                '  gases and fluids       N       volume/mol  volume[ccm]               wt/mol       wt [g]              density [g/ccm]',
                '  ----------------                                                                                                     ',
                '  H2O                 35.8638      18.6578      669.138                18.0153     646.0963                 0.965565',
                '',
                '',
                ' -----------------------------',
                ' H2O content of stable phases:',
                ' -----------------------------',
                '                                                                  |   wt% of     wt% of     wt% of',
                '  solid phases           N      H2O[pfu]    H2O[mol]     H2O [g]  |   phase      solids     H2O.solid',
                '  ------------                                                    |',
                '  WM02V_mu             6.9877     1.000       6.9877     125.8862 |   4.51002    1.79207    49.4316',
                '  BI05_ann             0.3682     1.000       0.3682       6.6340 |   3.76210    0.09444     2.6050',
                '  CHL_daph             1.5982     4.000       6.3927     115.1670 |  10.80764    1.63948    45.2225',
                '  cz                   0.7749     0.500       0.3875       6.9805 |   1.98250    0.09937     2.7410',
                '                                            --------   ---------- |             --------',
                '  total H2O in solids                        14.1362     254.6677 |              3.62536',
                ' ', '                                                                  |   wt% of',
                '  gases and fluids       N      H2O[pfu]    H2O[mol]     H2O [g]  |   phase',
                '  ----------------                                                |',
                '  H2O                 35.8638     1.000      35.8638     646.0963 | 100.00000']

block_composition = [' elements per formula unit:',
                     ' ',
                     ' PLC1_abh            8.000000   1.066655   0.066655   0.000000   0.000000   0.004895   0.000000   0.000000   0.928450   2.933345',
                     '                     0.000000   0.000000',
                     ' WM02V_mu           12.000000   2.666946   0.000000   0.102160   2.000000   0.900069   0.000000   0.059424   0.090046   3.171469',
                     '                     0.000000   0.000000',
                     ' GTT01_gr           12.000000   2.000000   1.565363   0.695636   0.000000   0.000000   0.729346   0.009655   0.000000   3.000000',
                     '                     0.000000   0.000000',
                     ' BI05_ann           12.000000   1.051688   0.000000   1.926930   2.000000   1.000000   0.026499   0.941144   0.000000   2.974156',
                     '                     0.039792   0.000000',
                     ' CHL_daph           18.000000   2.024227   0.000000   3.463994   8.000000   0.000000   0.054958   1.468935   0.000000   2.987887',
                     '                     0.000000   0.000000',
                     ' H2O                 1.000000   0.000000   0.000000   0.000000   2.000000   0.000000   0.000000   0.000000   0.000000   0.000000',
                     '                     0.000000   0.000000',
                     ' q                   2.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   1.000000',
                     '                     0.000000   0.000000',
                     ' sph                 5.000000   0.000000   1.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   1.000000',
                     '                     1.000000   0.000000',
                     ' cz                 13.000000   3.000000   2.000000   0.000000   1.000000   0.000000   0.000000   0.000000   0.000000   3.000000',
                     '                     0.000000   0.000000']

block_elements = [' elements in stable phases:',
                  ' --------------------------',
                  '',
                  '                      O          AL         CA         FE         H          K          MN         MG         NA         SI   ',
                  '                      TI         E    ',
                  ' PLC1_abh           36.454569   4.860555   0.303734   0.000000   0.000000   0.022305   0.000000   0.000000   4.230782  13.366730',
                  '                     0.000000   0.000000',
                  ' WM02V_mu           83.852935  18.635939   0.000000   0.713871  13.975489   6.289454   0.000000   0.415240   0.629218  22.161418',
                  '                     0.000000   0.000000',
                  ' GTT01_gr            0.697765   0.116294   0.091021   0.040449   0.000000   0.000000   0.042409   0.000561   0.000000   0.174441',
                  '                     0.000000   0.000000',
                  ' BI05_ann            4.418892   0.387275   0.000000   0.709575   0.736482   0.368241   0.009758   0.346568   0.000000   1.095206',
                  '                     0.014653   0.000000',
                  ' CHL_daph           28.767342   3.235090   0.000000   5.536105  12.785485   0.000000   0.087833   2.347631   0.000000   4.775197',
                  '                     0.000000   0.000000',
                  ' H2O                35.863797   0.000000   0.000000   0.000000  71.727594   0.000000   0.000000   0.000000   0.000000   0.000000',
                  '                     0.000000   0.000000',
                  ' q                  40.953627   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000  20.476813',
                  '                     0.000000   0.000000',
                  ' sph                 4.626735   0.000000   0.925347   0.000000   0.000000   0.000000   0.000000   0.000000   0.000000   0.925347',
                  '                     0.925347   0.000000',
                  ' cz                 10.074338   2.324847   1.549898   0.000000   0.774949   0.000000   0.000000   0.000000   0.000000   2.324847',
                  '                     0.000000   0.000000',
                  ' total:            245.710000  29.560000   2.870000   7.000000 100.000000   6.680000   0.140000   3.110000   4.860000  65.300000',
                  '                     0.940000   0.000000', '']

element_list = ['O', 'AL', 'CA', 'FE', 'H', 'K', 'MN', 'MG', 'NA', 'SI', 'TI']

output_overflow = True

# ## EXPECTED RESULTS
benchmark_mineral_names = ["PLC1_abh", "WM02V_mu", "GTT01_gr", "BI05_ann", "CHL_daph", "q", "sph", "cz"]

benchmark_biotite_compositon = [12.0, 1.051688, 0.0, 1.92693, 2.0, 1.0, 0.026499, 0.941144, 0.0, 2.974156, 0.039792]
benchmark_biotite_compositon_mol = [4.418892, 0.387275, 0.0, 0.709575, 0.736482, 0.368241, 0.009758, 0.346568, 0.0, 1.095206, 0.014653]

class TestRock(unittest.TestCase):
    def test_add_minerals(self):
        test_rock = Rock(pressure=6046, temperature=417)
        test_rock.add_minerals(block_volume=block_volume,
                               block_solutions={"a place holder empty list": None},
                               block_composition=block_composition,
                               block_elements=block_elements,
                               output_line_overflow=output_overflow)

        assert [mineral.name for mineral in test_rock.mineral_assemblage] == benchmark_mineral_names
        assert [mineral.composition_apfu for mineral in test_rock.mineral_assemblage if mineral.name == "BI05_ann"][0] == benchmark_biotite_compositon
        assert [mineral.composition_moles for mineral in test_rock.mineral_assemblage if mineral.name == "BI05_ann"][0] == benchmark_biotite_compositon_mol


    def test_add_endmember_properties(self):
        theriak = wrapper.TherCaller(programs_dir=Path.home() / "TheriakDominoMAC" / "Programs",
                                     database="tc55_for_testing",
                                     theriak_version="v2023.06.11",
                                     verbose=True)

        rock, element_list = theriak.minimisation(pressure=5000, temperature=450,
                                                  bulk="SI(68.2)TI(0.76)AL(25.18)FE(9.96)MG(4.36)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")

        biotite_activities = [mineral.endmember_activities for mineral in rock.mineral_assemblage if mineral.name == "BIO_ann"][0]
        print(biotite_activities["phl"])
        print(biotite_activities["ann"])
        assert biotite_activities["phl"] == 0.0196196, "Phlogopite act in biotite does not match."
        assert biotite_activities["ann"] == 0.312306, "Annite act in biotite does not match."

        # NO longer the case with new version of theriak! check also for a failing minimisation
        # rock, element_list = theriak.minimisation(pressure=5000, temperature=450,
        #                                           bulk="SI(68.2)TI(0.76)AL(25.18)FE(9.96)MN(0.02)MG(4.36)CA(0.18)NA(0.06)K(7.74)H(100)O(?)",
        #                                           return_failed_minimisation=True)

        # chlorite_activities = [mineral.endmember_activities for mineral in rock.mineral_assemblage if mineral.name == "CHL_daph"][0]
        # print(chlorite_activities["daph"])
        # print(chlorite_activities["ames"])
        # assert chlorite_activities["daph"] == 1.00000, "Failed minimisation case: Daphnite act in chlorite does not match."
        # assert chlorite_activities["ames"] == 0.0552862, "Failed minimisation case: Amesite act in chlorite does not match."

        # additional test, with different accessing of solutions
        solutions = [mineral.name for mineral in rock.mineral_assemblage if mineral.solution_phase]
        print(solutions)
        assert solutions == ['ILM_oilm', 'CHLR_daph', 'PHNG_mu', 'BIO_ann'], "Name-list of solutions does not match."

        # check for fluid solutions
        theriak = wrapper.TherCaller(programs_dir=Path.home() / "TheriakDominoMAC" / "Programs",
                                     database="JUN92_for_testing",
                                     theriak_version="v2023.06.11",
                                     verbose=True)

        rock, element_list = theriak.minimisation(pressure=5000, temperature=450,
                                                  bulk="SI(68.2)TI(0.76)AL(25.18)FE(9.96)MN(0.02)MG(4.36)CA(0.18)NA(0.06)K(7.74)H(100)C(25)O(?)")

        fluid_activities = [fluid.endmember_activities for fluid in rock.fluid_assemblage if fluid.name == "H2O-CO2_H2O"][0]
        assert fluid_activities["STEAM"] == 0.783832, "STEAM activity in fluid phase does not match."

        fluid_endmembers = [fluid.endmember_fractions for fluid in rock.fluid_assemblage if fluid.name == "H2O-CO2_H2O"][0]
        assert fluid_endmembers["CARBON-DIOXIDE"] == 0.426759, "CARBON-DIOXIDE fraction in fluid phase does not match."
        # check if state-attribute Phase().solution_phase is working correctly
        fluid_endmembers = [fluid.endmember_fractions for fluid in rock.fluid_assemblage if fluid.solution_phase][0]
        assert fluid_endmembers["STEAM"] == 0.573241, "STEAM fraction in fluid phase not match. Phase().solution_phase attr prob not updated correctly."


    def test_add_bulk_density(self):
        test_rock = Rock(pressure=6046, temperature=417)
        test_rock.add_bulk_density(block_volume=block_volume)

        assert test_rock.bulk_density == 2.842299


class TestTherCaller(unittest.TestCase):
    def test_TherCaller(self):
        """
        To run this test a  theriak.ini (on Windows) and the correct database must be place in the projects folder.
        """
        theriak = wrapper.TherCaller(programs_dir=Path.home() / "TheriakDominoMAC" / "Programs",
                                     database="tc55_for_testing",
                                     theriak_version="v2023.06.11",
                                     verbose=True)

        rock, element_list = theriak.minimisation(pressure=10000, temperature=400, bulk="AL(2)SI(1)O(?)")

        # ## BENCHMARKS
        bm_g_system = -2630473.73
        bm_mineral_assemblage = ["kyanite"]
        bm_mineral_composition = [5.0, 2.0, 1.0]

        assert rock.g_system == bm_g_system, "G_system failed"
        assert [mineral.name for mineral in rock.mineral_assemblage] == bm_mineral_assemblage, "Mineral assemblage failed"
        assert [mineral.composition_apfu for mineral in rock.mineral_assemblage if mineral.name == "kyanite"][0] == bm_mineral_composition, "Min. comp. failed"

    # no longer working with the newest version of theriak
    # def test_TherCaller_failed_minimisation(self):
    #     """To run this test a  theriak.ini (on Windows) and the correct database must be place in the projects folder.
    #     """
    #     print("Two WARNINGS for failed minimisation should be printet below:")

    #     theriak = wrapper.TherCaller(programs_dir="~/TheriakDominoMAC/Programs",
    #                                  database="ds55HP1_ONLYtestPytheriak.txt",
    #                                  theriak_version="v28.05.2022",
    #                                  verbose=True)

    #     fail_string, element_list_placeholder = theriak.minimisation(pressure=3863, temperature=656,
    #                                                                  bulk="SI(68.2)TI(0.76)AL(25.18)FE(9.96)MN(0.02)MG(4.36)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")
    #     rock, element_list = theriak.minimisation(pressure=3863, temperature=656,
    #                                               bulk="SI(68.2)TI(0.76)AL(25.18)FE(9.96)MN(0.02)MG(4.36)CA(0.18)NA(0.06)K(7.74)H(100)O(?)",
    #                                               return_failed_minimisation=True)

    #     bm_g_system = -117647924.43

    #     assert type(fail_string) == str, "failed minimisation not detected"
    #     assert rock.g_system == bm_g_system


class TestHDFwriter(unittest.TestCase):
    def test_create_rockcollection(self):
        """Generates a test rock collection to be saved as hdf5 file.
        """
        theriak = wrapper.TherCaller(programs_dir=Path.home() / "TheriakDominoMAC" / "Programs",
                                     database="tc55_for_testing",
                                     theriak_version="v2023.06.11",
                                     verbose=True)

        rock1, element_list1 = theriak.minimisation(pressure=5000, temperature=500,
                                                    bulk="SI(68.0)TI(0.72)AL(25.18)FE(9.96)MN(0.02)MG(4.50)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")

        rock2, element_list2 = theriak.minimisation(pressure=8000, temperature=600,
                                                    bulk="SI(68.0)TI(0.72)AL(25.18)FE(9.96)MN(0.02)MG(4.50)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")

        rock_collection = [rock1, rock2]

        assert element_list1 == element_list2, "Element lists in create_rockcollection() are not equal."

        return theriak, rock_collection, element_list1


    def test_write_to_hdf(self):
        """Saves test rock collection as hdf5 file.
        """
        theriak, rock_collection, element_list = self.test_create_rockcollection()

        writer = hdfwriter.HDF5writer(path_parent=Path("tests") / "test_data", filename="dataset_test_hdfwriter")
        writer.write_file(rock_collection, element_list, init_parameters_TherCaller=theriak, author_name="test_author")

        print("Created hdf5 file. Test passed.")


    def read_hdf_file(self):
        hdf_file = h5py.File(Path("tests", "test_data", "dataset_test_hdfwriter.hdf5"), "r")

        rock_group_names = list(hdf_file.keys())

        return hdf_file, rock_group_names


    def test_bulkcomposition(self):
        hdf_file, rock_group_names = self.read_hdf_file()

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


    def test_dG_metasatbale_minerals(self):
        hdf_file, rock_group_names = self.read_hdf_file()
        BENCHMARK_dG_ST_fst_rock1 = 4.43481E+04

        list_metastable_minerals_rock1 = hdf_file[rock_group_names[1]]["delta_G_meta-stable_minerals"].attrs["mineral_names"]
        idx_ST_fst_rock1 = np.where(list_metastable_minerals_rock1 == "STAU_fst")[0]

        dG_ST_fst_rock1 = hdf_file[rock_group_names[1]]["delta_G_meta-stable_minerals"][idx_ST_fst_rock1][0]

        assert dG_ST_fst_rock1 == BENCHMARK_dG_ST_fst_rock1, "dG of ST_fst in first rock is not correct. Retrieved was the value: " + str(dG_ST_fst_rock1)





if __name__ == "__main__":
    unittest.main()

