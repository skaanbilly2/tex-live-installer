# tex-installer-py
Texlive package install script in python


# Performance challenges
- Disk performance
- CPU 
- Network IO

To eliminate disk performance I used a ramdisk as the final destination of an extracted archive.

To see if CPU would be a bottleneck I checked the timings of network IO vs hash + extract write
In this scenario the proportion of time spent downloading was mostly in the high 90s, for big packages this could be lower.

The network IO can be solved by using non blocking io (asyncio) with the httpx client library, which allows multiple downloads to take place concurrently. To further eliminate overhead of setting up TCP connections I used the same asyncclient for all downloads, which automatically reuses the tcp socket.




# Asynchronous workers
If multiple workers are issued simultaneously, multiple downloads can take place at the same time. However all workers share the same thread and can wait for eachother if CPU is a bottleneck.
If CPU where to be a bottleneck, multiple process could be spun up with a subset of the work.



# Results
## Baseline
300 containers (randomly shuffled) Installed size 282 MB

Full install  Installed size 7,18 GB 

my experience
~= 4300 containers 3 hours 20 min  ==> 12000 seconds
==> 2.8 seconds / container
==> 0.6MB (installed size) / second


Note: from now on MB/sec will refer to installed size/sec unless indicated otherwise.

Remarks:
My internet connection during the install could do about 20Mb/second (2.5 MB/sec)



Remarks:
My internet connection used in the following experiments can do about 50Mb/second (6.5MB/sec)

## Sequential  Pooled (main_seq_pooled)
This is the baseline, should be comparable to the time for the installer

downloading took 183.46342825889587 seconds
==> 0.6 seconds / container
==> 1.5MB / second










## Async Pooled (main_async_pooled_all)
| Number of workers  |     seconds     | Speedup | Installed size/s|
|----------|:-------------:|:-------------:|------:|
| 1| 114.89 | 60%| 2.4 MB/s |
| 8 | 66.11886239051819 | 177% | 4.3 MB/s |
| 20 | 59.47248697280884 | 210%| 4.7 MB/s|


The use of asynchronous calls allows us to speedup the 

## All results
|Name| Number of workers  |     seconds     | Speedup | MB/s| Notes|
|----------|:-------------:|:-------------:|:-------------:|:-------------:|------:|
| texlive gui installer | ? | ? | ? | 0.6 MB/s | Different internet connection| 
| Sequential pooled( baseline) | 1| 183.46 | 0| 1.5 MB/| |
| Async Pooled | 1| 114.89 | 60%|2.4 MB/s | |
| Async Pooled | 8 | 66.11886239051819 | 177% |  4.3 MB/s | |
| Async Pooled  | 20 | 59.47248697280884 | 210%| 4.7 MB/s| |





