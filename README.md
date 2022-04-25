# tex-live-installer
Texlive package install script in Python

**!!! PROTOTYPE FOR EVALUATION !!!**


# Performance challenges
- Disk performance
- CPU 
- Network IO

To eliminate disk performance in tests I used a ramdisk as the final destination of an extracted archive.

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
- SSD

SSD disk speed:

![Crystaldiskmark SSD bench](/assets/images/SSD.png "Speedy SSD")

# Results
Note: At the moment I have not redid any of these test, as such some variation on these can be expected.

## Baseline
Test: 300 containers (randomly shuffled) Installed size 282 MB

Full install  Installed size 7,18 GB (~= 4300 containers)


texlive gui installer (full install)
|    seconds     | Seconds/container | Installed size/s| Drive | Network bandwith | Notes |
|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|-------------:|
| 12000 | 2.8 |  0.6 MB/s | SSD |16Mbps | FULL INSTALL|

Note: from now on MB/sec will refer to installed size/sec unless indicated otherwise.

Remarks:
My internet connection during the install could do about 16Mb/second (2 MB/sec)




## Sequential  Pooled (main_seq_pooled)
This is the baseline, which should be comparable to the time for the installer

|    seconds     | Seconds/container | Installed size/s|  Drive | Network bandwith | Notes |
|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|-------------:|
 230.41 | 0.76 |  1.22 MB/s | SSD | 16 Mbps | |
||
| 207.59 | 0.7 |  1.36 MB/s | Ramdisk | 16 Mbps | |
| 183.46 | 0.6 |  1.5 MB/s | Ramdisk | 50 Mbps | |







## Async Pooled (main_async_pooled_all)

The use of asynchronous calls allows us to use concurrent downloads as well as avoid using cpu time waiting.


### 16 Mbps internet connection
The 20 workers scenario with a 16 Mbps was not tested due to a limited bandwith causing the downloads to timeout. This can be resolved in multiple ways. 

#### Ramdisk
| Number of workers  |     seconds     | Speedup | Installed size/s | Drive | Network bandwith | Notes |
|----------|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|------:|
| 1 | 162.69 | 100% | 1.7 MB/s | Ramdisk | 16 Mbps
| 8 |  93.28 | 174% | 3.0 MB/s | Ramdisk | 16 Mbps


#### SSD
| Number of workers  |     seconds     | Speedup | Installed size/s | Drive | Network bandwith | Notes |
|----------|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|------:|
| 1 | 155.20 | 100% | 1.8 MB/s | SSD | 16 Mbps
| 8 | 99.65 | 156% | 2.83 MB/s | SSD | 16 Mbps



### 50 Mbps internet connection - Ramdisk
| Number of workers  |     seconds     | Speedup | Installed size/s | Drive | Network bandwith | Notes |
|----------|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|------:|
| 1 | 114.89 | 100% | 2.4 MB/s |  Ramdisk | 50 Mbps
| 8 | 66.13  | 177% | 4.3 MB/s | Ramdisk | 50 Mbps
| 20 | 59.47 | 210% | 4.7 MB/s| Ramdisk | 50 Mbps

## All results
Note: Speedup (based on Installed size/s) relative to the texlive gui installer 
| Name | Number of workers  |     seconds     | Speedup |  Installed size/s | Drive | Network bandwith | Notes |
|----------|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|:-------------:|------:|
| texlive gui installer | ? | 12000 | 100% | 0.6 MB/s | SSD | 16 Mbps | FULL INSTALL (3h 20m)
||
| Sequential pooled( baseline) | 1 | 230.41 | 203% | 1.22 MB/s | SSD | 16 Mbps
||
| Sequential pooled( baseline) | 1 | 207.59 | 226% | 1.36 MB/s | Ramdisk | 16 Mbps
| Sequential pooled( baseline) | 1 | 183.46 | 250% | 1.50 MB/s | Ramdisk | 50 Mbps
||
| Async Pooled | 1  | 155.20 | 300% | 1.80 MB/s | SSD | 16 Mbps
| Async Pooled | 8  | 99.65  | 471% | 2.83 MB/s | SSD | 16 Mbps
||
| Async Pooled | 1  | 162.69 | 283% | 1.70 MB/s | Ramdisk | 16 Mbps 
| Async Pooled | 8  |  93.28 | 500% | 3.00 MB/s | Ramdisk | 16 Mbps 
||
| Async Pooled | 1  | 114.89 | 400% | 2.40 MB/s | Ramdisk | 50 Mbps 
| Async Pooled | 8  | 66.12  | 717% | 4.30 MB/s | Ramdisk | 50 Mbps 
| Async Pooled | 20 | 59.47  | 783% | 4.70 MB/s | Ramdisk | 50 Mbps 
||

## Remarks
During testing, periods of network inactivity were found during the install, even in the asynchronous case. This leads me to believe that for the bigger containers a higher hash and extraction time stalls the other threads. Hence even a higher speedup could be attained, however this increases complexity.

To alleviate this I would propose a splitting in work depending on the containersize. Large containers, asynchronous sequential in a single thread within a proces. Smaller containers could be processed by a group of threads within another process. For example 1 proces with 10 threads where the download time is on average 90 % of the necessary time, 1 proces with 4 threads where the download time is on average 75 percent of the time, 1 proces with 2 threads where the the download time is about half of the necessary time.



## Conclusion
We can see a speedup of about 4-5x can be attained using this approach compared to the texlive gui approach. This could transform the 3 hours and 20 minutes install time into about 40-50 minutes, without sacrificing the flexibility of the installer in comparison to the iso-based install approach.


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
                      [--n_containers N_CONTAINERS] [--reshuffle {True,False}]
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
