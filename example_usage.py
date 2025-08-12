#!/usr/bin/env python3
"""
Example usage of the Marketing A/B Testing system.

This script demonstrates various ways to use the agentic A/B testing framework.
"""

import asyncio
from workflow.ab_testing_graph import ABTestingWorkflow, ABTestState

async def example_basic_test():
    """Basic A/B test example"""
    print("=== Basic A/B Test Example ===")
    
    # Initialize workflow (replace with your API key)
    workflow = ABTestingWorkflow("your-openai-api-key")
    
    # Define test variants
    variant_a = {
        "name": "Feature-Focused",
        "description": "Highlights product features and specifications",
        "price": 99.99,
        "category": "electronics",
        "marketing_angle": "technical_specs",
        "call_to_action": "Shop Now"
    }
    
    variant_b = {
        "name": "Lifestyle-Focused", 
        "description": "Shows product in lifestyle context",
        "price": 99.99,
        "category": "electronics",
        "marketing_angle": "lifestyle_benefits",
        "call_to_action": "Transform Your Life"
    }
    
    # Set up initial state
    initial_state: ABTestState = {
        "image_url": "https://images.unsplash.com/photo-1560472355-536de3962603?w=800",
        "image_description": "",
        "product_info": {"category": "electronics", "price": 99.99},
        "variant_a_info": variant_a,
        "variant_b_info": variant_b,
        "persona_responses": [],
        "current_variant": "",
        "test_results": {},
        "analysis_complete": False
    }
    
    # Run the test
    results = await workflow.run_ab_test(initial_state)
    
    # Display results
    winner = results["test_results"]["winner"]
    confidence = results["test_results"]["confidence_score"]
    print(f"Winner: Variant {winner} (Confidence: {confidence:.2%})")
    
    return results

async def example_custom_personas():
    """Example showing how persona behavior varies by product category"""
    print("\n=== Custom Product Category Tests ===")
    
    workflow = ABTestingWorkflow("your-openai-api-key")
    
    # Test different product categories
    test_cases = [
        {
            "name": "Baby Products",
            "image_url": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=800",
            "category": "baby",
            "price": 29.99
        },
        {
            "name": "Luxury Watch",
            "image_url": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800", 
            "category": "luxury",
            "price": 299.99
        },
        {
            "name": "Health Supplement",
            "image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
            "category": "health", 
            "price": 39.99
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        
        variant_a = {
            "name": "Standard",
            "description": f"Standard marketing for {test_case['name']}",
            "price": test_case["price"],
            "category": test_case["category"]
        }
        
        variant_b = {
            "name": "Premium",
            "description": f"Premium positioning for {test_case['name']}",
            "price": test_case["price"] * 1.2,  # 20% price increase
            "category": test_case["category"]
        }
        
        initial_state: ABTestState = {
            "image_url": test_case["image_url"],
            "image_description": "",
            "product_info": {"category": test_case["category"], "price": test_case["price"]},
            "variant_a_info": variant_a,
            "variant_b_info": variant_b,
            "persona_responses": [],
            "current_variant": "",
            "test_results": {},
            "analysis_complete": False
        }
        
        try:
            results = await workflow.run_ab_test(initial_state)
            
            # Show persona preferences for this category
            persona_analysis = results["test_results"]["persona_analysis"]
            for persona, analysis in persona_analysis.items():
                persona_name = persona.replace('_', ' ').title()
                preferred = analysis['preferred_variant']
                score_a = analysis['variant_a_score']
                score_b = analysis['variant_b_score']
                print(f"  {persona_name}: Prefers {preferred} ({score_a:.1%} vs {score_b:.1%})")
                
        except Exception as e:
            print(f"  Error testing {test_case['name']}: {e}")

def example_persona_analysis():
    """Example showing individual persona characteristics"""
    print("\n=== Persona Analysis Example ===")
    
    from agents.personas import SingleMotherPersona, YoungMalePersona, ElderlyRetireePersona
    
    # Create personas
    personas = {
        "Single Mother": SingleMotherPersona(),
        "Young Male": YoungMalePersona(), 
        "Elderly Retiree": ElderlyRetireePersona()
    }
    
    # Test product scenarios
    test_products = [
        {
            "description": "Premium organic baby food with safety certifications",
            "info": {"category": "baby", "price": 15.99}
        },
        {
            "description": "Latest smartphone with cutting-edge features and premium design",
            "info": {"category": "tech", "price": 899.99}
        },
        {
            "description": "Simple, reliable health monitoring device with large display",
            "info": {"category": "health", "price": 49.99}
        }
    ]
    
    for product in test_products:
        print(f"\nProduct: {product['description'][:50]}...")
        print(f"Category: {product['info']['category']}, Price: ${product['info']['price']}")
        
        for persona_name, persona in personas.items():
            response = persona.analyze_image(product["description"], product["info"])
            print(f"  {persona_name}: {response.purchase_likelihood:.1%} likelihood")
            print(f"    Reasoning: {response.reasoning[:60]}...")

async def main():
    """Run all examples"""
    print("Marketing A/B Testing Examples")
    print("=" * 50)
    
    # Note: Replace with actual API key to run
    print("Note: Replace 'your-openai-api-key' with actual OpenAI API key to run these examples")
    
    # Uncomment to run with real API key:
    # await example_basic_test()
    # await example_custom_personas()
    example_persona_analysis()
    
    print("\nExamples completed! Check the main.py script for actual execution.")

if __name__ == "__main__":
    asyncio.run(main())