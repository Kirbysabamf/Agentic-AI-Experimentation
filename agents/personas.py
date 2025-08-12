from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import random

class PersonaType(Enum):
    SINGLE_MOTHER = "single_mother"
    YOUNG_MALE = "young_male"
    ELDERLY_RETIREE = "elderly_retiree"

@dataclass
class PersonaResponse:
    persona_type: PersonaType
    purchase_likelihood: float  # 0.0 to 1.0
    reasoning: str
    key_factors: List[str]
    emotional_response: str
    budget_consideration: str

class BasePersona:
    def __init__(self, name: str, persona_type: PersonaType):
        self.name = name
        self.persona_type = persona_type
        self.decision_factors = []
        self.budget_constraints = {}
        
    def analyze_image(self, image_description: str, product_info: Dict[str, Any]) -> PersonaResponse:
        raise NotImplementedError("Subclasses must implement analyze_image")

class SingleMotherPersona(BasePersona):
    def __init__(self):
        super().__init__("Sarah", PersonaType.SINGLE_MOTHER)
        self.decision_factors = [
            "child_safety", "value_for_money", "durability", 
            "family_benefit", "time_saving", "necessity"
        ]
        self.budget_constraints = {"monthly_discretionary": 200, "max_single_purchase": 100}
        self.priorities = ["kids_wellbeing", "practical_value", "safety"]
        
    def analyze_image(self, image_description: str, product_info: Dict[str, Any]) -> PersonaResponse:
        price = product_info.get("price", 0)
        category = product_info.get("category", "").lower()
        
        # Decision logic based on single mother priorities
        purchase_likelihood = 0.3  # Base likelihood
        key_factors = []
        
        # Family-oriented products get higher likelihood
        if any(word in category for word in ["baby", "child", "family", "home", "food", "health"]):
            purchase_likelihood += 0.4
            key_factors.append("Benefits my children")
            
        # Price sensitivity
        if price <= 50:
            purchase_likelihood += 0.2
            key_factors.append("Affordable price point")
        elif price > 100:
            purchase_likelihood -= 0.3
            key_factors.append("Too expensive for budget")
            
        # Safety considerations
        if "safe" in image_description.lower() or "certified" in image_description.lower():
            purchase_likelihood += 0.2
            key_factors.append("Safety certified")
            
        # Practical value
        if any(word in image_description.lower() for word in ["practical", "useful", "convenient", "durable"]):
            purchase_likelihood += 0.1
            key_factors.append("Practical value")
            
        purchase_likelihood = max(0.0, min(1.0, purchase_likelihood))
        
        reasoning = f"As a single mother, I need to consider how this purchase affects my children and fits our budget. "
        if purchase_likelihood > 0.6:
            reasoning += "This seems like a good investment for our family."
        elif purchase_likelihood > 0.4:
            reasoning += "I'm somewhat interested but need to think about the cost."
        else:
            reasoning += "This doesn't seem necessary for our current needs."
            
        emotional_response = "Cautious but caring" if purchase_likelihood < 0.5 else "Interested and hopeful"
        budget_consideration = f"Monthly budget allows ${self.budget_constraints['monthly_discretionary']}, this costs ${price}"
        
        return PersonaResponse(
            persona_type=self.persona_type,
            purchase_likelihood=purchase_likelihood,
            reasoning=reasoning,
            key_factors=key_factors,
            emotional_response=emotional_response,
            budget_consideration=budget_consideration
        )

class YoungMalePersona(BasePersona):
    def __init__(self):
        super().__init__("Jake", PersonaType.YOUNG_MALE)
        self.decision_factors = [
            "status_symbol", "personal_enjoyment", "technology", 
            "style", "performance", "social_approval"
        ]
        self.budget_constraints = {"monthly_discretionary": 800, "max_single_purchase": 500}
        self.priorities = ["self_image", "instant_gratification", "social_status"]
        
    def analyze_image(self, image_description: str, product_info: Dict[str, Any]) -> PersonaResponse:
        price = product_info.get("price", 0)
        category = product_info.get("category", "").lower()
        
        purchase_likelihood = 0.4  # Base likelihood - more impulsive
        key_factors = []
        
        # Tech and status items get higher likelihood
        if any(word in category for word in ["tech", "gaming", "fashion", "sports", "car", "electronics"]):
            purchase_likelihood += 0.3
            key_factors.append("Appeals to my interests")
            
        # Brand and status considerations
        if any(word in image_description.lower() for word in ["premium", "exclusive", "latest", "trending"]):
            purchase_likelihood += 0.2
            key_factors.append("Status and brand appeal")
            
        # Price sensitivity (less than other personas)
        if price <= 200:
            purchase_likelihood += 0.1
            key_factors.append("Reasonable price")
        elif price > 400:
            purchase_likelihood -= 0.1
            key_factors.append("Expensive but might be worth it")
            
        # Social proof
        if any(word in image_description.lower() for word in ["popular", "trending", "recommended", "rated"]):
            purchase_likelihood += 0.15
            key_factors.append("Social proof and popularity")
            
        # Instant gratification appeal
        if any(word in image_description.lower() for word in ["fast", "instant", "immediate", "quick"]):
            purchase_likelihood += 0.1
            key_factors.append("Immediate satisfaction")
            
        purchase_likelihood = max(0.0, min(1.0, purchase_likelihood))
        
        reasoning = f"This looks pretty cool and I can afford it. "
        if purchase_likelihood > 0.7:
            reasoning += "I'm definitely getting this - it's exactly what I want."
        elif purchase_likelihood > 0.5:
            reasoning += "I'm really tempted, might get it this weekend."
        else:
            reasoning += "Not really my thing, I'll pass."
            
        emotional_response = "Excited and impulsive" if purchase_likelihood > 0.6 else "Mildly interested"
        budget_consideration = f"I can easily afford ${price} with my ${self.budget_constraints['monthly_discretionary']} monthly budget"
        
        return PersonaResponse(
            persona_type=self.persona_type,
            purchase_likelihood=purchase_likelihood,
            reasoning=reasoning,
            key_factors=key_factors,
            emotional_response=emotional_response,
            budget_consideration=budget_consideration
        )

class ElderlyRetireePersona(BasePersona):
    def __init__(self):
        super().__init__("Robert", PersonaType.ELDERLY_RETIREE)
        self.decision_factors = [
            "value_for_money", "necessity", "quality", 
            "health_benefit", "simplicity", "longevity"
        ]
        self.budget_constraints = {"monthly_discretionary": 150, "max_single_purchase": 75}
        self.priorities = ["frugality", "health", "practicality"]
        
    def analyze_image(self, image_description: str, product_info: Dict[str, Any]) -> PersonaResponse:
        price = product_info.get("price", 0)
        category = product_info.get("category", "").lower()
        
        purchase_likelihood = 0.2  # Base likelihood - very conservative
        key_factors = []
        
        # Health and necessity items get priority
        if any(word in category for word in ["health", "medical", "food", "home", "utility"]):
            purchase_likelihood += 0.3
            key_factors.append("Necessary for daily life")
            
        # Strong price sensitivity
        if price <= 25:
            purchase_likelihood += 0.3
            key_factors.append("Very affordable")
        elif price <= 50:
            purchase_likelihood += 0.1
            key_factors.append("Reasonably priced")
        else:
            purchase_likelihood -= 0.2
            key_factors.append("Too expensive for fixed income")
            
        # Quality and durability matter
        if any(word in image_description.lower() for word in ["quality", "durable", "long-lasting", "reliable"]):
            purchase_likelihood += 0.2
            key_factors.append("Good quality and durability")
            
        # Simplicity preference
        if any(word in image_description.lower() for word in ["simple", "easy", "basic", "traditional"]):
            purchase_likelihood += 0.1
            key_factors.append("Simple and easy to use")
        elif any(word in image_description.lower() for word in ["complex", "advanced", "high-tech"]):
            purchase_likelihood -= 0.1
            key_factors.append("Too complicated")
            
        # Health benefits
        if any(word in image_description.lower() for word in ["health", "comfort", "mobility", "wellness"]):
            purchase_likelihood += 0.2
            key_factors.append("Health and wellness benefits")
            
        purchase_likelihood = max(0.0, min(1.0, purchase_likelihood))
        
        reasoning = f"At my age and on a fixed income, I need to be careful with purchases. "
        if purchase_likelihood > 0.6:
            reasoning += "This seems like a wise investment that I actually need."
        elif purchase_likelihood > 0.3:
            reasoning += "I'll think about it and maybe ask my children's opinion."
        else:
            reasoning += "This isn't something I need right now."
            
        emotional_response = "Cautious and practical" if purchase_likelihood < 0.5 else "Carefully optimistic"
        budget_consideration = f"Fixed income limits me to ${self.budget_constraints['monthly_discretionary']}/month, this costs ${price}"
        
        return PersonaResponse(
            persona_type=self.persona_type,
            purchase_likelihood=purchase_likelihood,
            reasoning=reasoning,
            key_factors=key_factors,
            emotional_response=emotional_response,
            budget_consideration=budget_consideration
        )