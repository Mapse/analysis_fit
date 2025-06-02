# 3D Fit: association production of $J/\psi$ and $D^*$

## Merging coffea data

Once the coffea files were produced from the nanoAODPlus root files (for more details, see: [condor_mc_lxplus [1]), it is interesting to merge then into a lower number of files. This will substantially reduce the time needed to proccess the next steps, mainly with the real data samples, which are really big. 
To do this, two python files are used:

```
merge_data.py
config_merge_data.py
```



[1]: https://github.com/Mapse/condor_mc_lxplus
