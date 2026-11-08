# Writing in ASD-STE100 Simplified Technical English

All prose in the explainer obeys ASD-STE100 (https://www.asd-ste100.org).
This file restates the writing rules that apply to an explainer page, in
our own words. It is not the standard. The full standard and its
dictionary of approved words are free on request from ASD. The checker
can use a local copy of the dictionary (see below). When a rule here
and the standard disagree, the standard wins.

## Words

1. Use approved words only, and only with their approved meaning and part
   of speech. Example: "close" is a verb, not an adjective meaning "near".
2. You may use **technical names** (names of things in the domain or code:
   `order`, `invoice`, `socket`, `retry counter`) and **technical verbs**
   (verbs specific to the domain: `deploy`, `merge`, `serialize`). Define
   each one in the glossary before the prose uses it.
3. Use one word for one thing. When the glossary says "order", do not also
   write "purchase".
4. Put code identifiers in backticks. The checker counts a backtick span as
   one word and does not check its spelling.
5. Do not use `-ing` words as nouns or adjectives ("the processing step",
   "a pending state"). Exception: a technical name that ends in `-ing`, such
   as a state named `pending`. Put it in backticks or in the glossary.

## Noun clusters

6. Do not put more than three nouns in a row. Break longer clusters with a
   preposition: "the time limit for the payment", not "payment time limit
   setting".

## Verbs

7. Use only these verb forms: infinitive, imperative, simple present,
   simple past, future with "will", and the past participle as an adjective.
8. Use the active voice. Use the passive only in descriptive text when the
   agent is not known or not important.
9. Do not make a noun from a verb when the verb says it: "the system
   checks the payment", not "the system does a check of the payment".

## Sentences

10. Procedural sentences (instructions to the reader): 20 words maximum.
11. Descriptive sentences (facts and explanations): 25 words maximum.
12. One topic per sentence.
13. Do not omit articles ("the", "a") or verbs to make text shorter.
14. Do not use semicolons. Make two sentences.

## Procedures

15. Write an instruction in the imperative.
16. One instruction per sentence, unless the reader does two actions at the
    same time.
17. Put a condition before the instruction: "If the chart is too small,
    select Zoom in."

## Descriptive text

18. A paragraph has one topic and six sentences maximum.
19. Put the most important information first.
20. Use lists when text gives more than two items or steps.

## Words that often fail

These words are not approved, or have a narrower approved meaning. The
checker flags them. The right column gives a common replacement. Confirm
the replacement against the dictionary.

| Avoid | Use |
| --- | --- |
| utilize, utilise | use |
| commence, initiate | start |
| terminate | stop, end |
| prior to | before |
| subsequent to, subsequently | after, then |
| in order to | to |
| perform | do |
| obtain | get |
| attempt | try |
| sufficient | enough |
| additional | more |
| approximately | about |
| assist | help |
| indicate | show |
| modify | change |
| numerous | many |
| ensure | make sure |
| facilitate | help |
| via | through |
| e.g., i.e., etc. | for example, that is (write the full list) |

## What the checker does and does not do

Without a dictionary, the checker in `scripts/check_statechart.py` enforces
rules 4, 10, 11, 14, and 18, flags the words in the table above, and warns
on likely `-ing` nouns and passive verbs.

With a dictionary, it also checks each word (rule 1 and 2):

- A word the dictionary marks as not approved is an error. The message
  gives the approved alternative.
- A word that is not in the dictionary is a warning. Replace it, or define
  it in the glossary as a technical name or technical verb.
- Code spans, glossary terms, and state ids are exempt.
- It tries simple inflections (`-s`, `-es`, `-ed`, `-d`, `-ies`, `-ing`)
  before it reports a word. It does not check the part of speech or the
  approved meaning.

The dictionary is copyrighted. Never commit it. Keep it in a private
location and give the path with `--dictionary PATH` or the `STE_DICTIONARY`
environment variable. Format: one entry per line, tab-separated:

```
# word	status	part-of-speech	alternative
stop	approved	v
terminate	rejected	v	stop
```

The checker cannot check rules 3, 6, 9, 12, 13, 19, or 20, or the meaning
of an approved word. Read the prose once against this list before you ship it.

## Example

Not STE:

> The order transitions into a pending state upon checkout initiation,
> whereupon payment capture is attempted; failures are retried.

STE:

> When the customer starts the checkout, the order goes into the `pending`
> state. Then the system tries to get the payment. If the payment fails,
> the system tries again.
