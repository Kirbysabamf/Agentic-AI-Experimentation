#!/usr/bin/env python3
"""
Marketing A/B Testing Simulation with Agentic Architecture

This script runs A/B tests on marketing images using three distinct persona agents:
- Single Mother (budget-conscious, family-focused)  
- Young Male (status-seeking, high income)
- Elderly Retiree (value-focused, limited budget)
"""

import asyncio
import json
import os
import argparse
from typing import Dict, Any
from dotenv import load_dotenv

from workflow.ab_testing_graph import ABTestingWorkflow, ABTestState
from utils.image_processor import ImageProcessor

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    load_dotenv()
    
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "default_image_url": os.getenv("DEFAULT_IMAGE_URL", "https://example.com/marketing-image.jpg"),
        "output_dir": os.getenv("OUTPUT_DIR", "results")
    }
    
    if not config["openai_api_key"]:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return config

def create_sample_variants() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Create sample A/B test variants"""
    variant_a = {
        "name": "Original",
        "description": "Standard marketing approach with product features",
        "price": 49.99,
        "category": "consumer_goods",
        "marketing_angle": "feature_focused",
        "call_to_action": "Buy Now - Limited Time Offer",
        "color_scheme": "blue_and_white",
        "layout": "product_centered"
    }
    
    variant_b = {
        "name": "Emotional",
        "description": "Emotion-focused marketing emphasizing lifestyle benefits",
        "price": 49.99,  # Same price for fair comparison
        "category": "consumer_goods", 
        "marketing_angle": "lifestyle_focused",
        "call_to_action": "Transform Your Life Today",
        "color_scheme": "warm_colors",
        "layout": "lifestyle_centered"
    }
    
    return variant_a, variant_b

def print_results_summary(results: Dict[str, Any]):
    """Print a formatted summary of A/B test results"""
    test_results = results["test_results"]
    
    print("\n" + "="*60)
    print("           A/B TESTING RESULTS SUMMARY")
    print("="*60)
    
    print(f"\n<� WINNER: Variant {test_results['winner']}")
    print(f"=� Confidence Score: {test_results['confidence_score']:.2%}")
    print(f"=� Statistical Significance: {'Yes' if test_results['statistical_significance'] else 'No'}")
    
    print(f"\n=� OVERALL SCORES:")
    print(f"   Variant A Average: {test_results['variant_a_average']:.2%}")
    print(f"   Variant B Average: {test_results['variant_b_average']:.2%}")
    
    print(f"\n=e PERSONA ANALYSIS:")
    for persona, analysis in test_results["persona_analysis"].items():
        persona_name = persona.replace('_', ' ').title()
        print(f"\n   {persona_name}:")
        print(f"     Preferred Variant: {analysis['preferred_variant']}")
        print(f"     Variant A Score: {analysis['variant_a_score']:.2%}")
        print(f"     Variant B Score: {analysis['variant_b_score']:.2%}")
        print(f"     Difference: {analysis['score_difference']:.2%}")
    
    print(f"\n=� RECOMMENDATIONS:")
    for i, rec in enumerate(test_results["recommendations"], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "="*60)

def print_detailed_persona_responses(results: Dict[str, Any]):
    """Print detailed persona responses for analysis"""
    print("\n" + "="*80)
    print("                    DETAILED PERSONA RESPONSES")
    print("="*80)
    
    responses = results["persona_responses"]
    
    # Group responses by persona
    persona_responses = {}
    for response in responses:
        persona = response["persona"]
        if persona not in persona_responses:
            persona_responses[persona] = {"A": None, "B": None}
        persona_responses[persona][response["variant"]] = response["response"]
    
    for persona, variants in persona_responses.items():
        persona_name = persona.replace('_', ' ').title()
        print(f"\n<� {persona_name}:")
        print("-" * 50)
        
        for variant in ["A", "B"]:
            if variants[variant]:
                resp = variants[variant]
                print(f"\n   Variant {variant}:")
                print(f"     Purchase Likelihood: {resp['purchase_likelihood']:.2%}")
                print(f"     Emotional Response: {resp['emotional_response']}")
                print(f"     Reasoning: {resp['reasoning']}")
                print(f"     Key Factors: {', '.join(resp['key_factors'])}")
                print(f"     Budget Consideration: {resp['budget_consideration']}")

async def run_ab_test_simulation(image_url: str, variant_a: Dict[str, Any], variant_b: Dict[str, Any]) -> Dict[str, Any]:
    """Run the complete A/B test simulation"""
    config = load_config()
    
    # Initialize the workflow
    workflow = ABTestingWorkflow(config["openai_api_key"])
    
    # Prepare the initial state
    initial_state: ABTestState = {
        "image_url": image_url,
        "image_description": "",
        "product_info": {
            "category": "general",
            "price": 49.99
        },
        "variant_a_info": variant_a,
        "variant_b_info": variant_b,
        "persona_responses": [],
        "current_variant": "",
        "test_results": {},
        "analysis_complete": False
    }
    
    print("=� Starting A/B Test Simulation...")
    print(f"=� Analyzing image: {image_url}")
    print(f"<p  Variant A: {variant_a['name']} - {variant_a['description']}")
    print(f"<q  Variant B: {variant_b['name']} - {variant_b['description']}")
    
    # Run the workflow
    results = await workflow.run_ab_test(initial_state)
    
    return results

def save_results(results: Dict[str, Any], output_dir: str):
    """Save results to JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a clean filename with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ab_test_results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Convert results to JSON-serializable format
    json_results = json.loads(json.dumps(results, default=str))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print(f"=� Results saved to: {filepath}")
    return filepath

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run marketing A/B test simulation")
    parser.add_argument("--image-url", type=str, 
                       help="URL or path to marketing image")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Directory to save results")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed persona responses")
    parser.add_argument("--save", action="store_true", default=True,
                       help="Save results to file")
    
    args = parser.parse_args()
    
    try:
        # Use provided image URL or default
        image_url = args.image_url
        if not image_url:
            # Use a sample marketing image URL for demonstration
            image_url = "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&q=80"
            print(f"9  Using sample image: {image_url}")
        
        # Validate image if it's a URL
        if image_url.startswith('http'):
            if not ImageProcessor.validate_image_url(image_url):
                print(f"L Invalid image URL: {image_url}")
                return
        
        # Create test variants
        variant_a, variant_b = create_sample_variants()
        
        # Run the simulation
        results = await run_ab_test_simulation(image_url, variant_a, variant_b)
        
        # Display results
        print_results_summary(results)
        
        if args.detailed:
            print_detailed_persona_responses(results)
        
        # Save results if requested
        if args.save:
            save_results(results, args.output_dir)
        
        print("\n A/B Test Simulation Complete!")
        
    except Exception as e:
        print(f"L Error running simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) ;