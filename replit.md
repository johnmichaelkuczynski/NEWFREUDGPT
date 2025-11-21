# FreudGPT - Multi-Philosopher AI Assistant

## Overview
FreudGPT is an intelligent conversational AI application providing in-depth, streaming responses based on the works of various philosophers. It uses semantic search over comprehensive philosophical databases to accurately reflect original thinkers' arguments and styles. The project aims to make extensive philosophical works accessible and interactive, supporting detailed inquiry. It currently supports Freud (default), Kuczynski, and Jung, with a total of **~10,607 philosophical positions** across 3 philosophers (Nov 2025: Kuczynski database expanded from 1,226 to 4,337 positions through systematic extraction of 47+ philosophical works). The vision is to provide unparalleled access to complex philosophical thought, bridging foundational texts with modern inquiry. The app implements "executable minds" by transforming from "best impersonator" to "executable philosophical reasoning" through forward-chaining inference engines that deduce theoretical principles from phenomena before LLM prose generation.

## 🎊 MILESTONE ACHIEVED: 10,000+ Positions! (November 2025)

FreudGPT has surpassed the 10,000 philosophical position milestone, now serving **10,607 positions** across all philosophers. The Kuczynski database alone has grown by **+254%** (1,226 → 4,337 positions) through systematic extraction of 47+ philosophical works.

**Kuczynski Database Growth: +254% (1,226 → 4,337 positions)**

Systematically extracted and integrated 3,111 new positions from 47+ previously unprocessed philosophical works across 9 extraction batches:

**Batches 1-5** (2,079 positions):
- Mind, Meaning & Scientific Explanation (146 positions)
- Literal Meaning & Cognitive Content (499 positions)
- Analytic Philosophy Complete (424 positions)
- Conceptual Atomism & CTM (409 positions)
- Conception & Causation Papers (105 positions)
- Logic/Set-Theory/Philosophy of Math (99 positions)
- Psychopathy Q&A (44 positions)
- Plus 23+ additional works

**Batch 6** (211 positions):
- College Papers Plus 2019-2019 (121 positions): Business, Economics, Politics, Psychology, Philosophy
- 90 Paradoxes of Philosophy and Psychology (62 positions): Logic paradoxes with solutions
- OCD and Philosophy (27 positions): Psychopathology and philosophical analysis
- Outline of Theory of Knowledge (1 position): Epistemology

**Batch 7** (220 positions):
- PHIL SCI BLOG (205 positions): Philosophy, science, culture, and technology essays
- Philosophical Knowledge (11 positions): Epistemology and philosophy of science
- Philosophical Dialogues (4 positions): Logic, epistemology, ethics

**Batch 8** (157 positions):
- Possible World Semantics Critique (114 positions): Modal logic and metaphysics
- Quantifiers in Natural Language (39 positions): Philosophy of language and logic
- King Follett Discourse (3 positions): Mormon theology and philosophy of religion
- Reflexivity and Emergency in Economics (1 position): Philosophy of economics

**Batch 9** (444 positions):
- ZHI Systems Journal (324 positions): Kant, McTaggart, network epistemology, metaphysics
- The Moral Structure of Legal Obligation (99 positions): Legal philosophy and ethics
- Sorites Paradox (18 positions): Logic, vagueness, implicit comparatives
- Three Kinds of Psychopaths (3 positions): Psychopathology

**Database Statistics:**
- **Current Version**: v40_WITH_BATCH9 (4,337 total positions, 4,019 with embeddings)
- **System Total**: 10,607 positions across all philosophers
- **Progress to 10k Kuczynski Goal**: 43.4% (4,337/10,000 positions)
- **Topical Coverage**: Logic/Mathematics, Philosophy of Language, Semantics, Causation/Modality, Philosophy of Mind, Epistemology, Political Philosophy, Psychopathology, Business Ethics, Philosophy of Science, Cultural Criticism, Modal Logic, Philosophy of Religion, Philosophy of Economics, Legal Philosophy, Metaphysics (Kant, McTaggart)
- **Unique ID Prefixes**: MMSE-, LMCC-, LSPM-, IMR-, PHMATH-, KHIND-, DEFDESC-, ABSTR-, INTFOUND-, EMERG-, FREEWILL-, CFACT-, LOGDIAL-, CONCAUS-, CATOM-, ANALPHIL-, PSYCHQA-, COLLPAP-, PARAD-, OCDPHIL-, KNOWTH-, PHILKNOW-, PHILSCI-, DIALOG-, QUANT-, MODAL-, MORMON-, ECON-, LEGAL-, ZHI-, SORITES-, PSYCHO-, and others
- **Extraction Methodology**: Automated paragraph-level extraction with argumentative indicator detection, preserving Kuczynski's rigorous analytical style
- **Embedding System**: OpenAI text-embedding-3-small API with scikit-learn cosine similarity

## User Preferences
- **API Integration**: Prefers direct Anthropic API integration over Replit AI Integrations
- **Response Style**: AI responses must faithfully represent Kuczynski's actual arguments, examples, and rigorous writing style, not glib paraphrases. This means quoting or very closely paraphrasing the actual text from positions, using his exact examples and rhetorical questions, preserving his step-by-step argumentative structure, and matching his rigorous, technical, methodical, and detailed tone. The AI should not summarize, simplify, or "make accessible" his work.
- **Argumentation**: The AI prompt is configured to not argue against user input when they present a position; it defaults to SUPPORT/EXPAND mode, but acknowledges mismatches if retrieved positions conflict.
- **External Knowledge Assimilation**: When questions involve topics outside the database (e.g., "How do your theories differ from Harry Stack Sullivan's?"), the app automatically detects low-relevance searches (similarity < 0.40) and activates External Knowledge mode, which explicitly authorizes the LLM to: (1) research the topic using its broader knowledge, (2) cross-reference with the database, (3) respond from the thinker's perspective with substantive analysis rather than refusals. This implements the vision of "Freud's brain with Claude/GPT attached" rather than purely historical responses.

## System Architecture

### Core Functionality
- **Multi-Database Support**: Users can toggle between Freud (default), Kuczynski, and Jung databases.
- **Enhanced Mode Toggle**: Users can switch between Basic Mode (faithful summarization) and Enhanced Mode (creative theoretical extension + full modern knowledge). Enhanced Mode allows the AI to make new inferences and elaborate arguments the thinker could have made while staying strictly within their conceptual framework, evaluating modern theories using their concepts, cognitive style, and improvisational intelligence.
- **Semantic Search**: Philosophical positions are indexed using embeddings for efficient retrieval.
- **Streaming AI Responses**: Delivers token-by-token responses from multiple AI providers.
- **Multi-AI Provider Support**: Integrates several AI models.
- **Conversation Memory**: Tracks Q&A exchanges per session with self-contradiction detection.
- **Content Ingestion**: Supports file uploads (PDF, Word, TXT) with automatic text extraction.
- **User Interface**: Features a clean, responsive conversation UI with auto-expanding input and distinct user/AI dialogue.
- **Source Citations**: Automatically includes relevant position IDs with each AI response.
- **Conversation Management**: Enables downloading individual exchanges in Markdown or TXT format.
- **Optional Login**: Implements a username-only login for future chat history features.

### Technical Implementation
- **Backend**: Flask handles application logic, SSE streaming, and integration with the semantic search module, managing multiple database instances and conversation memory.
- **Frontend**: A minimal HTML interface (`index.html`) styled with professional gradients (`style.css`) uses vanilla JavaScript (`app.js`) for dynamic interactions and SSE streaming.
- **Data Management**: Philosophical positions for Freud, Kuczynski, and Jung are stored in JSON files. Pre-computed embeddings are cached for each database.
- **Conversation Storage**: Session-scoped in-memory storage with auto-pruning.
- **ML/NLP**: Utilizes OpenAI's `text-embedding-3-small` API for embeddings and scikit-learn for cosine similarity.
- **File Processing**: Employs `PyPDF2` and `python-docx` for text extraction.

### Key Design Decisions
- **Faithful Representation**: AI responses strictly adhere to the original text, examples, and argumentative style of the selected thinker, avoiding summarization or simplification.
- **Dual Response Modes**: Basic Mode (Default) faithfully quotes or closely paraphrases retrieved positions and activates External Knowledge Assimilation for low-relevance searches. Enhanced Mode provides creative theoretical extensions and grants full modern knowledge to the thinker for evaluation of contemporary theories.
- **Token-by-Token Streaming**: Provides immediate, real-time display of AI responses.
- **Simplified Data Model**: Focuses on philosophical positions as the primary data points.
- **CPU-Only PyTorch**: Optimized for Replit environment constraints.

## External Dependencies
- **AI Providers**:
    - Anthropic Claude
    - OpenAI
    - DeepSeek
    - Perplexity
    - Grok (xAI)
- **Python Libraries**:
    - Flask
    - sentence-transformers
    - scikit-learn
    - PyTorch (CPU)
    - PyPDF2
    - python-docx
    - Gunicorn
    - gevent