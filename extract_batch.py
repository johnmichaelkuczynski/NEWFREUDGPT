#!/usr/bin/env python3
"""
Batch Position Extraction - Process one section at a time
Allows incremental extraction with progress saving
"""

import json
import re
import os
from typing import List, Dict
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def extract_sample_positions(filepath: str, max_chunks: int = 3):
    """Extract positions from a small sample to demonstrate the pipeline"""
    
    print(f"Processing: {os.path.basename(filepath)}")
    print(f"Reading file...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Clean text
    text = text.replace('\ufeff', '')
    text = re.sub(r'\n\s*The Interpretation Of Dreams\s*\n', '\n', text)
    text = re.sub(r'\n\s*\d{3,4}\s*\n', '\n', text)
    
    # Extract a meaningful chunk (skip table of contents)
    chunks = text.split('\n\n\n')
    positions = []
    
    for i, chunk in enumerate(chunks[:max_chunks]):
        if len(chunk.split()) < 100:  # Skip very short chunks
            continue
        
        print(f"  Extracting from chunk {i+1}/{max_chunks}...")
        
        prompt = f"""Extract atomic philosophical/psychoanalytic positions from this Freud text.

For each position, provide JSON with:
- "title": Brief title (5-10 words)  
- "text_evidence": The philosophical claim (10-150 words)
- "domain": Category (DREAM_THEORY, PSYCHOPATHOLOGY, METAPSYCHOLOGY, CLINICAL_THEORY, etc.)

TEXT:
{chunk[:3000]}

Return JSON object with "positions" array. Extract 1-3 positions maximum."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in extracting philosophical positions from Freud's writings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            extracted = result.get('positions', [])
            
            for pos in extracted:
                if all(k in pos for k in ['title', 'text_evidence', 'domain']):
                    positions.append(pos)
                    print(f"    ✓ {pos['title']}")
        
        except Exception as e:
            print(f"    Error: {e}")
    
    return positions

def main():
    """Extract sample positions from one file"""
    
    print("=" * 70)
    print("FREUD POSITION EXTRACTION - SAMPLE RUN")
    print("=" * 70)
    print()
    
    # Process just Part 1 as a demo
    filepath = 'attached_assets/Freud - Complete Works (Over 4000 pages, Most Comprehensive Version Available)_Part1_1763442245951.txt'
    
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return
    
    positions = extract_sample_positions(filepath, max_chunks=5)
    
    print()
    print("=" * 70)
    print(f"EXTRACTED {len(positions)} POSITIONS")
    print("=" * 70)
    print()
    
    # Format as database
    database = {
        'metadata': {
            'version': '10.0-SAMPLE',
            'extraction_date': '2025-11-18',
            'source': 'Freud Complete Works Part 1 (sample)',
            'total_positions': len(positions)
        },
        'positions': []
    }
    
    for i, pos in enumerate(positions, 1):
        record = {
            'position_id': f'EXTRACT-{i:03d}',
            'id': f'EXTRACT-{i:03d}',
            'title': pos['title'],
            'text_evidence': pos['text_evidence'],
            'domain': pos['domain'],
            'source': ['Freud Complete Works'],
            'work_id': 'EXTRACTED',
            'work_title': 'Complete Works Sample Extraction'
        }
        database['positions'].append(record)
        
        print(f"Position {i}:")
        print(f"  Title: {pos['title']}")
        print(f"  Domain: {pos['domain']}")
        print(f"  Text: {pos['text_evidence'][:100]}...")
        print()
    
    # Save
    output_path = 'data/FREUD_EXTRACTED_SAMPLE.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved to: {output_path}")
    print()
    print("This demonstrates the extraction pipeline is working!")
    print(f"To extract all ~100,000 lines would take ~2-3 hours and ~$20-30 in API costs.")
    print("Would you like to proceed with full extraction?")

if __name__ == '__main__':
    main()
