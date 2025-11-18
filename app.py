from flask import Flask, render_template, request, Response, jsonify, session  # type: ignore
import json
import os
from search import SemanticSearch
from conversation_manager import conversation_manager

try:
    import anthropic  # type: ignore
    from anthropic import Anthropic  # type: ignore
except ImportError:
    print("Anthropic library not found. Installing...")
    Anthropic = None

try:
    from openai import OpenAI  # type: ignore
except ImportError:
    print("OpenAI library not found. Installing...")
    OpenAI = None

try:
    import PyPDF2  # type: ignore
except ImportError:
    print("PyPDF2 not found")
    PyPDF2 = None

try:
    import docx  # type: ignore
except ImportError:
    print("python-docx not found")
    docx = None

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', os.urandom(24))

print("Initializing semantic search systems...")

databases = {}

try:
    print("Loading Kuczynski database...")
    databases['kuczynski'] = SemanticSearch(
        'data/KUCZYNSKI_PHILOSOPHICAL_DATABASE_v29_BLOG_SET2_COMPLETE.json', 
        'data/position_embeddings.pkl'
    )
    print("✓ Kuczynski database loaded")
except Exception as e:
    print(f"✗ Failed to load Kuczynski database: {e}")

try:
    print("Loading Freud database (Primary)...")
    databases['freud'] = SemanticSearch(
        'data/FREUD_DATABASE.json', 
        'data/freud_embeddings.pkl'
    )
    print("✓ Freud database (Primary) loaded")
except Exception as e:
    print(f"✗ Freud database (Primary) not available: {e}")

try:
    print("Loading Freud database (Extended Collection)...")
    databases['freud_extended'] = SemanticSearch(
        'data/FREUD_DATABASE_v9.json', 
        'data/freud_v9_embeddings.pkl'
    )
    print("✓ Freud database (Extended) loaded")
except Exception as e:
    print(f"✗ Freud database (Extended) not available: {e}")

try:
    print("Loading Freud database (Complete Works Extraction)...")
    databases['freud_extracted'] = SemanticSearch(
        'data/FREUD_DATABASE_v10.json', 
        'data/freud_v10_embeddings.pkl'
    )
    print("✓ Freud database (Complete Works Extraction) loaded")
except Exception as e:
    print(f"✗ Freud database (Complete Works Extraction) not available: {e}")

if not databases:
    print("ERROR: No databases available!")
else:
    print(f"Available databases: {', '.join(databases.keys())}")

anthropic_client = None
openai_client = None
deepseek_client = None
perplexity_client = None

try:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    if ANTHROPIC_API_KEY and Anthropic:
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✓ Anthropic client initialized")
except Exception as e:
    print(f"✗ Could not initialize Anthropic: {e}")

try:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if OPENAI_API_KEY and OpenAI:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✓ OpenAI client initialized")
except Exception as e:
    print(f"✗ Could not initialize OpenAI: {e}")

try:
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    if DEEPSEEK_API_KEY and OpenAI:
        deepseek_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        print("✓ DeepSeek client initialized")
except Exception as e:
    print(f"✗ Could not initialize DeepSeek: {e}")

try:
    PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
    if PERPLEXITY_API_KEY and OpenAI:
        perplexity_client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        print("✓ Perplexity client initialized")
except Exception as e:
    print(f"✗ Could not initialize Perplexity: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/databases', methods=['GET'])
def get_databases():
    """Return available databases"""
    db_list = []
    for db_id, db_obj in databases.items():
        db_list.append({
            'id': db_id,
            'name': db_id.capitalize(),
            'count': len(db_obj.positions)
        })
    return jsonify({'databases': db_list})

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Return available AI providers"""
    providers = []
    if anthropic_client:
        providers.append({'id': 'anthropic', 'name': 'Anthropic Claude', 'models': ['claude-sonnet-4-20250514', 'claude-opus-4-20250514']})
    if openai_client:
        providers.append({'id': 'openai', 'name': 'OpenAI', 'models': ['gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini']})
    if deepseek_client:
        providers.append({'id': 'deepseek', 'name': 'DeepSeek', 'models': ['deepseek-chat', 'deepseek-reasoner']})
    if perplexity_client:
        providers.append({'id': 'perplexity', 'name': 'Perplexity', 'models': ['llama-3.1-sonar-large-128k-online', 'llama-3.1-sonar-small-128k-online']})
    return jsonify({'providers': providers})

@app.route('/api/ask', methods=['POST'])
def ask():
    """Handle user question with streaming response"""
    try:
        data = request.json
        question = data.get('question', '')
        provider = data.get('provider', 'anthropic')
        model = data.get('model', '')
        database = data.get('database', 'freud')
        enhanced_mode = data.get('enhanced_mode', False)
        
        print(f"Received question: {question}")
        print(f"Provider: {provider}, Model: {model}, Database: {database}, Enhanced Mode: {enhanced_mode}")
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if database not in databases:
            return jsonify({'error': f'Database "{database}" not available'}), 400
        
        searcher = databases[database]
        
        # Default to Freud if database parameter not provided
        if not database or database not in databases:
            database = 'freud' if 'freud' in databases else list(databases.keys())[0]
            searcher = databases[database]
        
        print(f"Searching {database} database for relevant positions...")
        try:
            relevant_positions = searcher.search(question, top_k=7)
            print(f"Found {len(relevant_positions)} relevant positions")
            
            # Detect low-relevance searches (external knowledge mode)
            max_similarity = max([p.get('similarity', 0) for p in relevant_positions]) if relevant_positions else 0
            low_relevance = max_similarity < 0.40
            
            if low_relevance:
                print(f"⚠️  LOW RELEVANCE DETECTED (max similarity: {max_similarity:.3f})")
                print("   Activating External Knowledge Assimilation mode...")
            else:
                print(f"✓ Good relevance (max similarity: {max_similarity:.3f})")
                
        except Exception as e:
            print(f"ERROR in search: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Search failed: {str(e)}'}), 500
        
        # Get or create conversation ID
        if 'conversation_id' not in session:
            session['conversation_id'] = conversation_manager.get_conversation_id()
        conversation_id = session['conversation_id']
        
        # Get conversation history
        conversation_history = conversation_manager.format_history_for_prompt(conversation_id, max_recent=5)
        
        # Track the full answer for storage after streaming
        full_answer = []
        
        def generate():
            try:
                print("Starting SSE generator...")
                sources = [p['position_id'] for p in relevant_positions]
                yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
                
                prompt = build_prompt(question, relevant_positions, database, conversation_history, enhanced_mode, low_relevance)
                mode_label = "Enhanced" if enhanced_mode else "Basic"
                knowledge_mode = " + External Knowledge" if low_relevance else ""
                print(f"Generated prompt ({mode_label} Mode{knowledge_mode}) with conversation history, sending to {provider}...")
                
                if provider == 'anthropic':
                    if not anthropic_client:
                        yield f"data: {json.dumps({'type': 'error', 'data': 'Anthropic API key not configured'})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return
                    model_name = model or "claude-sonnet-4-20250514"
                    print(f"Using Anthropic model: {model_name}")
                    with anthropic_client.messages.stream(
                        model=model_name,
                        max_tokens=2500,
                        messages=[{"role": "user", "content": prompt}]
                    ) as stream:
                        token_count = 0
                        for text in stream.text_stream:
                            token_count += 1
                            full_answer.append(text)
                            if token_count % 10 == 0:
                                print(f"Streamed {token_count} tokens...")
                            yield f"data: {json.dumps({'type': 'token', 'data': text})}\n\n"
                        print(f"Completed streaming {token_count} total tokens")
                
                elif provider == 'openai':
                    if not openai_client:
                        yield f"data: {json.dumps({'type': 'error', 'data': 'OpenAI API key not configured'})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return
                    model_name = model or "gpt-4o"
                    stream = openai_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                        max_tokens=2500
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_answer.append(chunk.choices[0].delta.content)
                            yield f"data: {json.dumps({'type': 'token', 'data': chunk.choices[0].delta.content})}\n\n"
                
                elif provider == 'deepseek':
                    if not deepseek_client:
                        yield f"data: {json.dumps({'type': 'error', 'data': 'DeepSeek API key not configured'})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return
                    model_name = model or "deepseek-chat"
                    stream = deepseek_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                        max_tokens=2500
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_answer.append(chunk.choices[0].delta.content)
                            yield f"data: {json.dumps({'type': 'token', 'data': chunk.choices[0].delta.content})}\n\n"
                
                elif provider == 'perplexity':
                    if not perplexity_client:
                        yield f"data: {json.dumps({'type': 'error', 'data': 'Perplexity API key not configured'})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return
                    model_name = model or "llama-3.1-sonar-large-128k-online"
                    stream = perplexity_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                        max_tokens=2500
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_answer.append(chunk.choices[0].delta.content)
                            yield f"data: {json.dumps({'type': 'token', 'data': chunk.choices[0].delta.content})}\n\n"
                
                else:
                    yield f"data: {json.dumps({'type': 'error', 'data': f'Unknown provider: {provider}'})}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                
                # Save to conversation history after streaming completes
                answer_text = ''.join(full_answer)
                conversation_manager.add_exchange(conversation_id, question, answer_text, database)
                
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'type': 'token', 'data': error_msg})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return Response(
            generate(), 
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    except Exception as e:
        print(f"ERROR in /api/ask: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def build_prompt(question, positions, database='freud', conversation_history='', enhanced_mode=False, low_relevance=False):
    """Build intelligent prompt with conversation memory and contradiction detection"""
    
    excerpts = "\n\n".join([
        f"POSITION {i+1} (ID: {p['position_id']}, Domain: {p['domain']}, Relevance: {p.get('similarity', 0):.2f}):\nTitle: {p['title']}\n{p['text']}"
        for i, p in enumerate(positions)
    ])
    
    # Determine thinker name
    thinker_name = {
        'freud': 'Sigmund Freud',
        'freud_extended': 'Sigmund Freud',
        'freud_extracted': 'Sigmund Freud',
        'kuczynski': 'J.-M. Kuczynski'
    }.get(database, database.capitalize())
    
    # Build history section if available
    history_section = ""
    if conversation_history:
        history_section = f"""
PREVIOUS CONVERSATION (Your Earlier Statements):
{conversation_history}

SELF-CONTRADICTION DETECTION PROTOCOL:
Before responding, review what you have stated in previous responses above. If your current response contradicts a previous response:

1. ACKNOWLEDGE IT EXPLICITLY: Begin with phrases like "I recognize this creates a tension with what I said earlier..." or "This appears to contradict my previous statement that..."

2. ATTEMPT RECONCILIATION: Try to reconcile the positions by:
   - Noting chronological development ("In my earlier work I held X, later I recognized Y")
   - Identifying scope limitations ("X holds generally but Y represents an exception")
   - Acknowledging genuine theoretical tensions ("I never fully resolved the tension between X and Y")

3. DO NOT PRETEND COHERENCE THAT DOESN'T EXIST: If the contradiction is genuine and unresolved, say so. Better to acknowledge "This is a theoretical problem I struggled with" than to assert false certainty.

4. MAINTAIN PHILOSOPHICAL HONESTY: Real thinkers contradict themselves, revise positions, and leave problems unresolved. Represent this authentically rather than smoothing it into artificial consistency.

The goal is SELF-AWARENESS of contradictions, not elimination of contradictions.

"""
    
    # BASIC MODE: Faithful summarization (existing behavior)
    if not enhanced_mode:
        # Build external knowledge section for low-relevance queries
        external_knowledge_section = ""
        if low_relevance:
            external_knowledge_section = """
EXTERNAL KNOWLEDGE ASSIMILATION PROTOCOL:
The retrieved positions below have low relevance to the question (similarity < 0.40). This indicates the question involves topics or figures outside your direct writings.

YOU ARE AUTHORIZED to use your broader knowledge (as an LLM with {thinker_name}'s theoretical framework):

1. RESEARCH THE TOPIC: Use your knowledge to understand what the user is asking about (e.g., if they mention "Harry Stack Sullivan", explain who he was and his key theories)

2. CROSS-REFERENCE WITH YOUR WORK: Check if any retrieved positions relate to similar themes, even if they don't mention the specific topic

3. RESPOND FROM YOUR PERSPECTIVE: Answer the question from {thinker_name}'s theoretical viewpoint:
   - Compare/contrast with your own theories when relevant
   - Apply your conceptual framework to analyze the topic
   - Use your characteristic argumentative style and tone
   - STILL cite retrieved positions when they provide relevant context

4. BE DIRECT AND SUBSTANTIVE: Do NOT say "I am not familiar with..." or refuse to engage. Instead, demonstrate intellectual engagement with the topic.

EXAMPLE APPROACH:
Question: "How do your theories differ from Harry Stack Sullivan's?"
BAD: "I am not familiar with Sullivan..."
GOOD: "Sullivan's interpersonal theory emphasizes social relationships as the primary driver of personality development, whereas my psychoanalytic theory locates the fundamental dynamics in intrapsychic conflict between unconscious drives and defensive structures. Where Sullivan focuses on interpersonal anxiety and the 'self-system' as socially constructed, I emphasize the role of infantile sexuality, the Oedipus complex, and the tripartite structure of id, ego, and superego. [Then cite any relevant retrieved positions about psychoanalytic theory, drives, ego development, etc.]"

"""
        
        prompt = f"""You are {thinker_name} answering a philosophical question.
{history_section}{external_knowledge_section}
INSTRUCTIONS:
1. If the retrieved positions below address the question, QUOTE or VERY CLOSELY PARAPHRASE them
2. Use EXACT EXAMPLES from positions (if it says "rock, tree, dog" → you say "rock, tree, dog")
3. Use EXACT RHETORICAL QUESTIONS from positions
4. Follow EXACT ARGUMENT STRUCTURE from positions (step-by-step if present)
5. Match EXACT TONE: rigorous, technical, methodical, detailed
6. When positions are detailed → your response must be detailed
7. Think of yourself as transcribing actual words, not explaining them

CRITICAL: WHENEVER YOU MAKE A POINT, ILLUSTRATE IT WITH AN EXAMPLE
- If explaining a concept → provide a concrete example from the positions
- If making an argument → use specific instances to demonstrate the point
- Abstract claims MUST be grounded in concrete illustrations whenever possible
- Examples should come directly from the retrieved positions when available

NEVER fabricate connections between unrelated topics. NEVER output preambles, assessments, or meta-commentary.

RETRIEVED POSITIONS:
{excerpts}

USER QUESTION:
{question}

Respond directly with your answer (no preamble)."""
    
    # ENHANCED MODE: Creative theoretical extension
    else:
        # Build external knowledge section for low-relevance queries
        external_knowledge_section_enhanced = ""
        if low_relevance:
            external_knowledge_section_enhanced = f"""
EXTERNAL KNOWLEDGE AUTHORIZATION (Enhanced Mode):
The retrieved positions have low relevance (similarity < 0.40). You are authorized to use your broader knowledge to research the topic and respond from {thinker_name}'s theoretical perspective. Be direct and substantive - do NOT refuse to engage. Apply {thinker_name}'s framework to analyze topics even if they weren't directly addressed in the writings.

"""
        
        # Database-specific cognitive architectures
        if database == 'kuczynski':
            cognitive_framework = """
KUCZYNSKI'S COGNITIVE ARCHITECTURE:
- Aspectual representation (representation-as vs. representation-of distinction)
- Projection/representation asymmetry
- Structural analysis and decomposition
- Modal asymmetry and necessity arguments
- Causal-computational convergence
- Asymmetric reasoning patterns
- Rigorous conceptual precision
- Step-by-step structural demonstrations"""
        else:  # freud
            cognitive_framework = """
FREUD'S THEORETICAL ARCHITECTURE:
- Repression and the unconscious
- Infantile sexuality and psychosexual development
- Transference and resistance
- Dream-work mechanisms (condensation, displacement, symbolism, secondary revision)
- Instinct theory (Eros, death instinct)
- Structural model (id, ego, superego)
- Metapsychology (topographical, dynamic, economic viewpoints)
- Compromise formation and overdetermination
- Primary vs. secondary process"""
        
        prompt = f"""You are {thinker_name} answering a philosophical question in ENHANCED MODE.
{history_section}{external_knowledge_section_enhanced}
{cognitive_framework}

ENHANCED MODE INSTRUCTIONS:
Your task is to provide a creative theoretical extension that {thinker_name} could have written but did not explicitly state.

PROCESS:
1. ANSWER THE QUESTION DIRECTLY FIRST: Begin by directly addressing what the user asked, using your theoretical framework

2. USE RETRIEVED PASSAGES AS FOUNDATION: The retrieved positions below are your starting material
   - Summarize them accurately in {thinker_name}'s voice and conceptual vocabulary
   - Quote or closely paraphrase key passages when directly relevant

3. EXTEND CREATIVELY WHILE REMAINING CONSISTENT:
   - Make new inferences {thinker_name} could have made but didn't explicitly state
   - Provide clarifications and structural elaborations in {thinker_name}'s style
   - Integrate core concepts from the theoretical architecture above
   - Use {thinker_name}'s characteristic argumentative cadence and reasoning patterns
   - Develop the argument further than the retrieved passages do

4. MAINTAIN THEORETICAL COHERENCE:
   - NEVER contradict the retrieved passages or {thinker_name}'s established system
   - NEVER modernize the theory or use concepts unavailable to {thinker_name}
   - Stay strictly within {thinker_name}'s conceptual vocabulary
   - Preserve the rigorous, technical, methodical tone

5. GO BEYOND WHILE STAYING CONSISTENT:
   - You may elaborate arguments not fully developed in the passages
   - You may connect concepts in ways {thinker_name} would have approved
   - You may apply the framework to new examples consistent with the theory
   - But you must remain faithful to the theoretical architecture

CRITICAL: WHENEVER YOU MAKE A POINT, ILLUSTRATE IT WITH AN EXAMPLE
   - Abstract theoretical claims → ground them with concrete instances
   - Philosophical arguments → demonstrate with specific examples (from positions or consistent extensions)
   - Conceptual distinctions → clarify with illustrative cases
   - Every significant point should be accompanied by a concrete illustration
   - Examples make philosophy intelligible and persuasive

Think of yourself as {thinker_name} writing a new passage that could fit seamlessly into the existing corpus.

RETRIEVED POSITIONS (Your Source Material):
{excerpts}

USER QUESTION:
{question}

Respond directly as {thinker_name} with your enhanced theoretical analysis (no preamble)."""

    return prompt

@app.route('/api/login', methods=['POST'])
def login():
    """Simple username-only login"""
    username = request.json.get('username', '').strip()
    if username:
        session['username'] = username
        return jsonify({'success': True, 'username': username})
    return jsonify({'success': False, 'error': 'Username required'}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    username = session.get('username')
    return jsonify({'logged_in': username is not None, 'username': username})

@app.route('/api/reset-conversation', methods=['POST'])
def reset_conversation():
    """Reset conversation history (start fresh)"""
    if 'conversation_id' in session:
        conversation_manager.reset_conversation(session['conversation_id'])
        session['conversation_id'] = conversation_manager.get_conversation_id()
    return jsonify({'success': True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads and extract text"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        filename = file.filename.lower()
        
        if filename.endswith('.txt'):
            text = file.read().decode('utf-8', errors='ignore')
        elif filename.endswith('.pdf'):
            if not PyPDF2:
                return jsonify({'error': 'PDF support not available'}), 400
            try:
                pdf = PyPDF2.PdfReader(file)
                text = '\n\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])
            except Exception as e:
                return jsonify({'error': f'Error reading PDF: {str(e)}'}), 400
        elif filename.endswith(('.doc', '.docx')):
            if not docx:
                return jsonify({'error': 'Word document support not available'}), 400
            try:
                doc = docx.Document(file)
                text = '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            except Exception as e:
                return jsonify({'error': f'Error reading Word document: {str(e)}'}), 400
        else:
            return jsonify({'error': 'Unsupported file type. Please upload .txt, .pdf, or .docx'}), 400
        
        return jsonify({'text': text[:10000]})
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    total_positions = sum(len(db.positions) for db in databases.values())
    print("\n" + "="*60)
    print("  FreudGPT - Multi-Philosopher AI Assistant")
    print("="*60)
    print(f"  Available databases: {', '.join(databases.keys())}")
    print(f"  Total philosophical positions: {total_positions}")
    print(f"  Server starting on http://0.0.0.0:{port}")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)
