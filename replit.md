# FreudGPT - Multi-Philosopher AI Assistant

## Overview
FreudGPT is an intelligent conversational AI application designed to provide in-depth, streaming responses based on the works of various philosophers. It leverages semantic search over comprehensive philosophical databases to accurately reflect the original thinkers' arguments and styles. The project aims to make extensive philosophical works accessible and interactive, supporting detailed inquiry. It currently supports Freud (default) and Kuczynski, with a total of **7,249 philosophical positions** (3,792 Freud Primary + 2,328 Freud Extended + 271 Freud Complete Works Extraction + 858 Kuczynski). The overarching vision is to provide unparalleled access to complex philosophical thought, bridging foundational texts with modern inquiry to expand intellectual discourse and understanding.

## User Preferences
- **API Integration**: Prefers direct Anthropic API integration over Replit AI Integrations
- **Response Style**: AI responses must faithfully represent Kuczynski's actual arguments, examples, and rigorous writing style, not glib paraphrases. This means quoting or very closely paraphrasing the actual text from positions, using his exact examples and rhetorical questions, preserving his step-by-step argumentative structure, and matching his rigorous, technical, methodical, and detailed tone. The AI should not summarize, simplify, or "make accessible" his work.
- **Argumentation**: The AI prompt is configured to not argue against user input when they present a position; it defaults to SUPPORT/EXPAND mode, but acknowledges mismatches if retrieved positions conflict.
- **External Knowledge Assimilation**: When questions involve topics outside the database (e.g., "How do your theories differ from Harry Stack Sullivan's?"), the app automatically detects low-relevance searches (similarity < 0.40) and activates External Knowledge mode, which explicitly authorizes the LLM to: (1) research the topic using its broader knowledge, (2) cross-reference with the database, (3) respond from the thinker's perspective with substantive analysis rather than refusals. This implements the vision of "Freud's brain with Claude/GPT attached" rather than purely historical responses.

## System Architecture

### Core Functionality
- **Multi-Database Support**: Users can toggle between Freud (default) and Kuczynski databases.
- **Enhanced Mode Toggle**: Users can switch between Basic Mode (faithful summarization) and Enhanced Mode (creative theoretical extension + full modern knowledge). Enhanced Mode allows the AI to make new inferences and elaborate arguments the thinker could have made while staying strictly within their conceptual framework. In Enhanced Mode, Freud/Kuczynski have FULL KNOWLEDGE of all modern theories and thinkers (e.g., Otto Kernberg, Carl Rogers, Tony Robbins, Albert Bandura, attachment theory, etc.). They evaluate modern theories using: (1) direct Freudian/Kuczynskian concepts where applicable, (2) their cognitive style and interpretive instincts where concepts don't directly map, (3) improvisational theoretical intelligence for topics requiring fresh analysis. This implements "Freud's brain with Claude/GPT attached" at maximum capacity.
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
- **Data Management**: Philosophical positions for Kuczynski and Freud are stored in JSON files:
  - FREUD_DATABASE.json: 3,792 positions (Primary collection)
  - FREUD_DATABASE_v9.json: 2,328 positions (Extended collection)
  - FREUD_DATABASE_v10.json: 271 positions (Complete Works extraction from Parts 1-20)
  - KUCZYNSKI_PHILOSOPHICAL_DATABASE_v29_BLOG_SET2_COMPLETE.json: 858 positions
  - Pre-computed embeddings are cached for each database. Full source texts for Freud's works are available in `texts/freud/`.
- **Conversation Storage**: Session-scoped in-memory storage with auto-pruning.
- **ML/NLP**: Utilizes OpenAI's `text-embedding-3-small` API for embeddings and scikit-learn for cosine similarity.
- **File Processing**: Employs `PyPDF2` and `python-docx` for text extraction.

### Key Design Decisions
- **Faithful Representation**: AI responses strictly adhere to the original text, examples, and argumentative style of the selected thinker, avoiding summarization or simplification.
- **Dual Response Modes**:
  - **Basic Mode (Default)**: Faithfully quotes or closely paraphrases retrieved positions, preserving exact examples, rhetorical questions, and argumentative structure. Activates External Knowledge Assimilation when questions involve topics outside the database (similarity < 0.40).
  - **Enhanced Mode**: Provides creative theoretical extensions that the thinker could have written. Grants FULL MODERN KNOWLEDGE - the thinker knows all contemporary theories and can evaluate them using their conceptual framework, cognitive style, and improvisational intelligence. Examples: Freud can analyze Otto Kernberg's borderline theory, critique Carl Rogers' person-centered therapy, or evaluate Tony Robbins using psychoanalytic principles. Never says "I am not familiar with..." - always engages substantively with any topic.
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
## Database Status

### Freud Database Progress
- **Part 1-10**: 1,029 positions (FREUD-0001 to FREUD-1029) covering 1893-1919
- **Part 11**: 60 positions (FREUD-1030 to FREUD-1089) added November 2025
  - Source: Introductory Lectures on Psycho-Analysis, Lectures XXV-XXVIII (1916-1917)
  - Coverage: Anxiety theory, libido theory, narcissism, transference, analytic therapy
  - Final lectures synthesizing core psychoanalytic theory through 1917
- **Part 12**: 351 positions (FREUD-1090 to FREUD-1440) added November 2025
  - Source: Introductory Lectures on Psycho-Analysis, Lectures XVI-XXIV (1916-1917)
  - Coverage: Dream methodology, psychoanalysis vs psychiatry, resistance/repression, infantile sexuality, Oedipus complex, libido development (oral/anal/genital phases), regression/fixation, symptom formation, childhood neuroses, primal phantasies, introversion, artistic sublimation
  - Systematic theoretical foundation for neurosis etiology and psychoanalytic technique
- **Part 15**: 83 positions (FREUD-1441 to FREUD-1523) added November 2025
  - Source: Post-WWI theoretical works (1919-1921)
  - Works: The 'Uncanny' (11), Beyond The Pleasure Principle (30), Group Psychology And The Analysis Of The Ego (42)
  - Coverage: Ego-splitting, doubling, repetition compulsion, death drive (Thanatos), Eros-Thanatos dualism, identification, group dynamics, ego-ideal, libidinal bonds
  - Major theoretical turn introducing death drive and structural model foundations
- **Total Freud Positions**: 1,523 (FREUD-0001 to FREUD-1523)
- **Embeddings**: Perfect 1:1 alignment, 3,792 total positions with embeddings

### Complete Works Extraction Progress (FREUD_DATABASE_v10.json)
- **Parts 1-20 Extracted**: 271 positions from raw Complete Works text files
- **LLM Extraction Pipeline**: Automated extraction using GPT-4o-mini
- **Coverage**: Psycho-Analytic Movement history, parapraxes, losing/mislaying, forgetting, bungled actions, dreams, ego-neurosis dynamics, gain from illness, traumatic neurosis, The Uncanny (doubling, repetition compulsion), The Ego and the Id (consciousness/unconscious, repression, psychical dynamics), Inhibitions/Symptoms/Anxiety (repression mechanisms, protective shield, symptom formation), Civilization and Its Discontents (Eros/Death instinct, cultural super-ego, ethics), dream theory and distortion, anti-semitism

### Part 11 Domains
Anxiety, libido theory, narcissism, ego-ideal, transference, transference-neurosis, analytic therapy, therapeutic principles, suggestion critique, gain from illness, treatment limitations, narcissistic neuroses, object-choice, sleep, physical illness, love, megalomania, primary/secondary narcissism, realistic/neurotic/moral anxiety, phobia, hysteria, obsessional neurosis, traumatic neurosis, instinct dualism, economic model, therapeutic mechanisms.

### Part 12 Domains
Dreams, dream interpretation, methodology, symptoms, neurosis, resistance, repression, unconscious, sexuality, libido, infantile sexuality, Oedipus complex, development, regression, fixation, ego, symptom formation, childhood neuroses, perversion, complementary series, phylogenetic inheritance, pleasure principle, reality principle, primal phantasies, introversion, artistic sublimation, castration complex, oral phase, anal phase, genital primacy.

### Part 15 Domains
Uncanny, doubling, ego-splitting, repetition compulsion, death drive, Thanatos, Eros, instinct dualism, identification, group psychology, ego-ideal, libidinal bonds, narcissism, transference, anxiety, regression, repression, unconscious, sexuality, psychoanalytic theory.

### Recent Changes
- **November 18, 2025**: Added Grok (xAI) API support - users can now select Grok models (grok-4.1, grok-4, grok-2, grok-2-mini) as AI provider
- **November 18, 2025**: Built Freud inference engine - 6,394 rules convert user queries into metapsychological deductions that become "undeniable foundations" for LLM responses. Transforms app from "best Freud impersonator" to "executable Freudian mind"
- **November 18, 2025**: **FINAL EXPANSION** - Extracted an additional 45 positions from Parts 17-20! Total Complete Works extraction now at **271 positions**. **GRAND TOTAL: 7,249 philosophical positions**.
- **November 18, 2025**: Parts 17-20 extraction complete - covering Inhibitions/Symptoms/Anxiety (repression mechanisms), Civilization and Its Discontents (Eros/Death instinct duality, cultural super-ego), dream theory and distortion, anti-semitism
- **November 18, 2025**: Parts 12-16 extraction complete - covering Psycho-Analytic Movement, parapraxes, ego-neurosis dynamics, The Uncanny essay, and The Ego and the Id
- **November 18, 2025**: **MAJOR MILESTONE** - Automated extraction pipeline built and deployed! Successfully extracted philosophical positions from raw Freud Complete Works text files (Parts 1-20) using LLM-based extraction.
- **November 18, 2025**: Created FREUD_DATABASE_v10.json with positions extracted from Complete Works covering unconscious mind, dreams, psychosexual development, defense mechanisms, Oedipus complex, psychopathology, delusions, taboo of virginity, Little Hans phobia analysis, parapraxes, ego-splitting, repetition compulsion, and more
- **November 18, 2025**: Enhanced Mode feature added - users can toggle between Basic Mode (faithful summarization) and Enhanced Mode (creative theoretical extension)
- **November 18, 2025**: Part 11 integration complete - added final Introductory Lectures (XXV-XXVIII) covering anxiety, narcissism, transference, and analytic therapy
- **November 18, 2025**: Part 12 integration complete - added 351 positions from Introductory Lectures XVI-XXIV covering neurosis theory, infantile sexuality, Oedipus complex, libido development, and symptom formation
- **November 18, 2025**: Part 15 integration complete - added 83 positions from post-WWI works (1919-1921) covering the uncanny, death drive, repetition compulsion, and group psychology
