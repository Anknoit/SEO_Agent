import json
import requests
from typing import Dict, List

class SEOAgent:
    def __init__(self, model_name: str = "gemma3:latest"):
        self.model = model_name
        self.conversation_history = []
        self.base_url = "http://localhost:11434"
        
    def check_ollama_running(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Get available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            return []
    
    def generate_with_ollama(self, prompt: str, model: str = None) -> str:
        """Generate response using Ollama API directly"""
        if model is None:
            model = self.model
            
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 512
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            return ""
    
    def analyze_and_advise(self, page_data: Dict, seo_analysis: Dict) -> Dict:
        """Generate SEO recommendations"""
        
        # First, check if Ollama is running and get available models
        if not self.check_ollama_running():
            print("Ollama is not running. Using fallback recommendations.")
            return self._generate_fallback_recommendations(seo_analysis)
        
        # Get available models
        available_models = self.get_available_models()
        if not available_models:
            print("No models available. Using fallback recommendations.")
            return self._generate_fallback_recommendations(seo_analysis)
        
        # Check if our model is available
        if self.model not in available_models:
            print(f"Model {self.model} not found. Available models: {available_models}")
            # Use the first available model
            self.model = available_models[0]
            print(f"Switching to model: {self.model}")
        
        print(f"Using model: {self.model}")
        
        # Create prompt
        prompt = self._create_analysis_prompt(page_data, seo_analysis)
        
        # Generate response
        response = self.generate_with_ollama(prompt)
        
        if response:
            print(f"Received response from Ollama")
            recommendations = self._parse_response(response)
        else:
            print("No response from Ollama. Using fallback.")
            recommendations = self._generate_fallback_recommendations(seo_analysis)
        
        return recommendations
    
    def chat(self, user_input: str, context: Dict = None) -> str:
        """Chat with the agent"""
        if not self.check_ollama_running():
            return "Ollama is not running. Please start Ollama with: `ollama serve`"
        
        context_prompt = self._create_chat_context(context) if context else ""
        
        full_prompt = f"""You are an SEO expert assistant. {context_prompt}
        
User: {user_input}

SEO Expert: """
        
        response = self.generate_with_ollama(full_prompt)
        return response if response else "I apologize, but I couldn't generate a response at the moment."
    
    def _create_analysis_prompt(self, page_data: Dict, seo_analysis: Dict) -> str:
        """Create analysis prompt"""
        # Format issues
        issues = []
        for category, data in seo_analysis.items():
            if isinstance(data, dict) and 'issues' in data:
                for issue in data['issues']:
                    # Clean up category name for display
                    cat_name = category.replace('_analysis', '').replace('_', ' ').title()
                    issues.append(f"{cat_name}: {issue}")
        
        issues_text = "\n".join(issues) if issues else "No major issues found"
        
        # Create prompt
        prompt = f"""As an expert SEO consultant, analyze this website and provide specific recommendations.

Website Analysis Data:
- URL: {page_data.get('url', 'N/A')}
- Title: {page_data.get('title', 'N/A')} (Length: {len(page_data.get('title', ''))} chars)
- Meta Description: {page_data.get('meta_description', 'N/A')} (Length: {len(page_data.get('meta_description', ''))} chars)
- Content Word Count: {seo_analysis.get('content_analysis', {}).get('word_count', 0)}
- Overall SEO Score: {seo_analysis.get('score', 0)}/100

Issues Identified:
{issues_text}

Please provide recommendations in this JSON format:
{{
  "summary": "Brief summary of the analysis",
  "recommendations": [
    {{"title": "Recommendation 1", "description": "Detailed description", "priority": "high/medium/low"}}
  ],
  "quick_wins": ["Quick fix 1", "Quick fix 2"],
  "long_term_strategies": ["Long-term strategy 1", "Long-term strategy 2"]
}}

Response:"""
        
        return prompt
    
    def _create_chat_context(self, context: Dict) -> str:
        """Create chat context"""
        if not context:
            return ""
        
        context_str = f"Context: Analyzing website {context.get('url', 'N/A')}"
        if 'score' in context:
            context_str += f" with SEO score {context['score']}/100"
        return context_str
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse response from Ollama"""
        try:
            # Try to extract JSON from the response
            # Look for JSON content
            import re
            
            # Try to find JSON object
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, response_text)
            
            if match:
                json_str = match.group()
                data = json.loads(json_str)
                return data
            else:
                # If no JSON found, create a simple response
                return {
                    'summary': response_text[:300],
                    'recommendations': [
                        {
                            'title': 'Review Analysis',
                            'description': 'Review the detailed analysis above',
                            'priority': 'medium'
                        }
                    ],
                    'quick_wins': ['Check meta tags', 'Review content'],
                    'long_term_strategies': ['Regular SEO audits', 'Content optimization']
                }
                
        except json.JSONDecodeError:
            print("Could not parse JSON response")
            return self._generate_fallback_recommendations({})
        except Exception as e:
            print(f"Error parsing response: {e}")
            return self._generate_fallback_recommendations({})
    
    def _generate_fallback_recommendations(self, seo_analysis: Dict) -> Dict:
        """Generate fallback recommendations when AI is not available"""
        
        # Extract issues for recommendations
        issues = []
        for category, data in seo_analysis.items():
            if isinstance(data, dict) and 'issues' in data:
                issues.extend(data['issues'][:3])  # Take first 3 issues
        
        # Create recommendations based on issues
        recommendations = []
        if issues:
            for i, issue in enumerate(issues[:5]):
                priority = 'high' if i < 2 else 'medium' if i < 4 else 'low'
                recommendations.append({
                    'title': f'Address Issue {i+1}',
                    'description': issue,
                    'priority': priority
                })
        else:
            # Default recommendations if no issues
            recommendations = [
                {
                    'title': 'Optimize Title Tag',
                    'description': 'Ensure title is 50-60 characters with primary keyword',
                    'priority': 'high'
                },
                {
                    'title': 'Improve Meta Description',
                    'description': 'Write compelling meta description of 120-160 characters',
                    'priority': 'high'
                },
                {
                    'title': 'Enhance Content',
                    'description': 'Aim for at least 300 words of quality, relevant content',
                    'priority': 'medium'
                }
            ]
        
        return {
            'summary': 'Based on technical SEO analysis, here are the key recommendations for improvement.',
            'recommendations': recommendations,
            'quick_wins': [
                'Fix meta tags if needed',
                'Add alt text to images without it',
                'Ensure fast page loading'
            ],
            'long_term_strategies': [
                'Regular content updates and optimization',
                'Build quality backlinks',
                'Monitor SEO performance regularly'
            ]
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []