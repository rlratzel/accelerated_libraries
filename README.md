# Accelerated Libraries Examples
* See `download_datsets.sh` to download the datasets used in these examples.
* To use Accelerated NetworkX (the `nx-cugraph` NetworkX backend) install `nx-cugraph` then set the following env var like this: `NETWORKX_AUTOMATIC_BACKENDS=cugraph`
* To use Accelerated Pandas (the `cudf.pandas` module) install `cudf` and run scripts using the `cudf.pandas` module like this: `python -m cudf.pandas my_script.py`
* This example uses both Accelerated Pandas and Accelerated NetworkX on the `bc_citpatents.py` example:
  * `NETWORKX_AUTOMATIC_BACKENDS=cugraph python -m cudf.pandas bc_citpatents.py`

# Results
## Pandas + Accelerated NetworkX
* As `k` increases, BC runtime using `nx-cugraph` really only starts to
  increase at k=10000. This is definitely not the case for standard NetworkX
  (see below).
* The number of central nodes (the bin containing the upper-half of the scores)
  increases as k increases, but since this is an approximation, sometimes
  increases do not always result in more accuracy as seen below in k=1000
  vs. k=10000.  k needs to increase significantly before this is generally
  true.  Ideally shortests paths between all pairs are computed, but this is
  computationally prohibitive.
* Other runs using the same k values result in more or less nodes in each bin.
  Generally the highest k value one can afford should be used.

```
(base) root@45e3c021531c:/Projects/accelerated_libraries# time NETWORKX_AUTOMATIC_BACKENDS=cugraph python bc_citpatents_multik_timings.py
read_csv:               1.861s
from_pandas_edgelist:   51.57s

--------
k=10
betweenness_centrality: 13.34s
to DataFrame:           1.623s

groupby:                0.06115s
bc
(-0.001, 3.87e-06]      3774765
(3.87e-06, 7.74e-06]          3
Name: node, dtype: int64

--------
k=100
betweenness_centrality: 11.25s
to DataFrame:           1.603s

groupby:                0.05179s
bc
(-0.001, 2.77e-05]      3774765
(2.77e-05, 5.53e-05]          3
Name: node, dtype: int64

--------
k=1000
betweenness_centrality: 23.0s
to DataFrame:           1.577s

groupby:                0.04587s
bc
(-0.001, 4.3e-06]      3774758
(4.3e-06, 8.61e-06]         10
Name: node, dtype: int64

--------
k=10000
betweenness_centrality: 136.2s
to DataFrame:           1.556s

groupby:                0.05284s
bc
(-0.001, 1.5e-06]      3774765
(1.5e-06, 3.01e-06]          3
Name: node, dtype: int64

real    4m15.086s
user    3m26.450s
sys     0m48.555s
```

## Accelerated Pandas + Accelerated NetworkX
* Accelerated Pandas results in 10X faster `groupby` calls.
* For some reason, the overall runtime is slightly slower though. This was
  observed consistently.

```
(base) root@45e3c021531c:/Projects/accelerated_libraries# time NETWORKX_AUTOMATIC_BACKENDS=cugraph python -m cudf.pandas bc_citpatents_multik_timings.py
read_csv:               1.838s
from_pandas_edgelist:   47.8s

--------
k=10
betweenness_centrality: 24.86s
to DataFrame:           1.641s

groupby:                0.004354s
(-0.001, 0.0]    3774766
(0.0, 0.001]           2
Name: node, dtype: int64

--------
k=100
betweenness_centrality: 11.32s
to DataFrame:           1.646s

groupby:                0.003568s
(-0.001, 0.0]    3774765
(0.0, 0.0]             3
Name: node, dtype: int64

--------
k=1000
betweenness_centrality: 23.1s
to DataFrame:           1.722s

groupby:                0.003534s
(-0.001, 0.0]    3774760
(0.0, 0.0]             8
Name: node, dtype: int64

--------
k=10000
betweenness_centrality: 136.8s
to DataFrame:           1.643s

groupby:                0.003476s
(-0.001, 0.0]    3774766
(0.0, 0.0]             2
Name: node, dtype: int64

real    4m28.525s
user    3m39.932s
sys     0m50.578s
```

## Pandas + NetworkX (no accelerated libraries used)
* NetworkX was too slow to complete anyting with k>100 in a reasonable time and
  was killed.

```
(base) root@45e3c021531c:/Projects/accelerated_libraries# time python bc_citpatents_multik_timings.py
read_csv:               1.83s
from_pandas_edgelist:   51.49s

--------
k=10
betweenness_centrality: 103.9s
to DataFrame:           1.611s

groupby:                0.04431s
bc
(-0.001, 1.74e-05]      3774762
(1.74e-05, 3.47e-05]          6
Name: node, dtype: int64

--------
k=100
betweenness_centrality: 1.014e+03s
to DataFrame:           1.607s

groupby:                0.04396s
bc
(-0.001, 1.27e-05]      3774765
(1.27e-05, 2.54e-05]          3
Name: node, dtype: int64

--------
k=1000
^C^CTraceback (most recent call last):
  File "/Projects/accelerated_libraries/bc_citpatents_multik_timings.py", line 23, in <module>
    bc_values_dict = nx.betweenness_centrality(G, k=k)
  File "<class 'networkx.utils.decorators.argmap'> compilation 8", line 4, in argmap_betweenness_centrality_5
  File "/opt/conda/lib/python3.10/site-packages/networkx/utils/backends.py", line 576, in __call__
    return self.orig_func(*args, **kwargs)
  File "/opt/conda/lib/python3.10/site-packages/networkx/algorithms/centrality/betweenness.py", line 136, in betweenness_centrality
    S, P, sigma, _ = _single_source_shortest_path_basic(G, s)
  File "/opt/conda/lib/python3.10/site-packages/networkx/algorithms/centrality/betweenness.py", line 259, in _single_source_shortest_path_basic
    P[v] = []
KeyboardInterrupt
^C

real    76m12.158s
user    74m30.520s
sys     1m41.331s
```
