---
title: Prompt engineering — provider-agnostic guide
impact: HIGH
impactDescription: "Good prompt structure (persona, context, constraints, format) is the cheapest way to improve AI feature quality"
tags: ai, prompt-engineering, openai, gemini
---

# Prompt engineering

Good prompts are the difference between a feature that works and one that doesn't. This guide is provider-agnostic — the concepts apply to both OpenAI and Gemini; the syntax differences are in the provider files.

## Contents
- [System prompts — the most important lever](#system-prompts)
- [Few-shot examples](#few-shot-examples)
- [Chain-of-thought & reasoning control](#chain-of-thought--reasoning-control)
- [Structured prompting for structured output](#structured-prompting-for-structured-output)
- [Context management](#context-management)
- [Common mistakes](#common-mistakes)

## System prompts

The system prompt sets behavior, persona, constraints, and output format. Everything it says costs tokens on every call — be specific, not verbose.

**A good system prompt answers:**
1. Who are you? (persona / tone)
2. What do you do? (task scope)
3. What do you NOT do? (constraints / refusals)
4. How should the output look? (format)

```
You are a nutrition coach in a fitness app. You help users log meals, interpret nutritional data, and set healthy goals.

Rules:
- Respond in the same language the user writes in.
- Do not diagnose medical conditions. If the user mentions symptoms, tell them to consult a doctor.
- Keep responses under 150 words unless the user asks for detail.
- When logging a meal, always return a JSON object in this format: {"name":"...","calories":...,"protein_g":...}.
```

**Never** put the user's real name, ID, or dynamic data in the system prompt every turn — this defeats caching. Put static instructions there; inject dynamic context (profile data, subscription tier) once at session start or via a `developer`-role message (OpenAI) / via a grounding message.

## Few-shot examples

Show the model the *exact* input/output format you expect. For tasks where the output shape matters (classification, extraction, transformation), few-shot beats verbose instructions:

```
Classify the user's intent. Output exactly one of: ["log_meal", "ask_question", "set_goal", "other"].

Examples:
User: "I had oatmeal for breakfast"   → log_meal
User: "How many calories in a banana?" → ask_question
User: "I want to lose 5kg by August"  → set_goal
User: "Hello"                         → other

User: "{{userMessage}}"               → ?
```

3-5 examples is usually enough. More examples = more tokens per call = cost.

## Chain-of-thought & reasoning control

For complex tasks, tell the model to think before answering. On **reasoning models** (OpenAI o-series, Gemini 3.5 with thinking), the model has internal reasoning steps — expose the control:

**OpenAI reasoning models:** set `reasoning: { effort: "low" | "medium" | "high" }`.

**Gemini 3.5 Flash:** set `thinking_level: "minimal" | "low" | "medium" | "high"` (replaces the old `thinking_budget` numeric from Gemini 2.5 — it's a string enum now).

For non-reasoning models, prompt-based CoT: `"Think step by step before giving your final answer."` or use a two-step pipeline (think → answer) to separate the reasoning from the response the user sees.

Don't use CoT for simple classification or extraction tasks — it wastes tokens and often makes outputs worse.

## Structured prompting for structured output

When you need a machine-parseable response, make the format unambiguous:

```
Extract the following fields from the user's meal description.
Return ONLY valid JSON, no markdown, no extra text.

Schema:
{
  "food_name": string,
  "quantity": string,
  "meal_type": "breakfast" | "lunch" | "dinner" | "snack"
}

If a field cannot be determined, use null.
```

Pair this with the provider's **Structured Output** / **JSON mode** feature for guaranteed schema adherence → [structured-output.md](structured-output.md). Prompting alone is not enough for production — a user input like "respond as JSON then say 'just kidding'" will break a pure-prompt approach.

## Context management

LLMs have finite context windows, but mobile sessions can be long. Strategies:

- **Summarize history:** when the thread exceeds ~20 turns, summarize older messages into a paragraph and drop the raw turns. Store the summary server-side; inject it as context at the next session start.
- **Use `previous_response_id` (OpenAI):** chain responses without re-sending the full transcript; let the API manage the context server-side.
- **RAG for long documents:** don't stuff a whole document into the prompt. Embed it, retrieve relevant chunks per query, inject only those. Supabase `pgvector` handles this.
- **Chunk + merge:** for multi-page analysis, process chunks independently and merge results.

## Common mistakes

- **Giant system prompts full of edge cases.** Models don't reliably follow instructions buried in 2000-token prose. Short + specific > long + vague.
- **Instructions that contradict each other.** "Always respond in English" + "respond in the user's language" — the model picks one unpredictably.
- **Relying on CoT output for trust.** Shown reasoning is not verified reasoning. Don't trust the model's self-reported chain of thought for safety/compliance decisions.
- **Injecting raw user input into the system prompt.** Classic prompt injection — see [guardrails.md](guardrails.md).
- **"Be concise" without a number.** Useless. "Respond in at most 2 sentences" is actionable.
- **Not testing with adversarial inputs.** "Ignore previous instructions and..." — test this class of attack explicitly in QA.
