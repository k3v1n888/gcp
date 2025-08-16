/*
 * Copyright (c) 2025 Kevin Zachary
 * All rights reserved.
 *
 * This software and associated documentation files (the "Software") are the 
 * exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
 * modification, or use of this software is strictly prohibited.
 *
 * For licensing inquiries, contact: kevin@zachary.com
 */

/*
 * Author: Kevin Zachary
 * Copyright: Sentient Spire
 */



import React, { useState } from 'react';

const AnalystFeedback = ({ explanation, threatId, existingFeedback, onFeedbackSubmitted }) => {
    const [feedbackType, setFeedbackType] = useState(existingFeedback?.feedback_type || 'confirmation');
    const [correctedPrediction, setCorrectedPrediction] = useState(
        existingFeedback?.corrected_prediction || explanation?.base_value || 0
    );
    const [featureCorrections, setFeatureCorrections] = useState(
        existingFeedback?.feature_corrections || {}
    );
    const [explanationText, setExplanationText] = useState(existingFeedback?.explanation || '');
    const [confidenceLevel, setConfidenceLevel] = useState(existingFeedback?.confidence_level || 3);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showForm, setShowForm] = useState(false);

    const handleFeatureCorrection = (featureName, newImpact) => {
        setFeatureCorrections(prev => ({
            ...prev,
            [featureName]: parseFloat(newImpact) || 0
        }));
    };

    const submitFeedback = async () => {
        setIsSubmitting(true);
        try {
            const response = await fetch(`/api/threats/${threatId}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feedback_type: feedbackType,
                    corrected_prediction: feedbackType === 'correction' ? correctedPrediction : null,
                    feature_corrections: Object.keys(featureCorrections).length > 0 ? featureCorrections : null,
                    explanation: explanationText,
                    confidence_level: confidenceLevel
                })
            });

            if (response.ok) {
                const result = await response.json();
                onFeedbackSubmitted?.(result);
                setShowForm(false);
                alert('Feedback submitted successfully! This will help improve the AI model.');
            } else {
                throw new Error('Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            alert('Error submitting feedback. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const baseValue = explanation?.base_value || 0;
    const features = explanation?.features || {};
    const shapValues = explanation?.shap_values?.[0] || [];

    return (
        <div className="mt-6 p-4 bg-slate-800 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-200">
                    🧠 Analyst Feedback & Model Improvement
                </h3>
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                    {existingFeedback ? 'Update Feedback' : 'Provide Feedback'}
                </button>
            </div>

            {existingFeedback && !showForm && (
                <div className="mb-4 p-3 bg-slate-700 rounded-lg">
                    <div className="text-sm text-slate-300">
                        <p><span className="font-medium">Previous Feedback:</span> {existingFeedback.feedback_type}</p>
                        {existingFeedback.explanation && (
                            <p className="mt-1"><span className="font-medium">Note:</span> {existingFeedback.explanation}</p>
                        )}
                        <p className="mt-1"><span className="font-medium">Confidence:</span> {existingFeedback.confidence_level}/5</p>
                    </div>
                </div>
            )}

            {showForm && (
                <div className="space-y-4">
                    {/* Feedback Type Selection */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Feedback Type
                        </label>
                        <select
                            value={feedbackType}
                            onChange={(e) => setFeedbackType(e.target.value)}
                            className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200"
                        >
                            <option value="confirmation">Confirm AI Assessment</option>
                            <option value="correction">Correct AI Assessment</option>
                            <option value="feature_importance">Adjust Feature Importance</option>
                        </select>
                    </div>

                    {/* Prediction Correction */}
                    {feedbackType === 'correction' && (
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Corrected Risk Score (Current: {baseValue.toFixed(4)})
                            </label>
                            <div className="flex items-center space-x-2">
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.01"
                                    value={correctedPrediction}
                                    onChange={(e) => setCorrectedPrediction(parseFloat(e.target.value))}
                                    className="flex-1"
                                />
                                <span className="text-slate-200 font-mono min-w-[80px]">
                                    {correctedPrediction.toFixed(4)}
                                </span>
                            </div>
                            <div className="text-xs text-slate-400 mt-1">
                                0.0 = No Risk, 0.5 = Medium Risk, 1.0 = Critical Risk
                            </div>
                        </div>
                    )}

                    {/* Feature Importance Corrections */}
                    {(feedbackType === 'feature_importance' || feedbackType === 'correction') && (
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Adjust Feature Importance
                            </label>
                            <div className="space-y-2 max-h-60 overflow-y-auto">
                                {Object.keys(features).map((featureName, index) => {
                                    const currentImpact = shapValues[index] || 0;
                                    const correctedImpact = featureCorrections[featureName] ?? currentImpact;
                                    
                                    return (
                                        <div key={featureName} className="flex items-center justify-between p-2 bg-slate-700 rounded">
                                            <span className="text-sm text-slate-300 flex-1">
                                                {featureName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                            </span>
                                            <div className="flex items-center space-x-2 ml-4">
                                                <span className="text-xs text-slate-400 min-w-[60px]">
                                                    Was: {currentImpact.toFixed(3)}
                                                </span>
                                                <input
                                                    type="range"
                                                    min="-0.2"
                                                    max="0.2"
                                                    step="0.001"
                                                    value={correctedImpact}
                                                    onChange={(e) => handleFeatureCorrection(featureName, e.target.value)}
                                                    className="w-24"
                                                />
                                                <span className="text-xs text-slate-200 font-mono min-w-[60px]">
                                                    {correctedImpact.toFixed(3)}
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Explanation */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Explanation (Optional)
                        </label>
                        <textarea
                            value={explanationText}
                            onChange={(e) => setExplanationText(e.target.value)}
                            placeholder="Explain your assessment or corrections..."
                            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 resize-none"
                            rows={3}
                        />
                    </div>

                    {/* Confidence Level */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Confidence Level
                        </label>
                        <div className="flex items-center space-x-2">
                            {[1, 2, 3, 4, 5].map(level => (
                                <button
                                    key={level}
                                    onClick={() => setConfidenceLevel(level)}
                                    className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                                        confidenceLevel >= level
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-slate-600 text-slate-400 hover:bg-slate-500'
                                    }`}
                                >
                                    {level}
                                </button>
                            ))}
                            <span className="text-sm text-slate-400 ml-2">
                                {confidenceLevel === 1 && 'Very Low'}
                                {confidenceLevel === 2 && 'Low'}
                                {confidenceLevel === 3 && 'Medium'}
                                {confidenceLevel === 4 && 'High'}
                                {confidenceLevel === 5 && 'Very High'}
                            </span>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex items-center justify-between pt-4 border-t border-slate-600">
                        <button
                            onClick={() => setShowForm(false)}
                            className="px-4 py-2 text-slate-400 hover:text-slate-200 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={submitFeedback}
                            disabled={isSubmitting}
                            className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                        >
                            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                        </button>
                    </div>
                </div>
            )}

            <div className="mt-4 text-xs text-slate-400">
                💡 Your feedback helps improve the AI model's accuracy and explainability for future threat assessments.
            </div>
        </div>
    );
};

export default AnalystFeedback;