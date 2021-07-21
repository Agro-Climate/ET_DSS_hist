# dssat-base-files

This repo consists of some minimum files/directory that you need before running DSSAT on Linux. The goal is to provide a template for the "working directory" where you can run the DSSAT model from.

## What You Need:

### DSSAT
Follow the guidelines from the [DSSAT](https://github.com/eusojk/dssat-csm-os) repo to download and compile it on your system.

After compiling DSSAT, copy the binary file to this working directory.

### Genotype Files
This repo currently has the required files (SGCER047) for running the Sorghum model. Other genotype files can be found [here](https://github.com/eusojk/dssat-csm-os/tree/develop/Data/Genotype).

### Experimental Files
This repo has some sample .SNX and .WTH files. Please add your own files as needed.

### DSSBatch.V47
Depending on how you run DSSAT, this file needs to be updated accordingly. It is currently set to run the `SESGTEMP.SNX` experimental file for Sorghum in batch mode. It's only provided for demonstration purposes.

## Testing
Copy the `dscsm047` binary into this working directory and rename it as `DSCSM047.EXE`.

Then run: `DSCSM047.EXE SGCER047 B DSSBatch.V47`

## References

[1] https://github.com/DSSAT/dssat-csm-os 

