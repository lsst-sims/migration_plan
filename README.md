# Migration Plan
Planning for migrating sims code to use setup.py and conda-forge for installation instead of eups.


## Motivation

The vast majority of Rubin sims code is pure python, and thus doesn't benefit from the eups system as the DM stack which mixes python and C++.

We propose to migrate the Rubin sims code to use the standard python setup.py, and package the code to be distributable via conda-forge.

Advantages to moving sims code to a single git repo and distributing via conda-forge:

* Simplified install procedure for ourselves and collaborators (I think all our current dependencies are conda-installable)
* Easier to make changes across packages (moving a utility from MAF to sims_utils becomes 1 PR instead of 2)
* Can unify the documentation in the same repo
* Trivial to track versioning if everything is in the same repo, there is one git SHA for everything
* Cleaner directory structure (no more lsst/sims/thing1/thing2 to get to the code)
* Removes DM dependency. This is probably desirable/necessary for moving into operations. We don't want to be in a position where we can't install our code because a numpy update broke something in pipe_tasks


## Priority issues to check

Here are things that should be thought out before migrating.

* What to do with `sims_maf_contrib`. This repo currently has code from the project and the community, often that has dependencies beyond what we would like to support (e.g., sncosmo). The `sims_maf_contrib` repo also has a number of example jupyter notebooks, which could be migrated to the new repo, or converted into documentation. One potential solution would be to leave `sims_maf_contrib` as an independent repo, and if folks are interested in running it they would be responsible for installing it and the extra dependencies manually. Another option would be to also convert `sims_maf_contrib` to be a conda-installable package.

* What to do with legacy sims code that the project is no longer supporting? Part of the motivation for moving to our own build system is so things like sims_catUtils and API changes in the DM stack are no longer an issue. We need to hand off sims_catUtils, sims_coordUtils, etc.

* Sounds like this is compatible with what Telescope and Site are doing, as they are also using conda for their code. I propose that for operations we make a new package (that will have rubin_sims as a dependency) that has the functionality to load up the current state of the survey and simulate an upcoming night.

* Data files. Many of the repos currently rely on large pre-computed data sets. For example, `sims_maps` has pre-computed HEALpix maps of dust and stellar densities. Currently, we have a mix of solutions for handling these data files. Most of the repos have simple rsync scripts for downloading files hosted at NCSA, while `sims_skybrightness_data` is it's own repo holding only data and no code. I propose we write a simple sub-package that can be called to provide data blobs and downloads files if needed. If the user sets an environment variable, then that's where data will be put. Otherwise default to `$HOME/rubin_sim_data/` I suppose. Required files (e.g., for unit tests) will be downloaded with setup.py, the rest can have their own script to download. 

* Does anyone care about the git history of the old repos? I propose archiving the old repos and starting fresh without trying to transfer the full git histories of the files.

* Unit tests:  We can strip out the LSST-boilerplate and unit tests should migrate with just path and name updates. Are there any strong motivations on unit test directory structure?

* When to freeze and migrate:  Doing such a large migration will require freezing development until everything gets moved. Should announce plans and dates on Slack and community. Anywhere else? Email the SCOC?

* What to name it, where to host it:  Could go in lsst organization or lsst-sims. Any name ideas? rubin_sim? rubin_sched? 

* How to ensure users don't use the old code. We should have a plan for making sure it is not trivial for users to install an old verison of the code with eups. One option would be to make a final build of `lsst_sims` that does not include the migrated packages. 

* Any name changes we would like to make? I'd say swapping `featureScheduler` to `scheduler` would be good. Could even go `maf` to `viz`. We have a mix of underscore and camelCase, do we want to try to push for more uniformity?


Current repos to migrate:

* sims_almanac
* sims_cloudModel
* sims_downtimeModel
* sims_maf
* sims_maps
* sims_movingObjects
* sims_featureScheduler
* sims_seeingModel
* sims_skybrightness
* sims_skybrightness_pre
* sims_skybrightness_data
* sims_survey_fields
* sims_photUtiles
* sims_utils
* throughputs


repos to replace with new code:

* sims_coordUtils
* sims_catalogs (copy out the base-class for MAF, already done)

repos that we are no longer supporting:

* sims_catUtils
* sims_coordUtils
* sims_catalogs
* sims_data

Undecided repos:

* sims_sed_library


## New Repo Organization

```
rubin_sim
|  README
|  requirements.txt
|  setup.py
|
|--data/
|--doc/
|--test/ (tests here, or in each sub-dir? I think this can have sub-dirs.)
|--rubin_sim/
|--scripts/
```

## rubin_sim Organization

(dropping "sims_" from names. Maybe convert camelCase to underscores)

```
scheduler
 |   sims_featureScheduler
maf
 |   sims_maf
 |   sims_maps
site_models
 |   sims_almanac
 |   sims_cloudModel
 |   sims_downtimeModel
 |   sims_seeingModel
photometry
 |   sims_photUtils
utils
 |   sims_utils
 |   sims_survey_fields
 |   focal_plane_map (replacement for sims_coordUtils)
skybrightness
 |   sims_skybrightness
 |   sims_skybrightness_pre
 |   sims_skybrightness_data
moving_objects
 |   sims_movingObjects
data
 |   new util that can check for data files and download if needed
```

Rough order to migrate things:

* utils
* data
* throughputs to data
* photUtils
* site_models
* skybrightness
* scheduler
* maf
* moving_objects


## Expected 3rd Party Dependencies

Here are the packages we expect to have dependencies on

* numpy
* scipy
* matplotlib
* pandas
* sqlite3
* sqlalchemy
* pyephem
* astropy
* palpy
* oorb
* tornado
* jinja2

If we want to absorb `sims_maf_contrib` as well:

* sncosmo (might actually be easy to get rid of? Only used by `transientAsciiSEDMetric` which I dislike anyway.)


## The external data sets

One way to potentially manage the external data sets is to have directories for each set and label them. For example, we could have `throughputs_2021_May.tgz`, `throughputs_2022_June.tgz`, etc. stored at NCSA. Then the code has a hard-coded dictionary with keys of dataset-name and values of filename. Updating a dataset is a two-step process of creating a new .tgz file and updating the dictionary. This way it's possible to reconstruct the exact state of the software from any git commit. There is an issue that one must remember to re-download the proper dataset if you check out an earlier commit. Given that this is a fairly niche use-case, I think we can have a little section in the readme outlining what one has to do if they want exact repeatability from an earlier version.


## Lower Priority Issues

Other decisions that need to be made, but final details aren't needed to start migration.

* What to do with `throughputs` and `sims_sed_library`. These two packages are not currently dependencies, but have tools/data that could be useful in the future. It should be fine to leave them in limbo for the moment as they can be migrated into rubin_sim at anytime.

* Tiago gives the tip that it's good to keep the conda recipe out of the main code repo. Step one will be getting a repo that can build from source with setup.py, but after that we'll want to remember to put conda recipe elsewhere.

* Focal plane geometry. The only thing from the DM stack we currently use is the focal plane geometry. Proposed solution is to write some code that calls the DM stack to build a pre-computed lookup table that can then be used in this package and updated as needed. While the focal plane geometry is currently a dependency, it's not used by default, so there wouldn't be much loss of functionality if we finished this after migration.

* Data files that need to be updated:  Along with the focal plane geometry, there are values like telescope zeropoints, airmass extinction coefficients, etc that need to be computed elsewhere and saved. We should have a plan for how that happens, when we updated, how we note we have updated.

* Versioning of data files:  Do we need to include some versioning on our data blobs? This has been requested in the past, but we've never actually done it. 

* Executable files:  We have things like showMaf.py. I'm sure there's a way to handle executable python scripts so they get added to a users path on install, just need to learn what it is. Looks like things usually just go in a scripts/ directory.

* Continuous integration:  We will either need to have jenkins updated to build our new package, or setup a new CI. conda-forge has tools in place to link into things like Travis CI. 

* Documentation plan:  The current documentation is scattered and fragmentary. Presumably we can adopt a standard documentation system like sphinx and have it built and linked off www.lsst.io and can take down the outdated things like sims-maf.lsst.io etc. 
