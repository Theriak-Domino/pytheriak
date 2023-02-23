# %%
from src.pytheriak import wrapper
# %%
theriak = wrapper.TherCaller(programs_dir="C:\\TheriakDominoWIN\\Programs",
                             database="ds55HP1_ONLYtestPytheriak.txt",
                             theriak_version="v28.05.2022",
                             verbose=True)

out = theriak.call_theriak(5000, 550, "SI(68.2)TI(0.76)AL(25.18)FE(9.96)MN(0.02)MG(4.36)CA(0.18)NA(0.06)K(7.74)H(100)O(?)")
blocks = theriak.read_theriak(out)[0]
# %%
blocks["block_phases"]
# %%
mineral_list = wrapper.Rock.get_mineral_list(blocks["block_volume"])
wrapper.Rock.extract_solution_subblocks(blocks["block_phases"], mineral_list)
# %%
