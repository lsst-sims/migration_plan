import os
import warning
import subprocess

# Thoughts on how one might download the various datasets we need


def rsync_sims_data(data_dir=None, remote_location="lsst-rsync.ncsa.illinois.edu::sim/",
                    maps=False, orbit_files=False, test_sync=False):

    env_data_dir = os.getenv('RUBIN_SIM_DATA_DIR')

    # Catch if we've set the data directory differently in different places.
    if (data_dir is not None) & (env_data_dir is not None):
        if os.path.normpath(data_dir) != os.path.normpath(env_data_dir):
            ValueError("kwarg data_dir %s does not match environment variable %s" % (data_dir, env_data_dir))

    todownload = {}
    # There should be a faster way to do this?
    todownload['orbit_files'] = orbit_files
    todownload['maps'] = maps

    # Set the root data directory
    if data_dir is None:
        data_dir = env_data_dir
    if data_dir is None:
        warning.warn('No data directory kwarg specified and no $RUBIN_SIM_DATA_DIR env, using $HOME/rubin_sim_data')
        data_dir = os.path.join(os.getenv('HOME'), 'rubin_sim_data')

    # Check that the directory exists
    if not os.path.isdir(data_dir):
        warning.warn('Directory %s does not exist, attempting to create' % data_dir)
        os.mkdir(data_dir)

    # subprocess.call(["rsync", "-Ccavz", "--delete","DJStatic", "username@website"])
    base_call = ["rsync", "-avz", "--progress", "--delete"]

    for key in todownload:
        if todownload[key]:
            call = base_call + [os.path.join(remote_location, key)] + [os.path.join(data_dir, key)]
            subprocess.call(call)
