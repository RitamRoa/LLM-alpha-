Terms & Jargons & Definations

----

Defination:

   1. Transformers are core building blocks of any models like Dark Champion. Where text tokens enter and come out more with context from each transformer layer 
       --> what are transformer layer: 
               they have sub-layers: 
                      -> Self-Attention: They find the relationship between previuos tokens : For eg : Bank can be money or river 
                      -> FFN : Feed Forward Network / MLP : applies maths we know we have studied this already in 3rd semester.

     Role: Each layer builds higher-level understanding. First layers detect basic patterns (syntax); deeper layers handle complex reasoning (context, logic)

| Term      | Simple Meaning                                  | Responsibility                                                                  |
| --------- | ----------------------------------------------- | ------------------------------------------------------------------------------- |
| n_layer   | Number of transformer factory stages            | More layers = better reasoning but slower .                                     |
| n_embd    | "Width" of each token's internal representation | Wider = richer token features (like more neurons in a brain).                   |
| n_head    | Attention "spotlights" per layer                | Each head focuses on different patterns (e.g., one for grammar, one for facts). |
| n_head_kv | Attention heads for keys/values                 | Fewer here = Grouped Query Attention (GQA) to save memory/speed.                |
| n_ff      | Width of the feed-forward part                  | Bigger = more "thinking power" per layer.                                       |
| n_ctx     | Max conversation length                         | Tokens the model remembers (grows KV cache linearly). deepwiki+1​                |


Explanation: 

    1. n_alayer : No of layers to understand .... More layers more computations. starts from simple to complex. 
    2. n_embd   : shows the size of the vector which it was given, meaning like is this related to that or not... is the word "bank" related to finance or not. tokens higher then wider and richer words but more ram.
    3. n_head   : This will tell how multi area the search needs to be "nulti-aspect awareness".
    4. nheads_kv: basically lets say it is 24 (n_head) and then if your nheads_kv = 3 then 24/8=3 meaning the whole thing is divided into 3 groups of each 
                       Every attention head (24 total in your model) has 3 jobs:

                       Query (Q): "What do I need?" (asker).
                       Key (K): "Who matches?" (search index).
                       Value (V): "Relevant info." (actual content).
                       n_head = 24: 24 full sets of (Q+K+V) workers → diverse focus.
                       n_head_kv = 8: Only 8 unique (K+V) note‑sets made.

Head1: Q1 + K1V1
Head2: Q2 + K2V2  ← 24 separate notebooks!
...
Head24: Q24 + K24V24

Group1 KV: K1V1  ← Shared by Q1,Q2,Q3
Group2 KV: K2V2  ← Shared by Q4,Q5,Q6
...
Group8 KV: K8V8  ← Shared by Q22,Q23,Q24

      5. n_ff   : Feed-Forward-> more "intelligent" it seems. 
      6. n_ctx  : active tokens. 
