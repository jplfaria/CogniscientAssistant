#!/usr/bin/env python3
"""Simple mock proxy using built-in libraries."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import uuid

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
    
    def do_POST(self):
        if self.path == '/v1/chat/completions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract prompt
            messages = data.get('messages', [])
            user_message = ""
            for msg in messages:
                if msg.get('role') == 'user':
                    user_message = msg.get('content', '')
            
            # Generate response
            response_content = self.generate_response(user_message)
            
            response = {
                "id": str(uuid.uuid4()),
                "created": int(time.time()),
                "model": data.get('model', 'gpt35'),
                "choices": [{
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": response_content,
                        "role": "assistant"
                    }
                }],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 200,
                    "total_tokens": 300
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
    
    def generate_response(self, prompt):
        """Generate appropriate test responses."""
        
        # For ParseResearchGoal
        if "Develop a cure for aging using nanotechnology" in prompt:
            return json.dumps({
                "primary_objective": "Create nanotechnology-based interventions to halt or reverse biological aging in humans",
                "sub_objectives": [
                    "Identify key aging mechanisms targetable by nanotechnology",
                    "Design biocompatible nanodevices for cellular repair",
                    "Develop targeted delivery systems for anti-aging therapies",
                    "Test safety and efficacy in model organisms"
                ],
                "implied_constraints": [
                    "Must ensure biocompatibility and safety",
                    "Ethical considerations for human enhancement",
                    "Regulatory compliance for medical interventions",
                    "Cost-effectiveness for widespread application"
                ],
                "hypothesis_categories": ["mechanistic", "therapeutic", "technological"],
                "key_terms": ["nanotechnology", "aging", "senescence", "cellular repair", "longevity"],
                "success_criteria": [
                    "Demonstrated reversal of aging biomarkers",
                    "Extension of healthy lifespan in model organisms",
                    "FDA approval for human trials",
                    "No significant adverse effects"
                ]
            })
        
        # For GenerateHypothesis about jellyfish
        elif "biological immortality" in prompt and "jellyfish" in prompt:
            return json.dumps({
                "id": "hyp_jellyfish_mtrna_001",
                "summary": "Jellyfish transdifferentiation is mediated by mitochondrial-derived regulatory RNAs that reset cellular age",
                "full_description": "Based on recent studies of Turritopsis dohrnii, I hypothesize that the jellyfish's ability to revert from medusa to polyp stage is controlled by a unique class of mitochondrial-derived regulatory RNAs (mt-rRNAs) that can reprogram nuclear gene expression patterns. These mt-rRNAs are released during stress conditions and interact with chromatin remodeling complexes to reset epigenetic age markers, effectively reversing cellular differentiation while maintaining genomic integrity.",
                "category": "mechanistic",
                "novelty_claim": "First proposal linking mitochondrial RNA signaling to cellular transdifferentiation and age reversal in jellyfish",
                "assumptions": [
                    "Mitochondria can produce regulatory RNAs that affect nuclear gene expression",
                    "Epigenetic age markers can be systematically reset without genomic damage",
                    "The transdifferentiation process is regulated rather than stochastic"
                ],
                "reasoning": "Recent discoveries show mitochondria produce various RNA species that can translocate to the nucleus. In jellyfish undergoing life cycle reversal, mitochondrial dynamics change dramatically. By connecting these observations with the known role of epigenetic modifications in aging, I propose a mechanism where specialized mt-rRNAs coordinate the dedifferentiation process by targeting specific chromatin modifiers, explaining how jellyfish achieve biological immortality while maintaining tissue organization.",
                "experimental_protocol": {
                    "objective": "Identify and characterize mitochondrial-derived RNAs involved in jellyfish transdifferentiation",
                    "methodology": "1) Collect T. dohrnii samples at different stages of life cycle reversal. 2) Perform mitochondrial RNA-seq and small RNA profiling. 3) Use RNA-FISH to track mt-RNA nuclear translocation. 4) Perform ChIP-seq for chromatin modifications before/during/after reversal. 5) Inject synthetic mt-RNA candidates into adult medusae to trigger reversal. 6) Use CRISPR to knock down mt-RNA processing machinery and assess impact on immortality.",
                    "expected_outcomes": [
                        "Identification of specific mt-RNA species upregulated during reversal",
                        "Demonstration of mt-RNA nuclear localization",
                        "Correlation between mt-RNA levels and epigenetic reprogramming",
                        "Synthetic mt-RNAs induce transdifferentiation"
                    ],
                    "required_resources": [
                        "T. dohrnii culture facility",
                        "Next-generation sequencing platform",
                        "Advanced microscopy for RNA-FISH",
                        "Microinjection equipment"
                    ],
                    "timeline": "24 months"
                },
                "supporting_evidence": [
                    "Zhang et al. (2023) - Mitochondrial RNAs regulate nuclear gene expression in mammalian cells",
                    "Hasegawa et al. (2022) - Epigenetic clock reversal in T. dohrnii during life cycle reversal",
                    "Liu et al. (2023) - Stress-induced mitochondrial RNA release in marine invertebrates"
                ],
                "version": 1
            })
        
        # Simple test responses
        elif "What is 2+2" in prompt:
            return "4"
        elif "Say hello" in prompt or "Say 'OK'" in prompt:
            return "OK"
        else:
            return "Mock response for testing"
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8000), MockHandler)
    print("Mock proxy running on http://127.0.0.1:8000")
    server.serve_forever()