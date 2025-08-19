#!/usr/bin/env python3
"""
XAI Model Testing & Analyst Feedback Integration
Test the Explainable AI model and collect analyst feedback for continuous improvement

This script integrates with your existing analyst feedback database and MITRE ATT&CK framework.
"""

import asyncio
import json
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd


class XAITester:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.test_results = []
        self.feedback_data = []
        
    def get_threats(self) -> List[Dict]:
        """Get all threats from the API"""
        try:
            response = requests.get(f"{self.base_url}/threats")
            if response.status_code == 200:
                data = response.json()
                return data.get("threats", [])
            else:
                print(f"❌ Failed to get threats: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting threats: {e}")
            return []
    
    def get_threat_detail(self, threat_id: int) -> Dict:
        """Get detailed threat analysis including XAI explanation"""
        try:
            response = requests.get(f"{self.base_url}/threats/{threat_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get threat {threat_id}: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error getting threat detail: {e}")
            return {}
    
    def test_xai_explanation(self, threat_detail: Dict) -> Dict:
        """Test and analyze XAI explanation quality"""
        print(f"\n🔬 Testing XAI Explanation for Threat {threat_detail.get('id')}")
        
        xai = threat_detail.get("ai_analysis", {}).get("xai_explanation", {})
        mitre_info = threat_detail.get("mitre_attck", {})
        
        if not xai:
            print("⚠️  No XAI explanation found")
            return {"quality_score": 0, "issues": ["No XAI explanation available"]}
        
        # Test explanation quality
        quality_metrics = {
            "completeness": self._test_completeness(xai, mitre_info),
            "clarity": self._test_clarity(xai),
            "technical_accuracy": self._test_technical_accuracy(xai, threat_detail),
            "mitre_integration": self._test_mitre_integration(xai, mitre_info),
            "actionability": self._test_actionability(threat_detail)
        }
        
        overall_score = sum(quality_metrics.values()) / len(quality_metrics)
        
        print(f"📊 XAI Quality Metrics:")
        for metric, score in quality_metrics.items():
            print(f"   {metric}: {score:.2f}/1.0")
        print(f"📈 Overall Quality Score: {overall_score:.2f}/1.0")
        
        return {
            "quality_score": overall_score,
            "metrics": quality_metrics,
            "xai_data": xai,
            "mitre_data": mitre_info
        }
    
    def _test_completeness(self, xai: Dict, mitre: Dict) -> float:
        """Test if explanation covers all necessary components"""
        required_fields = ["reasoning", "decision_factors", "confidence_score"]
        present_fields = sum(1 for field in required_fields if field in xai and xai[field])
        
        # Bonus for MITRE integration
        mitre_bonus = 0.2 if mitre and "technique_id" in mitre else 0
        
        return min(1.0, (present_fields / len(required_fields)) + mitre_bonus)
    
    def _test_clarity(self, xai: Dict) -> float:
        """Test clarity of explanation"""
        reasoning = xai.get("reasoning", "")
        if not reasoning:
            return 0.0
        
        # Simple clarity metrics
        clarity_score = 0.0
        
        # Length check (not too short, not too long)
        if 50 <= len(reasoning) <= 500:
            clarity_score += 0.3
        
        # Technical term balance
        technical_terms = ["IP", "MITRE", "technique", "threat", "analysis", "detection"]
        term_count = sum(1 for term in technical_terms if term.lower() in reasoning.lower())
        if 2 <= term_count <= 5:
            clarity_score += 0.4
        
        # Structure check
        decision_factors = xai.get("decision_factors", [])
        if isinstance(decision_factors, list) and len(decision_factors) >= 3:
            clarity_score += 0.3
        
        return min(1.0, clarity_score)
    
    def _test_technical_accuracy(self, xai: Dict, threat_detail: Dict) -> float:
        """Test technical accuracy of explanation"""
        accuracy_score = 0.0
        
        # Confidence score should be realistic
        confidence = xai.get("confidence_score", 0)
        if 0.5 <= confidence <= 1.0:
            accuracy_score += 0.3
        
        # Decision factors should mention key threat attributes
        factors = " ".join(xai.get("decision_factors", []))
        threat_attrs = [threat_detail.get("severity", ""), threat_detail.get("ip", ""), threat_detail.get("threat_type", "")]
        
        for attr in threat_attrs:
            if attr and attr.lower() in factors.lower():
                accuracy_score += 0.2
        
        return min(1.0, accuracy_score)
    
    def _test_mitre_integration(self, xai: Dict, mitre: Dict) -> float:
        """Test MITRE ATT&CK integration quality"""
        if not mitre:
            return 0.0
        
        integration_score = 0.0
        
        # Check if MITRE technique is mentioned in reasoning
        reasoning = xai.get("reasoning", "")
        technique_id = mitre.get("technique_id", "")
        
        if technique_id and technique_id in reasoning:
            integration_score += 0.4
        
        # Check if tactic is mentioned
        tactic = mitre.get("tactic", "")
        if tactic and tactic.lower() in reasoning.lower():
            integration_score += 0.3
        
        # Check if MITRE context is in XAI
        if "mitre_context" in xai:
            integration_score += 0.3
        
        return min(1.0, integration_score)
    
    def _test_actionability(self, threat_detail: Dict) -> float:
        """Test if recommendations are actionable"""
        recommendations = threat_detail.get("ai_analysis", {}).get("recommended_actions", [])
        if not recommendations:
            return 0.0
        
        actionability_score = 0.0
        
        # Should have multiple recommendations
        if len(recommendations) >= 3:
            actionability_score += 0.4
        
        # Should contain specific actions
        action_keywords = ["block", "isolate", "monitor", "update", "implement"]
        for rec in recommendations:
            if any(keyword in rec.lower() for keyword in action_keywords):
                actionability_score += 0.1
        
        return min(1.0, actionability_score)
    
    def simulate_analyst_review(self, threat_id: int, test_result: Dict) -> Dict:
        """Simulate analyst review and generate feedback"""
        print(f"\n👨‍💻 Simulating Analyst Review for Threat {threat_id}")
        
        quality_score = test_result["quality_score"]
        
        # Simulate analyst satisfaction based on quality
        if quality_score >= 0.8:
            feedback_type = "confirmation"
            satisfaction = random.uniform(4.0, 5.0)
            analyst_notes = "XAI explanation is comprehensive and accurate. Good MITRE integration."
        elif quality_score >= 0.6:
            feedback_type = "feature_importance"
            satisfaction = random.uniform(3.0, 4.0)
            analyst_notes = "Explanation is adequate but could benefit from more detailed reasoning."
        else:
            feedback_type = "correction"
            satisfaction = random.uniform(1.0, 3.0)
            analyst_notes = "Explanation lacks clarity and technical depth. Needs improvement."
        
        # Generate feature corrections if needed
        feature_corrections = {}
        if feedback_type in ["correction", "feature_importance"]:
            # Simulate adjustments to key factors
            feature_corrections = {
                "ip_reputation_weight": random.uniform(0.1, 0.4),
                "mitre_technique_weight": random.uniform(0.2, 0.5),
                "severity_assessment_weight": random.uniform(0.1, 0.3)
            }
        
        feedback = {
            "threat_id": threat_id,
            "feedback_type": feedback_type,
            "original_prediction": quality_score,
            "corrected_prediction": min(1.0, quality_score + random.uniform(0.1, 0.3)) if feedback_type == "correction" else None,
            "feature_corrections": feature_corrections if feature_corrections else None,
            "explanation": analyst_notes,
            "confidence_level": int(satisfaction),
            "analyst_id": f"analyst_{random.randint(1, 5)}",
            "analysis_time_minutes": random.randint(5, 30),
            "used_explanation": quality_score > 0.3
        }
        
        print(f"📝 Analyst Feedback:")
        print(f"   Type: {feedback_type}")
        print(f"   Satisfaction: {satisfaction:.1f}/5.0")
        print(f"   Notes: {analyst_notes}")
        
        return feedback
    
    def submit_feedback_to_api(self, feedback: Dict) -> bool:
        """Submit analyst feedback to the API"""
        try:
            threat_id = feedback["threat_id"]
            response = requests.post(
                f"{self.base_url}/threats/{threat_id}/feedback",
                json=feedback,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ Feedback submitted successfully (ID: {result.get('feedback_id')})")
                    return True
                else:
                    print(f"❌ Feedback submission failed: {result.get('message')}")
                    return False
            else:
                print(f"❌ API error submitting feedback: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error submitting feedback: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive XAI testing with analyst feedback"""
        print("🚀 Starting Comprehensive XAI Model Testing")
        print("=" * 60)
        
        # Get all threats
        threats = self.get_threats()
        if not threats:
            print("❌ No threats found to test")
            return
        
        print(f"📊 Found {len(threats)} threats to analyze")
        
        for threat in threats[:10]:  # Test first 10 threats
            threat_id = threat.get("id")
            if not threat_id:
                continue
                
            print(f"\n🔍 Analyzing Threat {threat_id}: {threat.get('threat', 'Unknown')}")
            
            # Get detailed threat information
            threat_detail = self.get_threat_detail(threat_id)
            if not threat_detail:
                continue
            
            # Test XAI explanation
            test_result = self.test_xai_explanation(threat_detail)
            test_result["threat_id"] = threat_id
            test_result["threat_type"] = threat_detail.get("threat_type")
            test_result["severity"] = threat_detail.get("severity")
            
            self.test_results.append(test_result)
            
            # Simulate analyst feedback
            feedback = self.simulate_analyst_review(threat_id, test_result)
            self.feedback_data.append(feedback)
            
            # Submit feedback to API
            self.submit_feedback_to_api(feedback)
            
            print("-" * 40)
        
        # Generate final report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 XAI MODEL TESTING REPORT")
        print("=" * 60)
        
        if not self.test_results:
            print("❌ No test results available")
            return
        
        # Overall statistics
        avg_quality = sum(r["quality_score"] for r in self.test_results) / len(self.test_results)
        high_quality_count = sum(1 for r in self.test_results if r["quality_score"] >= 0.8)
        
        print(f"🎯 Overall Results:")
        print(f"   Total Threats Tested: {len(self.test_results)}")
        print(f"   Average Quality Score: {avg_quality:.2f}/1.0")
        print(f"   High Quality Explanations: {high_quality_count}/{len(self.test_results)} ({high_quality_count/len(self.test_results)*100:.1f}%)")
        
        # Quality metrics breakdown
        if self.test_results[0].get("metrics"):
            metrics_avg = {}
            for metric in ["completeness", "clarity", "technical_accuracy", "mitre_integration", "actionability"]:
                avg_score = sum(r["metrics"][metric] for r in self.test_results if "metrics" in r) / len(self.test_results)
                metrics_avg[metric] = avg_score
            
            print(f"\n📊 Quality Metrics Breakdown:")
            for metric, score in metrics_avg.items():
                print(f"   {metric.replace('_', ' ').title()}: {score:.2f}/1.0")
        
        # Analyst feedback summary
        if self.feedback_data:
            correction_rate = sum(1 for f in self.feedback_data if f["feedback_type"] == "correction") / len(self.feedback_data)
            avg_satisfaction = sum(f["confidence_level"] for f in self.feedback_data) / len(self.feedback_data)
            usage_rate = sum(1 for f in self.feedback_data if f["used_explanation"]) / len(self.feedback_data)
            
            print(f"\n👥 Analyst Feedback Summary:")
            print(f"   Total Feedback: {len(self.feedback_data)}")
            print(f"   Correction Rate: {correction_rate:.1%}")
            print(f"   Average Satisfaction: {avg_satisfaction:.1f}/5.0")
            print(f"   Explanation Usage Rate: {usage_rate:.1%}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if avg_quality < 0.6:
            print("   🔴 Critical: XAI explanations need significant improvement")
            print("   → Focus on completeness and technical accuracy")
        elif avg_quality < 0.8:
            print("   🟡 Moderate: XAI explanations are adequate but can be enhanced")
            print("   → Improve MITRE integration and clarity")
        else:
            print("   🟢 Good: XAI explanations are performing well")
            print("   → Continue monitoring and minor optimizations")
        
        if "mitre_integration" in metrics_avg and metrics_avg["mitre_integration"] < 0.7:
            print("   → Enhance MITRE ATT&CK technique integration")
        
        # Save results
        self.save_test_results()
    
    def save_test_results(self):
        """Save test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save test results
        with open(f"xai_test_results_{timestamp}.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Save feedback data
        with open(f"analyst_feedback_{timestamp}.json", "w") as f:
            json.dump(self.feedback_data, f, indent=2, default=str)
        
        print(f"\n💾 Results saved:")
        print(f"   📁 xai_test_results_{timestamp}.json")
        print(f"   📁 analyst_feedback_{timestamp}.json")


def main():
    """Main execution function"""
    tester = XAITester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main()
