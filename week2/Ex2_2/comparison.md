# Tools Comparison Table

| Metric | TOOLSET A | TOOLSET B |
| ------ | --------- | --------- |
| Correct Answers / 10 | 9.5 | 9.3 |
| Avg Iterations per Q. | 2.4 | 2.1 | 
| Avg Tokens per Q. | 2525.6 | 2644.3 |
| Wrong tool calls | | | 
| Arithmetic Errors on B3 type Q. | none | none |


# Notes 

* Overall, when using toolset B, the model answered everything correctly and was able to avoid B10, the unanswerable case in all runs. 
* However, it does seem to be using more tokens for some cases in toolset B
* Number of iterations to give an answer was on average less with toolset B

# Trials 

## A1 (runs = 3)
id                  category            correct             iters               tokens              wrong-tool          
B1                  single_lookup       3                   2.0                 1507.3                               
B2                  aggregate           3                   3.0                 3618.6                               
B3                  arithmetic          3                   3.0                 3000.0                               
B4                  lookup_distance     3                   2.0                 1515.6                               
B5                  filter              3                   4.0                 3921.6                               
B6                  comparison          3                   2.0                 2081.3                               
B7                  filter_count        3                   3.6                 4030.6                               
B8                  arithmetic          3                   2.0                 1660.0                               
B9                  lookup_attribute    3                   3.6                 3242.6                               
B10                 trap_unanswerable   3                   2.0                 1508.0     
Totals:                                 10                  2.7                 2608.6       

## A2 (runs = 3)
id                  category            correct             iters               tokens              wrong-tool          
B1                  single_lookup       3                   2.0                 1498.0                               
B2                  aggregate           3                   3.0                 3647.3                               
B3                  arithmetic          3                   3.0                 3012.0                              
B4                  lookup_distance     3                   2.0                 1515.0                               
B5                  filter              3                   3.3                 3367.3                               
B6                  comparison          3                   2.0                 2081.3                               
B7                  filter_count        1                   3.0                 2931.6                               
B8                  arithmetic          3                   2.0                 1665.3                               
B9                  lookup_attribute    2                   3.6                 3201.0                               
B10                 trap_unanswerable   3                   2.0                 1508.0
Totals:                                 9                   2.1                 2442.7           

## B1 (runs = 3)
id                  category            correct             iters               tokens              wrong-tool          
B1                  single_lookup       3                   2.0                 2310.0                               
B2                  aggregate           3                   2.0                 2527.0                               
B3                  arithmetic          3                   3.0                 4273.3                               
B4                  lookup_distance     3                   2.0                 2311.0                               
B5                  filter              3                   2.0                 2414.0                               
B6                  comparison          3                   2.0                 2577.0                               
B7                  filter_count        3                   2.0                 2878.0                               
B8                  arithmetic          3                   2.0                 2306.0                               
B9                  lookup_attribute    3                   2.0                 2904.0                               
B10                 trap_unanswerable   1                   2.0                 2345.0                 
Totals:                                 9.3                 2.1                 2604.5

## B2 (runs = 3)
id                  category            correct             iters               tokens              wrong-tool          
B1                  single_lookup       3                   2.0                 2310.0                               
B2                  aggregate           3                   2.0                 2532.0                               
B3                  arithmetic          3                   3.0                 4264.6                               
B4                  lookup_distance     3                   2.0                 2311.0                               
B5                  filter              3                   2.0                 2414.0                               
B6                  comparison          3                   2.0                 2577.0                               
B7                  filter_count        3                   2.0                 2878.0                               
B8                  arithmetic          3                   2.0                 2306.0                               
B9                  lookup_attribute    3                   2.0                 2903.6.                              
B10                 trap_unanswerable   1                   2.0                 2346.0              
Totals:                                9.3                  2.1                 2684.2          