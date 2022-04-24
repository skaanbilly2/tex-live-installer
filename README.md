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





