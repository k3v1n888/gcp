#!/usr/bin/env python3
"""
XAI Model Testing & Analyst Feedback System
Test the Explainable AI model and collect analyst feedback for improvement
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

class XAIModelTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.analyst_feedback = []
        
    def get_threats(self) -> List[Dict]:
        """Get all threats from the API"""
        try:
            response = requests.get(f"{self.base_url}/api/threats")
            if response.status_code == 200:
                return response.json().get('threats', [])
            else:
                print(f"❌ Failed to get threats: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting threats: {e}")
            return []
    
    def test_threat_explanation(self, threat_id: int) -> Dict[str, Any]:
        """Test XAI explanation for a specific threat"""
        print(f"\n🔍 Testing XAI explanation for threat ID: {threat_id}")
        
        try:
            # Get detailed threat analysis
            response = requests.get(f"{self.base_url}/api/threats/{threat_id}")
            
            if response.status_code != 200:
                return {"error": f"Failed to get threat details: {response.status_code}"}
            
            threat_data = response.json()
            
            # Extract XAI components
            xai_explanation = threat_data.get('xai_explanation', {})
            ai_recommendations = threat_data.get('ai_recommendations', [])
            
            # Test explanation quality
            test_result = {
                "threat_id": threat_id,
                "timestamp": datetime.now().isoformat(),
                "threat_description": threat_data.get('description', ''),
                "severity": threat_data.get('severity', ''),
                "source_ip": threat_data.get('source_ip', ''),
                
                # XAI Metrics
                "xai_present": bool(xai_explanation),
                "confidence_score": xai_explanation.get('confidence_score', 0),
                "decision_factors_count": len(xai_explanation.get('decision_factors', [])),
                "reasoning_quality": len(xai_explanation.get('reasoning', '').split()) > 10,
                "recommendations_count": len(ai_recommendations),
                
                # Quality Assessment
                "explanation_completeness": self._assess_explanation_completeness(xai_explanation),
                "recommendation_relevance": self._assess_recommendation_relevance(ai_recommendations, threat_data),
                "overall_score": 0  # Will be calculated
            }
            
            # Calculate overall score
            test_result["overall_score"] = self._calculate_overall_score(test_result)
            
            self.test_results.append(test_result)
            
            print(f"✅ XAI Test Complete:")
            print(f"   Confidence: {test_result['confidence_score']:.2f}")
            print(f"   Decision Factors: {test_result['decision_factors_count']}")
            print(f"   Recommendations: {test_result['recommendations_count']}")
            print(f"   Overall Score: {test_result['overall_score']:.2f}/10")
            
            return test_result
            
        except Exception as e:
            error_result = {"error": str(e), "threat_id": threat_id}
            print(f"❌ Error testing threat {threat_id}: {e}")
            return error_result
    
    def _assess_explanation_completeness(self, xai_explanation: Dict) -> float:
        """Assess how complete the XAI explanation is (0-10 scale)"""
        score = 0
        
        # Check for required components
        if xai_explanation.get('confidence_score'):
            score += 2
        if xai_explanation.get('decision_factors'):
            score += 3
        if xai_explanation.get('reasoning'):
            score += 2
        if len(xai_explanation.get('reasoning', '')) > 50:
            score += 2
        if xai_explanation.get('model_version'):
            score += 1
            
        return min(score, 10)
    
    def _assess_recommendation_relevance(self, recommendations: List[str], threat_data: Dict) -> float:
        """Assess how relevant the AI recommendations are (0-10 scale)"""
        if not recommendations:
            return 0
        
        score = 0
        threat_desc = threat_data.get('description', '').lower()
        severity = threat_data.get('severity', '').lower()
        
        # Check for relevant keywords in recommendations
        relevant_keywords = {
            'malware': ['quarantine', 'antivirus', 'scan', 'isolate'],
            'trojan': ['quarantine', 'scan', 'isolate', 'remove'],
            'scan': ['block', 'firewall', 'monitor', 'harden'],
            'email': ['block', 'filter', 'train', 'quarantine'],
            'phish': ['block', 'train', 'filter', 'domain']
        }
        
        for threat_type, keywords in relevant_keywords.items():
            if threat_type in threat_desc:
                for rec in recommendations:
                    for keyword in keywords:
                        if keyword.lower() in rec.lower():
                            score += 1
        
        # Severity-based recommendations
        if severity in ['high', 'critical']:
            for rec in recommendations:
                if any(word in rec.lower() for word in ['immediate', 'quarantine', 'isolate', 'block']):
                    score += 1
        
        return min(score, 10)
    
    def _calculate_overall_score(self, test_result: Dict) -> float:
        """Calculate overall XAI quality score"""
        weights = {
            'xai_present': 2.0,
            'confidence_score': 2.0,
            'explanation_completeness': 3.0,
            'recommendation_relevance': 2.0,
            'reasoning_quality': 1.0
        }
        
        score = 0
        if test_result['xai_present']:
            score += weights['xai_present']
        
        score += test_result['confidence_score'] * weights['confidence_score']
        score += (test_result['explanation_completeness'] / 10) * weights['explanation_completeness']
        score += (test_result['recommendation_relevance'] / 10) * weights['recommendation_relevance']
        
        if test_result['reasoning_quality']:
            score += weights['reasoning_quality']
        
        return score
    
    def simulate_analyst_feedback(self, threat_id: int, test_result: Dict) -> Dict:
        """Simulate analyst feedback on XAI explanations"""
        print(f"\n👥 Simulating analyst feedback for threat {threat_id}")
        
        # Simulate different analyst personas
        analyst_personas = [
            {"name": "Senior SOC Analyst", "experience": "expert", "focus": "accuracy"},
            {"name": "Junior Analyst", "experience": "beginner", "focus": "clarity"},
            {"name": "Threat Hunter", "experience": "expert", "focus": "completeness"},
            {"name": "Incident Responder", "experience": "intermediate", "focus": "actionability"}
        ]
        
        analyst = random.choice(analyst_personas)
        
        # Generate feedback based on test results
        feedback = {
            "analyst_id": f"analyst_{random.randint(1000, 9999)}",
            "analyst_profile": analyst,
            "threat_id": threat_id,
            "timestamp": datetime.now().isoformat(),
            "feedback_type": "xai_evaluation",
            
            # Ratings (1-5 scale)
            "ratings": {
                "explanation_clarity": self._generate_rating(test_result['explanation_completeness'], analyst['experience']),
                "recommendation_usefulness": self._generate_rating(test_result['recommendation_relevance'], analyst['experience']),
                "confidence_appropriateness": self._generate_confidence_rating(test_result['confidence_score']),
                "overall_satisfaction": 0  # Will be calculated
            },
            
            # Detailed feedback
            "comments": self._generate_analyst_comments(test_result, analyst),
            "suggestions": self._generate_improvement_suggestions(test_result, analyst),
            
            # Corrections
            "corrections": self._generate_corrections(test_result),
            
            # Usage patterns
            "used_explanation": random.choice([True, False]),
            "followed_recommendations": random.choice([True, True, False]),  # 66% follow recommendations
            "time_spent_minutes": random.randint(3, 15)
        }
        
        # Calculate overall satisfaction
        ratings = feedback['ratings']
        feedback['ratings']['overall_satisfaction'] = round(
            (ratings['explanation_clarity'] + 
             ratings['recommendation_usefulness'] + 
             ratings['confidence_appropriateness']) / 3, 1
        )
        
        self.analyst_feedback.append(feedback)
        
        print(f"✅ Analyst Feedback Generated:")
        print(f"   Analyst: {analyst['name']} ({analyst['experience']})")
        print(f"   Overall Satisfaction: {feedback['ratings']['overall_satisfaction']}/5")
        print(f"   Time Spent: {feedback['time_spent_minutes']} minutes")
        
        return feedback
    
    def _generate_rating(self, score: float, experience: str) -> float:
        """Generate analyst rating based on score and experience"""
        # Normalize score to 1-5 scale
        base_rating = (score / 10) * 5
        
        # Adjust based on analyst experience
        if experience == "expert":
            # Experts are more critical
            base_rating *= 0.9
        elif experience == "beginner":
            # Beginners are more generous
            base_rating *= 1.1
        
        # Add some randomness
        base_rating += random.uniform(-0.3, 0.3)
        
        return max(1.0, min(5.0, round(base_rating, 1)))
    
    def _generate_confidence_rating(self, confidence: float) -> float:
        """Rate confidence score appropriateness"""
        # Good confidence scores are between 0.7-0.95
        if 0.7 <= confidence <= 0.95:
            return random.uniform(4.0, 5.0)
        elif 0.6 <= confidence < 0.7:
            return random.uniform(3.0, 4.0)
        elif confidence > 0.95:
            return random.uniform(2.0, 3.0)  # Too high might be overconfident
        else:
            return random.uniform(1.0, 2.5)  # Too low
    
    def _generate_analyst_comments(self, test_result: Dict, analyst: Dict) -> List[str]:
        """Generate realistic analyst comments"""
        comments = []
        
        # Experience-based comments
        if analyst['experience'] == 'expert':
            if test_result['confidence_score'] > 0.9:
                comments.append("Confidence score seems artificially high. Need more nuanced uncertainty modeling.")
            if test_result['decision_factors_count'] < 4:
                comments.append("Would benefit from more detailed factor analysis.")
        
        elif analyst['experience'] == 'beginner':
            if not test_result['reasoning_quality']:
                comments.append("Need more detailed explanation to understand the reasoning.")
            comments.append("The recommendations are helpful for learning response procedures.")
        
        # Focus-based comments
        if analyst['focus'] == 'accuracy':
            if test_result['recommendation_relevance'] < 5:
                comments.append("Some recommendations don't seem relevant to this specific threat type.")
        
        elif analyst['focus'] == 'clarity':
            comments.append("The explanation could be more structured for easier understanding.")
        
        elif analyst['focus'] == 'completeness':
            comments.append("Missing correlation with other threats and historical context.")
        
        elif analyst['focus'] == 'actionability':
            comments.append("Recommendations need more specific steps and timelines.")
        
        return comments
    
    def _generate_improvement_suggestions(self, test_result: Dict, analyst: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if test_result['confidence_score'] < 0.7:
            suggestions.append("Improve confidence calibration with more training data")
        
        if test_result['decision_factors_count'] < 3:
            suggestions.append("Add more decision factors (network context, user behavior, asset criticality)")
        
        if test_result['recommendation_relevance'] < 7:
            suggestions.append("Make recommendations more threat-specific and contextual")
        
        suggestions.append("Add timeline estimates for recommended actions")
        suggestions.append("Include links to relevant playbooks and procedures")
        
        return suggestions
    
    def _generate_corrections(self, test_result: Dict) -> Dict:
        """Generate analyst corrections to improve the model"""
        corrections = {}
        
        # Severity corrections
        if test_result['severity'] == 'low' and test_result['confidence_score'] > 0.8:
            corrections['suggested_severity'] = 'medium'
            corrections['severity_reason'] = 'High confidence suggests more serious threat'
        
        # Confidence corrections
        if test_result['confidence_score'] > 0.95:
            corrections['suggested_confidence'] = 0.85
            corrections['confidence_reason'] = 'Overconfident - add uncertainty modeling'
        
        return corrections
    
    def run_comprehensive_test(self, max_threats: int = 10) -> Dict:
        """Run comprehensive XAI testing"""
        print("🚀 Starting Comprehensive XAI Model Testing")
        print("=" * 50)
        
        # Get threats
        threats = self.get_threats()
        if not threats:
            print("❌ No threats found to test")
            return {}
        
        print(f"📊 Found {len(threats)} threats, testing first {min(max_threats, len(threats))}")
        
        # Test each threat
        test_count = 0
        for threat in threats[:max_threats]:
            threat_id = threat.get('id')
            if threat_id:
                test_result = self.test_threat_explanation(threat_id)
                if 'error' not in test_result:
                    # Generate analyst feedback
                    self.simulate_analyst_feedback(threat_id, test_result)
                    test_count += 1
                
                time.sleep(0.5)  # Avoid overwhelming the API
        
        # Generate summary report
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        print("\n📋 Generating Test Report")
        print("=" * 30)
        
        if not self.test_results:
            return {"error": "No test results available"}
        
        # Calculate statistics
        df_tests = pd.DataFrame(self.test_results)
        df_feedback = pd.DataFrame(self.analyst_feedback)
        
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if 'error' not in r]),
                "average_overall_score": df_tests['overall_score'].mean(),
                "average_confidence": df_tests['confidence_score'].mean(),
                "average_completeness": df_tests['explanation_completeness'].mean(),
                "average_relevance": df_tests['recommendation_relevance'].mean()
            },
            
            "analyst_feedback_summary": {
                "total_feedback": len(self.analyst_feedback),
                "average_satisfaction": df_feedback['ratings'].apply(lambda x: x['overall_satisfaction']).mean(),
                "average_time_spent": df_feedback['time_spent_minutes'].mean(),
                "usage_rate": df_feedback['used_explanation'].mean() * 100,
                "recommendation_follow_rate": df_feedback['followed_recommendations'].mean() * 100
            },
            
            "model_performance": {
                "strengths": self._identify_strengths(df_tests, df_feedback),
                "weaknesses": self._identify_weaknesses(df_tests, df_feedback),
                "improvement_areas": self._get_improvement_areas(df_feedback)
            },
            
            "recommendations": self._generate_model_recommendations(df_tests, df_feedback)
        }
        
        # Print summary
        print(f"✅ Tests Completed: {report['test_summary']['total_tests']}")
        print(f"📊 Average XAI Score: {report['test_summary']['average_overall_score']:.2f}/10")
        print(f"👥 Analyst Satisfaction: {report['analyst_feedback_summary']['average_satisfaction']:.1f}/5")
        print(f"⏱️  Average Analysis Time: {report['analyst_feedback_summary']['average_time_spent']:.1f} minutes")
        print(f"📈 Explanation Usage Rate: {report['analyst_feedback_summary']['usage_rate']:.1f}%")
        
        return report
    
    def _identify_strengths(self, df_tests, df_feedback) -> List[str]:
        """Identify model strengths"""
        strengths = []
        
        if df_tests['confidence_score'].mean() > 0.8:
            strengths.append("High confidence in predictions")
        
        if df_tests['explanation_completeness'].mean() > 7:
            strengths.append("Comprehensive explanations")
        
        if df_feedback['ratings'].apply(lambda x: x['overall_satisfaction']).mean() > 3.5:
            strengths.append("Good analyst satisfaction")
        
        if df_feedback['used_explanation'].mean() > 0.7:
            strengths.append("High explanation utility")
        
        return strengths
    
    def _identify_weaknesses(self, df_tests, df_feedback) -> List[str]:
        """Identify model weaknesses"""
        weaknesses = []
        
        if df_tests['recommendation_relevance'].mean() < 6:
            weaknesses.append("Low recommendation relevance")
        
        if df_tests['decision_factors_count'].mean() < 3:
            weaknesses.append("Insufficient decision factors")
        
        if df_feedback['time_spent_minutes'].mean() > 10:
            weaknesses.append("Explanations take too long to analyze")
        
        if df_feedback['followed_recommendations'].mean() < 0.6:
            weaknesses.append("Low recommendation adoption")
        
        return weaknesses
    
    def _get_improvement_areas(self, df_feedback) -> List[str]:
        """Get improvement areas from analyst feedback"""
        all_suggestions = []
        for feedback in self.analyst_feedback:
            all_suggestions.extend(feedback.get('suggestions', []))
        
        # Count frequency of suggestions
        suggestion_counts = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
        
        # Return top suggestions
        return sorted(suggestion_counts.keys(), key=lambda x: suggestion_counts[x], reverse=True)[:5]
    
    def _generate_model_recommendations(self, df_tests, df_feedback) -> List[str]:
        """Generate recommendations for model improvement"""
        recommendations = []
        
        avg_confidence = df_tests['confidence_score'].mean()
        if avg_confidence > 0.9:
            recommendations.append("Implement uncertainty quantification to prevent overconfidence")
        elif avg_confidence < 0.7:
            recommendations.append("Improve model training data and feature engineering")
        
        if df_tests['recommendation_relevance'].mean() < 7:
            recommendations.append("Enhance threat-specific recommendation engine")
        
        if df_feedback['time_spent_minutes'].mean() > 8:
            recommendations.append("Simplify explanation structure and add visual aids")
        
        recommendations.append("Implement continuous learning from analyst feedback")
        recommendations.append("Add A/B testing for different explanation formats")
        
        return recommendations
    
    def save_results(self, filename: str = None):
        """Save test results and feedback to files"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xai_test_results_{timestamp}"
        
        # Save test results
        with open(f"{filename}_tests.json", 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Save analyst feedback
        with open(f"{filename}_feedback.json", 'w') as f:
            json.dump(self.analyst_feedback, f, indent=2)
        
        print(f"📁 Results saved to {filename}_tests.json and {filename}_feedback.json")

def main():
    """Main testing function"""
    print("🧠 XAI Model Testing & Analyst Feedback System")
    print("=" * 50)
    
    tester = XAIModelTester()
    
    # Run comprehensive test
    report = tester.run_comprehensive_test(max_threats=5)
    
    if report and 'error' not in report:
        print("\n📊 FINAL REPORT")
        print("=" * 20)
        print(json.dumps(report, indent=2))
        
        # Save results
        tester.save_results()
        
        print("\n🎯 Next Steps:")
        print("1. Review analyst feedback patterns")
        print("2. Implement suggested improvements")
        print("3. A/B test explanation formats")
        print("4. Set up continuous feedback collection")
        print("5. Monitor model performance over time")
    
    return tester, report

if __name__ == "__main__":
    tester, report = main()
