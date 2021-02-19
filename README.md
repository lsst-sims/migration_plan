# migration_plan
Planning for migrating sims code to use setup.py instead of eups


## Motivation

The vast majority of Rubin sims code is pure python, and thus doesn't benefit from the eups system as the DM stack which mixes python and C++.

We propose to migrate the Rubin sims code to use the standard python setup.py, and package the code to be distributable via conda-forge.

Advantages to moving sims code to a single git repo and distributing via conda-forge:

* Simplified install procedure for ourselves and collaborators (I think all our current dependencies are conda-installable)
* Easier to make changes across packages (moving a utility from MAF to sims_utils becomes 1 PR instead of 2)
* Can unify the documentation in the same repo
* Trivial to track versioning if everything is in the same repo
* Cleaner directory structure (no more lsst/sims/thing1/thing2 to get to code)
* Removes DM dependency. This is probably desireable for moving into opperations


## Priority issues to check

Here are things that need to be thought out before migrating.

What to do with `sims_maf_contrib`. This repo currently has code from the project and the community, often that has dependencies beyond what we would like to support (e.g., sncosmo). The `sims_maf_contrib` repo also has a number of example jupyter notebooks, which could be migrated to the new repo. One potential solution would be to leave `sims_maf_contrib` as an independent repo, and if folks are interested in running it they would be responsible for installing it and the extra dependencies manually.

What to do with legacy sims code that the project is no longer supporting? Part of the motivation for moving to our own build system is so things like sims_catUtils and API changes in the DM stack are no longer an issue. We need to finish handing off sims_catUtils and other image simulation utils. 

Need to check (probably with Tiago), that this is compatible with the opperations plan for telescope and site. I don't know what their plans are for their code--this might be a good opportunity for them to migrate to conda as well.

Data files. Many of the repos currently rely on large pre-computed data sets. For example, `sims_maps` has pre-computed HEALpix maps of dust and stellar densities. Currently, we have a mix of solutions for handling these data files. Most of the repos have simple rsynv scripts for downloading files hosted at NCSA, while `sims_skybrightness_data` is it's own repo holding only data and no code. I propose we write a simple sub-package that can be called to provide data blobs and downloads files if needed. 

Does anyone care about the git history of the old repos? I propose archiving the old repos and starting fresh without trying to transfer the full git histories of the files.

Versioning of data files:  Do we need to include some versioning on our data blobs? 

unit tests:  We can strip out the LSST-boilerplate and unit tests should migrate with just path/name updates. 

When to freeze and migrate:  Doing such a large migration will require freezing development until everything gets moved.


repos to migrate:

sims_almanac
sims_cloudModel
sims_downtimeModel
sims_maf
sims_maps
sims_featureScheduler
sims_seeingModel
sims_skybrightness
sims_skybrightness_pre
sims_skybrightness_data
sims_survey_fields
sims_photUtiles
sims_utils

repos to replace:

sims_coordUtils

repos that we are no longer supporting:

sims_catUtils


## repo organization

README
requirements.txt
setup.py

data/
doc/
tests/
rubin_sim/
scripts/

## rubin_sim Organization

scheduler
    sims_featureScheduler
maf
    sims_maf
    sims_maps
site_models
    sims_almanac
    sims_cloudModel
    sims_downtimeModel
    sims_seeingModel
photometry
    sims_photUtiles
utils
    sims_utils
    sims_survey_fields
skybrightness
    sims_skybrightness
    sims_skybrightness_pre
    sims_skybrightness_data
data
    new sub-package for grabbing data files from NCSA

## Lower Priority Issues

Other decisions that need to be made, but final details aren't needed to start migration.

Focal plane geometry. The only thing from the DM stack we currently use is the focal plane geometry. Proposed solution is to write some code that calls the DM stack to build a pre-computed lookup table that can then be used in this package and updated as needed. While the focal plane geometry is currently a dependency, it's not used by default, so there wouldn't be much loss of functionality if we finished this after migration.

Data files that need to be updated:  Along with the focal plane geometry, there are values like telescope zeropoints, airmass exticntion coefficents, etc that need to be computed elsewhere and saved. We should have a plan for how that happens, when we updated, how we note we have updated.

executable files:  We have things like showMaf.py. I'm sure there's a way to handle executable python scripts so they get added to a users path on install, just need to learn what it is. Looks like things usually just go in a scripts/ directory.

Continuous integration:  We will either need to have jenkins updated to build our new package, or setup a new CI. conda-forge has tools in place to link into things like Travis CI. 

Documentation plan:  The current documentation is scattered and fragmentary. Presumably we can adopt a standard documentation system like sphinx and have it built and linked off www.lsst.io and can take down the outdated things like sims-maf.lsst.io etc. 

