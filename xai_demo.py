#!/usr/bin/env python3
"""
XAI Model & Analyst Feedback Demo
Demonstrates the complete Explainable AI system with MITRE ATT&CK integration and analyst feedback loop

Usage: python xai_demo.py
"""

import requests
import json
from datetime import datetime


class XAIDemo:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        
    def display_header(self, title):
        print("\n" + "=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
        
    def display_threat_analysis(self, threat_id):
        """Display complete threat analysis with XAI explanation and MITRE ATT&CK"""
        print(f"\n🔍 Analyzing Threat {threat_id}")
        print("-" * 40)
        
        response = requests.get(f"{self.base_url}/threats/{threat_id}")
        if response.status_code != 200:
            print(f"❌ Failed to get threat {threat_id}")
            return None
            
        threat = response.json()
        
        # Basic threat info
        print(f"📍 Threat: {threat['description']}")
        print(f"🌐 Source IP: {threat['ip']}")
        print(f"⚡ Severity: {threat['severity']}")
        print(f"📊 CVSS Score: {threat['cvss_score']}")
        
        # XAI Explanation
        xai = threat['ai_analysis']['xai_explanation']
        print(f"\n🧠 XAI Explanation:")
        print(f"   Reasoning: {xai['reasoning']}")
        print(f"   Confidence: {xai['confidence_score']}")
        print(f"   Decision Factors:")
        for factor in xai['decision_factors']:
            print(f"     • {factor}")
        
        # MITRE ATT&CK
        mitre = threat['mitre_attck']
        print(f"\n🎯 MITRE ATT&CK Mapping:")
        print(f"   Technique: {mitre['technique_id']} - {mitre['technique_name']}")
        print(f"   Tactic: {mitre['tactic']} ({mitre['tactic_id']})")
        print(f"   Description: {mitre['description']}")
        
        # Existing feedback
        feedback = threat.get('analyst_feedback')
        if feedback:
            print(f"\n📝 Existing Analyst Feedback:")
            print(f"   Type: {feedback['feedback_type']}")
            print(f"   Explanation: {feedback['explanation']}")
            print(f"   Confidence: {feedback['confidence_level']}/5")
        
        return threat
    
    def submit_feedback_example(self, threat_id, feedback_type="confirmation"):
        """Submit analyst feedback example"""
        print(f"\n📝 Submitting {feedback_type} feedback for Threat {threat_id}")
        
        if feedback_type == "confirmation":
            feedback_data = {
                "feedback_type": "confirmation",
                "explanation": "XAI explanation accurately identifies the threat and provides clear reasoning with good MITRE integration",
                "confidence_level": 5,
                "analyst_id": "demo_analyst"
            }
        elif feedback_type == "correction":
            feedback_data = {
                "feedback_type": "correction",
                "corrected_prediction": 9.5,
                "feature_corrections": '{"ip_reputation_weight": 0.5, "mitre_technique_weight": 0.4}',
                "explanation": "AI model should weight IP reputation higher for this attack type. MITRE technique indicates advanced persistent threat.",
                "confidence_level": 4,
                "analyst_id": "senior_analyst"
            }
        elif feedback_type == "feature_importance":
            feedback_data = {
                "feedback_type": "feature_importance",
                "feature_corrections": '{"severity_assessment_weight": 0.3, "behavioral_analysis_weight": 0.4}',
                "explanation": "Behavioral analysis should be weighted higher for this type of threat pattern",
                "confidence_level": 4,
                "analyst_id": "ml_specialist"
            }
        
        response = requests.post(
            f"{self.base_url}/threats/{threat_id}/feedback",
            json=feedback_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Feedback submitted successfully (ID: {result['feedback_id']})")
                print(f"   Analyst: {result['analyst_id']}")
                print(f"   Timestamp: {result['timestamp']}")
                return True
            else:
                print(f"❌ Feedback submission failed: {result.get('message')}")
        else:
            print(f"❌ API error: {response.status_code}")
        
        return False
    
    def display_feedback_analytics(self):
        """Display comprehensive feedback analytics"""
        print("\n📊 Analyst Feedback Analytics")
        print("-" * 40)
        
        response = requests.get(f"{self.base_url}/analyst/feedback/summary")
        if response.status_code != 200:
            print("❌ Failed to get feedback summary")
            return
            
        data = response.json()
        summary = data['summary']
        
        print(f"Total Feedback Records: {summary['total_feedback']}")
        print(f"Confirmations: {summary['confirmation_count']} ({summary['confirmation_count']/summary['total_feedback']*100:.1f}%)")
        print(f"Corrections: {summary['correction_count']} ({summary['correction_count']/summary['total_feedback']*100:.1f}%)")
        print(f"Feature Adjustments: {summary['feature_importance_count']}")
        print(f"Model Correction Rate: {summary['correction_rate']:.1f}%")
        
        print(f"\n🕒 Recent Feedback Activity:")
        for feedback in data['recent_feedback'][:5]:
            print(f"   Threat {feedback['threat_id']}: {feedback['feedback_type']} by {feedback['analyst_id']} (confidence: {feedback['confidence_level']}/5)")
    
    def demo_model_improvement_cycle(self):
        """Demonstrate the complete model improvement cycle"""
        self.display_header("XAI MODEL IMPROVEMENT CYCLE DEMO")
        
        # Step 1: Analyze a threat
        print("🔄 Step 1: AI Model Analysis")
        threat = self.display_threat_analysis(1)
        
        # Step 2: Analyst provides feedback
        print("\n🔄 Step 2: Analyst Feedback Collection")
        self.submit_feedback_example(1, "confirmation")
        
        # Step 3: Analyze another threat that needs correction
        print("\n🔄 Step 3: Model Correction Example")
        self.display_threat_analysis(4)
        self.submit_feedback_example(4, "correction")
        
        # Step 4: Feature importance adjustment
        print("\n🔄 Step 4: Feature Importance Adjustment")
        self.submit_feedback_example(2, "feature_importance")
        
        # Step 5: Analytics and insights
        print("\n🔄 Step 5: Feedback Analytics & Model Insights")
        self.display_feedback_analytics()
        
        print("\n💡 Model Improvement Insights:")
        print("   • High confirmation rate indicates good model performance")
        print("   • Correction feedback helps calibrate risk scoring")
        print("   • Feature importance feedback optimizes detection algorithms")
        print("   • MITRE ATT&CK integration provides tactical context")
        print("   • Continuous feedback loop enables model evolution")
    
    def demo_xai_capabilities(self):
        """Demonstrate XAI explanation capabilities"""
        self.display_header("XAI EXPLANATION CAPABILITIES")
        
        print("🧠 XAI Model provides:")
        print("   ✅ Clear reasoning for threat classification")
        print("   ✅ Confidence scores for predictions") 
        print("   ✅ Decision factor breakdown")
        print("   ✅ MITRE ATT&CK technique mapping")
        print("   ✅ Actionable recommendations")
        print("   ✅ Integration with analyst feedback")
        
        # Show examples with different threat types
        threat_examples = [1, 4, 10, 22]  # Different types: trojan, sql injection, port scan, phishing
        
        for threat_id in threat_examples:
            self.display_threat_analysis(threat_id)
            print()
    
    def run_complete_demo(self):
        """Run the complete XAI and analyst feedback demonstration"""
        print("🚀 Starting XAI Model & Analyst Feedback System Demo")
        print("🎯 This demo shows how the system works end-to-end")
        
        # Demo XAI capabilities
        self.demo_xai_capabilities()
        
        # Demo model improvement cycle
        self.demo_model_improvement_cycle()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETE")
        print("=" * 60)
        print("🎉 The XAI system is now fully operational with:")
        print("   • Advanced threat explanation capabilities")
        print("   • Complete MITRE ATT&CK framework integration")
        print("   • Real-time analyst feedback collection")
        print("   • Automated model improvement insights")
        print("   • Comprehensive analytics and reporting")
        print("\n📚 Use the frontend dashboard to interact with threats")
        print("🔗 Visit: http://localhost:3000/dashboard")


def main():
    demo = XAIDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()
