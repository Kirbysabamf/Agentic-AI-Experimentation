from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import asyncio
from agents.personas import SingleMotherPersona, YoungMalePersona, ElderlyRetireePersona, PersonaResponse

class ABTestState(TypedDict):
    image_url: str
    image_description: str
    product_info: Dict[str, Any]
    variant_a_info: Dict[str, Any]
    variant_b_info: Dict[str, Any]
    persona_responses: List[Dict[str, Any]]
    current_variant: str
    test_results: Dict[str, Any]
    analysis_complete: bool

class ABTestingWorkflow:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-vision-preview",
            api_key=openai_api_key,
            temperature=0.7
        )
        self.personas = {
            "single_mother": SingleMotherPersona(),
            "young_male": YoungMalePersona(),
            "elderly_retiree": ElderlyRetireePersona()
        }
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        graph = StateGraph(ABTestState)
        
        # Add nodes
        graph.add_node("analyze_image", self.analyze_image)
        graph.add_node("test_variant_a", self.test_variant_a)
        graph.add_node("test_variant_b", self.test_variant_b)
        graph.add_node("collect_responses", self.collect_responses)
        graph.add_node("analyze_results", self.analyze_results)
        
        # Add edges
        graph.add_edge("analyze_image", "test_variant_a")
        graph.add_edge("test_variant_a", "test_variant_b")
        graph.add_edge("test_variant_b", "collect_responses")
        graph.add_edge("collect_responses", "analyze_results")
        graph.add_edge("analyze_results", END)
        
        # Set entry point
        graph.set_entry_point("analyze_image")
        
        return graph.compile()
    
    async def analyze_image(self, state: ABTestState) -> Dict[str, Any]:
        """Analyze the marketing image using LLM vision capabilities"""
        try:
            # Use OpenAI's vision model to analyze the image
            messages = [
                SystemMessage(content="""You are an expert marketing analyst. Analyze this marketing image and provide:
1. A detailed description of what you see
2. The product category
3. Key visual elements and marketing messages
4. Target demographic indicators
5. Emotional appeals being used

Be specific and detailed in your analysis."""),
                HumanMessage(content=[
                    {"type": "text", "text": "Analyze this marketing image:"},
                    {"type": "image_url", "image_url": {"url": state["image_url"]}}
                ])
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse the response to extract product information
            description = response.content
            
            # Extract product category and price from existing product_info or make educated guess
            product_info = state.get("product_info", {})
            if not product_info.get("category"):
                # Use LLM to extract category
                category_prompt = f"Based on this image analysis, what product category is this? Respond with just the category: {description}"
                category_response = await self.llm.ainvoke([HumanMessage(content=category_prompt)])
                product_info["category"] = category_response.content.strip()
            
            return {
                **state,
                "image_description": description,
                "product_info": product_info
            }
            
        except Exception as e:
            # Fallback if image analysis fails
            return {
                **state,
                "image_description": f"Image analysis failed: {str(e)}. Using provided product info.",
                "product_info": state.get("product_info", {"category": "general", "price": 50})
            }
    
    async def test_variant_a(self, state: ABTestState) -> Dict[str, Any]:
        """Test variant A with all personas"""
        variant_info = state["variant_a_info"]
        responses = []
        
        # Combine image description with variant-specific information
        enhanced_description = f"{state['image_description']}\n\nVariant A Details: {variant_info.get('description', '')}"
        product_info = {**state["product_info"], **variant_info}
        
        for persona_name, persona in self.personas.items():
            response = persona.analyze_image(enhanced_description, product_info)
            responses.append({
                "variant": "A",
                "persona": persona_name,
                "response": response.__dict__
            })
        
        current_responses = state.get("persona_responses", [])
        current_responses.extend(responses)
        
        return {
            **state,
            "persona_responses": current_responses,
            "current_variant": "A"
        }
    
    async def test_variant_b(self, state: ABTestState) -> Dict[str, Any]:
        """Test variant B with all personas"""
        variant_info = state["variant_b_info"]
        responses = []
        
        # Combine image description with variant-specific information
        enhanced_description = f"{state['image_description']}\n\nVariant B Details: {variant_info.get('description', '')}"
        product_info = {**state["product_info"], **variant_info}
        
        for persona_name, persona in self.personas.items():
            response = persona.analyze_image(enhanced_description, product_info)
            responses.append({
                "variant": "B",
                "persona": persona_name,
                "response": response.__dict__
            })
        
        current_responses = state.get("persona_responses", [])
        current_responses.extend(responses)
        
        return {
            **state,
            "persona_responses": current_responses,
            "current_variant": "B"
        }
    
    async def collect_responses(self, state: ABTestState) -> Dict[str, Any]:
        """Collect and organize all persona responses"""
        responses = state["persona_responses"]
        
        # Organize responses by variant and persona
        organized_responses = {
            "variant_a": {},
            "variant_b": {}
        }
        
        for response_data in responses:
            variant = "variant_a" if response_data["variant"] == "A" else "variant_b"
            persona = response_data["persona"]
            organized_responses[variant][persona] = response_data["response"]
        
        return {
            **state,
            "organized_responses": organized_responses
        }
    
    async def analyze_results(self, state: ABTestState) -> Dict[str, Any]:
        """Analyze A/B test results and provide insights"""
        responses = state["persona_responses"]
        
        # Calculate metrics for each variant
        variant_a_scores = [r["response"]["purchase_likelihood"] for r in responses if r["variant"] == "A"]
        variant_b_scores = [r["response"]["purchase_likelihood"] for r in responses if r["variant"] == "B"]
        
        variant_a_avg = sum(variant_a_scores) / len(variant_a_scores) if variant_a_scores else 0
        variant_b_avg = sum(variant_b_scores) / len(variant_b_scores) if variant_b_scores else 0
        
        # Persona-specific analysis
        persona_analysis = {}
        for persona_name in self.personas.keys():
            persona_a = next((r for r in responses if r["variant"] == "A" and r["persona"] == persona_name), None)
            persona_b = next((r for r in responses if r["variant"] == "B" and r["persona"] == persona_name), None)
            
            if persona_a and persona_b:
                persona_analysis[persona_name] = {
                    "variant_a_score": persona_a["response"]["purchase_likelihood"],
                    "variant_b_score": persona_b["response"]["purchase_likelihood"],
                    "preferred_variant": "A" if persona_a["response"]["purchase_likelihood"] > persona_b["response"]["purchase_likelihood"] else "B",
                    "score_difference": abs(persona_a["response"]["purchase_likelihood"] - persona_b["response"]["purchase_likelihood"]),
                    "variant_a_reasoning": persona_a["response"]["reasoning"],
                    "variant_b_reasoning": persona_b["response"]["reasoning"]
                }
        
        # Overall winner determination
        winner = "A" if variant_a_avg > variant_b_avg else "B"
        confidence = abs(variant_a_avg - variant_b_avg)
        
        test_results = {
            "winner": winner,
            "confidence_score": confidence,
            "variant_a_average": variant_a_avg,
            "variant_b_average": variant_b_avg,
            "persona_analysis": persona_analysis,
            "recommendations": self._generate_recommendations(persona_analysis, winner, confidence),
            "statistical_significance": confidence > 0.1  # Simple threshold
        }
        
        return {
            **state,
            "test_results": test_results,
            "analysis_complete": True
        }
    
    def _generate_recommendations(self, persona_analysis: Dict, winner: str, confidence: float) -> List[str]:
        """Generate actionable recommendations based on test results"""
        recommendations = []
        
        if confidence < 0.1:
            recommendations.append("Results are inconclusive - consider testing with different variants or larger sample size")
        else:
            recommendations.append(f"Variant {winner} performs better overall with {confidence:.2%} higher conversion likelihood")
        
        # Persona-specific recommendations
        for persona, analysis in persona_analysis.items():
            if analysis["score_difference"] > 0.2:
                recommendations.append(
                    f"{persona.replace('_', ' ').title()} strongly prefers Variant {analysis['preferred_variant']} "
                    f"(difference: {analysis['score_difference']:.2%})"
                )
        
        # Check for persona splits
        preferences = [analysis["preferred_variant"] for analysis in persona_analysis.values()]
        if len(set(preferences)) > 1:
            recommendations.append("Different personas prefer different variants - consider targeted campaigns")
        
        return recommendations
    
    async def run_ab_test(self, initial_state: ABTestState) -> Dict[str, Any]:
        """Run the complete A/B testing workflow"""
        final_state = await self.graph.ainvoke(initial_state)
        return final_state