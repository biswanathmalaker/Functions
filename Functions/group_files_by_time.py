def group_files_by_time(files , dt):
    """
    dt is timedelta object of python.\n
    files = sorted files by time.
    """

    import datetime
    import numpy as np

    obs_time = [file.split(".")[3] for file in files]
    obs_time = [datetime.datetime.strptime(t,"%Y-%m-%dT%H%M%SZ") for t in obs_time]
    obs_time = np.array(obs_time)

    Files_grouped = []
    group = []
    t0 = obs_time[0]
    for t,file in zip(obs_time,files):
        if t-t0<dt:
            group.append(file)
        else:
            Files_grouped.append(group)
            t0 = t
            group = [file]

    return Files_grouped

if __name__ == "__main__":
    import datetime
    import glob
    dt = datetime.timedelta(minutes=1)

    files = glob.glob("./data/171/*.fits")
    files = sorted(files)[0:17]

    group_files_by_time(files , dt)