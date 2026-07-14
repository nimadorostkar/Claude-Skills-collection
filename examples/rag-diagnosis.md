# Fixing a RAG system

**Skills loaded:** `rag`, then `llm-evaluation`
**Outcome:** The prompt was never the problem

---

## The request

> Our RAG system keeps hallucinating. It gives confident answers that aren't in the docs. We've rewritten the prompt four times. What else can we try?

## Without the skills

The obvious response is to help with the prompt: add "only answer from the provided context", add "say I don't know if the context is insufficient", lower the temperature, add few-shot examples of refusal.

All reasonable. All addressing 6% of the problem, as it turns out.

## What the skills changed

`rag` opens with a rule that redirects the entire investigation:

> **Evaluate retrieval separately** — before touching the prompt. If the correct passage is not in the top-k, no amount of prompt engineering will produce a correct answer. Measure recall@k first.

And in `Best Practices`:

> Most "the LLM hallucinated" complaints in RAG systems are retrieval failures. The model answered from its parameters because the context did not contain the answer.

## The session

**Agent:** Before we touch the prompt again — has retrieval been measured?

Specifically: for the questions it gets wrong, is the correct passage in the retrieved context at all? If it is not, the model is not hallucinating in any interesting sense. It is answering from its parameters because you handed it nothing to answer from, and a fifth prompt rewrite will change nothing.

Do you have a set of questions with known-correct answers, and can you identify which chunks contain those answers?

**User:** We have about 100 questions from support tickets with the right answers. We haven't mapped them to chunks.

**Agent:** That mapping is the whole diagnostic. It takes an hour and it will tell you which of two completely different problems you have.

```python
retrieval_failures = 0
generation_failures = 0

for case in eval_set:
    retrieved = retrieve(case.question)
    retrieved_ids = {c.id for c in retrieved}

    if not (case.gold_chunk_ids & retrieved_ids):
        retrieval_failures += 1        # the answer was never in the context
    else:
        answer = generate(case.question, retrieved)
        if not matches(answer, case.gold_answer):
            generation_failures += 1   # it was there and the model missed it
```

**User:**

```
RETRIEVAL_FAILURE:  31 / 100
GENERATION_FAILURE:  6 / 100
```

**Agent:** There it is. 31 of the 37 failures are retrieval. The prompt is responsible for 6.

Four prompt rewrites addressed at most 6% of the problem. Fix retrieval.

Looking at the 31 failures — what is the chunking strategy?

**User:** Fixed 512-token chunks, no overlap. Dense embeddings, top-5.

**Agent:** Three problems, in order of impact:

1. **Fixed-size chunking with no overlap.** A fact that spans a boundary is destroyed — half of it is in one chunk, half in another, and neither is retrievable. Chunk on semantic boundaries (sections, paragraphs) with 10–15% overlap.

2. **No sparse retrieval.** Dense embeddings find semantic matches. They are poor at exact terms — error codes, product names, version numbers. Support questions are *full* of these. Add BM25 and fuse the rankings.

3. **No reranking.** You retrieve 5 and pass 5. Retrieve 50, rerank with a cross-encoder, pass the top 5. A cross-encoder sees the query and the passage together, which a bi-encoder embedding structurally cannot. This is usually the single largest improvement available to a naive pipeline.

One more, which is the most common cause of retrieval failure in support corpora: **your chunks are unretrievable in isolation.** A chunk that reads "It expires after 30 days and cannot be renewed" has no way to be matched against "how long does an API key last" — the word "key" does not appear in it. Prepend the document title and section heading to each chunk before embedding.

**User** *(one week later)*:

```
RETRIEVAL_FAILURE:   4 / 100      (was 31)
GENERATION_FAILURE:  5 / 100      (was 6)
```

Overlap + hybrid + reranking + contextual headers. We haven't touched the prompt.

**Agent:** 37 failures down to 9, and the prompt is untouched.

Now the prompt is worth looking at — those 5 generation failures are real, and they are the ones a grounding instruction and an explicit permission to refuse will address. That work is now worth doing, because it is 5% of the problem rather than 6% of a problem you were treating as 100%.

---

## What the skills contributed

| Step | Skill | The rule that fired |
| --- | --- | --- |
| Refused to touch the prompt | `rag` | *Evaluate retrieval separately — before touching the prompt.* |
| Split the failures by component | `rag` | *For each wrong answer: was the right passage retrieved? These have completely different fixes.* |
| Diagnosed chunking | `rag` | *Fixed-size chunking splits a table in half. Add overlap so a fact spanning a boundary is not lost.* |
| Added hybrid retrieval | `rag` | *Dense finds semantic matches; BM25 finds exact terms, product codes, and names.* |
| Added reranking | `rag` | *Reranking is the single highest-value addition to a naive RAG pipeline.* |
| Contextual chunk headers | `rag` | *A chunk that reads "It expires after 30 days" is unretrievable without knowing what "it" is.* |
| Built the eval set first | `llm-evaluation` | *A prompt engineer without an evaluation set is guessing with extra confidence.* |

The team had spent four rounds of iteration on the component responsible for one-sixth of the failures. The diagnostic that redirected them took an hour.
