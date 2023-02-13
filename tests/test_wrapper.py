from pytheriak import wrapper
from pytheriak.wrapper import Rock

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


# ## TEST
def test_add_minerals():
    test_rock = Rock(pressure=6046, temperature=417)
    test_rock.add_minerals(block_volume=block_volume,
                           block_composition=block_composition,
                           block_elements=block_elements,
                           output_line_overflow=output_overflow)

    assert [mineral.name for mineral in test_rock.mineral_assemblage] == benchmark_mineral_names
    assert [mineral.composition_apfu for mineral in test_rock.mineral_assemblage if mineral.name == "BI05_ann"][0] == benchmark_biotite_compositon
    assert [mineral.composition_moles for mineral in test_rock.mineral_assemblage if mineral.name == "BI05_ann"][0] == benchmark_biotite_compositon_mol


def test_TherCaller():
    """To run this test a  theriak.ini (on Windows) and the correct dtabase must be place in the projects folder.
    """
    theriak = wrapper.TherCaller(programs_dir="C:\\TheriakDominoWIN\\Programs",
                                 database="ds55HP1.txt",
                                 theriak_version="v28.05.2022",
                                 cwd=".", verbose=True)

    rock, element_list = theriak.minimisation(pressure=4000, temperature=550, bulk="AL(2)SI(1)H(100)O(?)")

    # ## BENCHMARKS
    bm_g_system = -20519354.34
    bm_mineral_assemblage = ["and"]
    bm_fluid_assemblage = ["H2O"]
    bm_mineral_composition = [5.0, 2.0, 0.0, 1.0]
    bm_fluid_composition = [1.0, 0.0, 2.0, 0.0]

    assert rock.g_system == bm_g_system, "G_system failed"
    assert [mineral.name for mineral in rock.mineral_assemblage] == bm_mineral_assemblage, "Mineral assemblage failed"
    assert [mineral.composition_apfu for mineral in rock.mineral_assemblage if mineral.name == "and"][0] == bm_mineral_composition, "Min. comp. failed"
    assert [fluid.name for fluid in rock.fluid_assemblage] == bm_fluid_assemblage, "Fluid assemblage failed"
    assert [fluid.composition_apfu for fluid in rock.fluid_assemblage if fluid.name == "H2O"][0] == bm_fluid_composition, "Fluid composition failed"


if __name__ == "__main__":
    test_add_minerals()
    test_TherCaller()
