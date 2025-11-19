import json
import re
from typing import List, Dict

class JungInferenceEngine:
    def __init__(self, rules_file='jung_rules_full.json'):
        """Initialize the Jungian inference engine with rule database"""
        with open(rules_file, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
        print(f"✓ Jung inference engine loaded: {len(self.rules):,} rules")
    
    def deduce(self, phenomenon: str, max_rules: int = 15) -> List[Dict]:
        """
        Forward-chaining inference over phenomenon.
        Returns list of fired rules with conclusions and metadata.
        
        Args:
            phenomenon: User's input text describing a psychological phenomenon
            max_rules: Maximum number of rules to return (default 15)
        
        Returns:
            List of fired rules sorted by year (descending), each containing:
            - id, year, premise, conclusion, strength, domain
        """
        activated = []
        accumulated_text = phenomenon.lower()
        
        # First pass: fire all matching rules
        for rule in self.rules:
            premise_pattern = rule['premise']
            try:
                if re.search(premise_pattern, accumulated_text, re.IGNORECASE):
                    activated.append(rule)
                    # Add conclusion to accumulated text for chaining
                    accumulated_text += " " + rule['conclusion'].lower()
            except re.error:
                # Skip malformed regex patterns
                continue
        
        # Chronological override: later Jung wins
        activated.sort(key=lambda r: r['year'], reverse=True)
        
        # Return top max_rules
        return activated[:max_rules]
    
    def format_chain(self, fired_rules: List[Dict]) -> str:
        """
        Format fired rules into analytical psychology chain explanation.
        
        Args:
            fired_rules: List of rules from deduce()
        
        Returns:
            Formatted string for LLM consumption
        """
        if not fired_rules:
            return "No specific Jungian rules activated. Proceed with general analytical psychology principles."
        
        chain = []
        for rule in fired_rules:
            viewpoint = self._get_viewpoint(rule)
            chain.append(
                f"From the {viewpoint} viewpoint ({rule['year']}): {rule['conclusion']}"
            )
        
        return "\n\n".join(chain)
    
    def _get_viewpoint(self, rule: Dict) -> str:
        """Determine analytical psychology viewpoint from rule content"""
        premise = rule['premise'].lower()
        conclusion = rule['conclusion'].lower()
        
        if any(term in premise or term in conclusion for term in ['archet', 'collective', 'symbol', 'myth']):
            return 'archetypal'
        elif any(term in premise or term in conclusion for term in ['individuation', 'self', 'wholeness', 'integration']):
            return 'individuation'
        elif any(term in premise or term in conclusion for term in ['introversion', 'extraversion', 'type', 'function', 'attitude']):
            return 'typological'
        elif any(term in premise or term in conclusion for term in ['unconscious', 'complex', 'shadow', 'projection']):
            return 'dynamic'
        else:
            return 'analytical'

# Global instance for app import
engine = None

def get_engine():
    """Get or create singleton inference engine"""
    global engine
    if engine is None:
        engine = JungInferenceEngine()
    return engine
