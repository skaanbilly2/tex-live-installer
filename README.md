# tex-live-installer
Texlive package install script in python


# Performance challenges
- Disk performance
- CPU 
- Network IO

To eliminate disk performance I used a ramdisk as the final destination of an extracted archive.

To see if CPU would be a bottleneck I checked the timings of network IO vs hash + extract write
In this scenario the proportion of time spent downloading was mostly more than 90% for big packages this could be lower.

The network IO can be solved by using non blocking io (asyncio) with the httpx client library, which allows multiple downloads to take place concurrently. To further eliminate overhead of setting up TCP connections I used the same asyncclient for all downloads, which automatically reuses the tcp socket.




# Asynchronous workers
If multiple workers are issued simultaneously, multiple downloads can take place at the same time. However all workers share the same thread and can wait for eachother if CPU is a bottleneck.
If CPU where to be a bottleneck, multiple process could be spun up with a subset of the work.

# Test environment
- laptop (plugged in during testing)
- Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz   2.60 GHz
- 16,0 GB
- Wi-Fi connection
- Python 3.7.9


# Results
Note: At the moment I have not redid any of these test, as such some variation on these can be expected.

## Baseline
Test: 300 containers (randomly shuffled) Installed size 282 MB

Full install  Installed size 7,18 GB (~= 4300 containers)


texlive gui installer (full install)
|    seconds     | Seconds/container | Installed size/s| 
|:-------------:|:-------------:|-------------:|
| 12000 | 2.8 |  0.6 MB/s |

Note: from now on MB/sec will refer to installed size/sec unless indicated otherwise.

Remarks:
My internet connection during the install could do about 20Mb/second (2.5 MB/sec)



Remarks:
My internet connection used in the following experiments can do about 50Mb/second (6.5MB/sec)

## Sequential  Pooled (main_seq_pooled)
This is the baseline, should be comparable to the time for the installer

|    seconds     | Seconds/container | Installed size/s| 
|:-------------:|:-------------:|-------------:|
| 183.46 | 0.6 |  1.5 MB/s |









## Async Pooled (main_async_pooled_all)
| Number of workers  |     seconds     | Speedup | Installed size/s |
|----------|:-------------:|:-------------:|------:|
| 1 | 114.89 | 60% | 2.4 MB/s |
| 8 | 66.11886239051819 | 177% | 4.3 MB/s |
| 20 | 59.47248697280884 | 210% | 4.7 MB/s|


The use of asynchronous calls allows us to use concurrent downloads as well as avoid using cpu time waiting.

## All results
| Name | Number of workers  |     seconds     | Speedup |  Installed size/s | Notes |
|----------|:-------------:|:-------------:|:-------------:|:-------------:|------:|
| texlive gui installer | ? | ? | ? | 0.6 MB/s | Different internet connection | 
| Sequential pooled( baseline) | 1 | 183.46 | 0 | 1.5 MB/| |
| Async Pooled | 1 | 114.89 | 60% |2.4 MB/s | |
| Async Pooled | 8 | 66.11886239051819 | 177% |  4.3 MB/s | |
| Async Pooled  | 20 | 59.47248697280884 | 210%| 4.7 MB/s| |





# Install
Make sure you have a python version >= 3.7
```
pip install -r requirements.txt
```
# Cli-tool

A small cli-tool to easily experiment with this installer.


## Usage
```
usage: python main.py [-h] [--configfile CONFIGFILE] [--inputfile INPUTFILE]
                      [--installdir INSTALLDIR] [--outputfile OUTPUTFILE]
                      [--mirror_base_url MIRROR_BASE_URL]
                      [--n_packages N_PACKAGES] [--reshuffle {True,False}]
                      [--asyncio {True,False}] [--n_workers N_WORKERS]
                      {extract_tlpdb,install}
```
### Configfile
The command will run with the defaults given in `CONFIGFILE` possibly overridden with command line parameters.

The `CONFIGFILE` can be used to specify a different path to the configfile. If not specified these defaults will be used:
```
DEFAULT_CONFIG_FILE_INSTALL = "config_install.json"
DEFAULT_CONFIG_FILE_EXTRACT = "config_extract.json"
```

### Extract_tlpdb

The `extract_tlpdb` command is used to read a tlpdb.txt file and translate it into a json file with the appropriate information to download. This essentially creates the packages.json (`OUTPUTFILE`) file from texlive.tlpdb.txt (`INPUTFILE`). 


### Install
The `install` command installs `N_PACKAGES` packages given in the `INPUTFILE` to the `INSTALLDIR`. It fetches them from the `MIRROR_BASE_URL` site. It does this asynchronously with `n_workers` is `asyncio` is set to true. Otherwise a sequential method is used. The `reshuffle` parameter determines if the packages are reshuffled before selecting `N_PACKAGES` from it, disable this for accurate performance result samples, enable this for increased performance in practice.