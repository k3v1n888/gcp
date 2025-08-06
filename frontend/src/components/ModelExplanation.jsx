import React from 'react';
import AnalystFeedback from './AnalystFeedback';

const FeatureImpact = ({ feature, value, impact }) => {
    const isPushingHigher = impact > 0;
    const color = isPushingHigher ? 'text-red-400' : 'text-green-400';
    const bgColor = isPushingHigher ? 'bg-red-900/20' : 'bg-green-900/20';
    const borderColor = isPushingHigher ? 'border-red-500/30' : 'border-green-500/30';
    const arrow = isPushingHigher ? '↗' : '↘';
    const absImpact = Math.abs(impact);

    // Helper function to safely format numeric values
    const formatValue = (val) => {
        if (val === null || val === undefined) return 'N/A';
        if (typeof val === 'number') {
            if (isNaN(val) || !isFinite(val)) return '0';
            if (absImpact < 0.001 && absImpact > 0) {
                return val.toExponential(2);
            } else if (absImpact < 0.1) {
                return val.toFixed(4);
            } else {
                return val.toFixed(3);
            }
        }
        return String(val);
    };

    const formatFeatureValue = (val) => {
        if (val === null || val === undefined) return 'N/A';
        if (typeof val === 'number') {
            if (isNaN(val) || !isFinite(val)) return '0';
            return val.toFixed(2);
        }
        return String(val);
    };

    // Create a visual impact bar
    const impactPercentage = Math.min(100, (absImpact / 0.2) * 100); // Scale relative to 0.2 max impact

    return (
        <div className={`flex justify-between items-center text-sm p-3 rounded-lg border ${borderColor} ${bgColor}`}>
            <div className="flex-1">
                <div className="flex items-center justify-between">
                    <span className="text-slate-300 font-medium">
                        {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <span className="font-semibold ml-2 text-slate-100">
                        {formatFeatureValue(value)}
                    </span>
                </div>
                
                {/* Impact visualization bar */}
                {absImpact > 0.001 && (
                    <div className="mt-1 w-full bg-slate-700 rounded-full h-1">
                        <div 
                            className={`h-1 rounded-full ${isPushingHigher ? 'bg-red-400' : 'bg-green-400'}`}
                            style={{ width: `${impactPercentage}%` }}
                        />
                    </div>
                )}
            </div>
            
            <span className={`${color} font-bold ml-4 min-w-[100px] text-right flex items-center`}>
                <span className="mr-1">{arrow}</span>
                {formatValue(absImpact)}
            </span>
        </div>
    );
};

export default function ModelExplanation({ explanation, threatId, existingFeedback }) {
    if (!explanation) {
        return (
            <div className="text-slate-400 p-4 bg-slate-800 rounded-lg">
                <p>No explanation data available for this prediction.</p>
                <p className="text-sm mt-2">The AI model may not have generated explainability data for this threat.</p>
            </div>
        );
    }

    console.log('🔍 ModelExplanation received:', explanation);

    // Helper function to safely handle numeric values
    const safeNumber = (val) => {
        if (val === null || val === undefined || isNaN(val) || !isFinite(val)) {
            return 0;
        }
        return val;
    };

    // Safely get base value
    const baseValue = safeNumber(explanation.base_value);

    // Handle explanation data structure
    let featureImpacts = [];

    if (explanation.features && explanation.shap_values) {
        const features = explanation.features;
        const shapValues = Array.isArray(explanation.shap_values[0]) 
            ? explanation.shap_values[0] 
            : explanation.shap_values;
        
        const featureKeys = Object.keys(features);
        featureImpacts = featureKeys.map((key, index) => {
            const shapValue = index < shapValues.length ? safeNumber(shapValues[index]) : 0;
            return {
                feature: key,
                value: features[key],
                impact: shapValue
            };
        });
    }

    // Sort by absolute impact value (highest first)
    featureImpacts.sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

    // Check if we have meaningful impacts
    const hasNonZeroImpacts = featureImpacts.some(fi => Math.abs(fi.impact) > 0.001);
    const totalPositiveImpact = featureImpacts.filter(fi => fi.impact > 0).reduce((sum, fi) => sum + fi.impact, 0);
    const totalNegativeImpact = featureImpacts.filter(fi => fi.impact < 0).reduce((sum, fi) => sum + Math.abs(fi.impact), 0);

    if (featureImpacts.length === 0) {
        return (
            <div className="text-slate-400 p-4 bg-slate-800 rounded-lg">
                <p>⚠️ No feature impact data could be processed.</p>
                <details className="mt-3">
                    <summary className="cursor-pointer text-xs hover:text-slate-300">Show raw explanation data</summary>
                    <pre className="text-xs mt-2 bg-slate-900 p-3 rounded overflow-auto max-h-40 border border-slate-700">
                        {JSON.stringify(explanation, null, 2)}
                    </pre>
                </details>
            </div>
        );
    }

    const handleFeedbackSubmitted = (result) => {
        console.log('Feedback submitted:', result);
        // Optionally refresh the page or update state
        window.location.reload();
    };

    return (
        <div className="space-y-4">
            <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-slate-300">Model Base Prediction:</span>
                    <span className="font-mono text-slate-100 text-lg">{baseValue.toFixed(4)}</span>
                </div>
                
                {hasNonZeroImpacts && (
                    <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                        <div className="text-red-400">
                            <span className="font-medium">Risk Increasing:</span> +{totalPositiveImpact.toFixed(3)}
                        </div>
                        <div className="text-green-400">
                            <span className="font-medium">Risk Decreasing:</span> -{totalNegativeImpact.toFixed(3)}
                        </div>
                    </div>
                )}
                
                {hasNonZeroImpacts ? (
                    <p className="text-slate-400 text-sm mt-3">
                        Features are ranked by their impact on the final risk score. 
                        Red indicates factors that increase risk, green indicates factors that decrease risk.
                    </p>
                ) : (
                    <p className="text-yellow-400 text-sm mt-3">
                        ⚠️ All feature impacts are near zero. This may indicate an issue with the AI model's explanation service.
                    </p>
                )}
            </div>
            
            <div className="space-y-2">
                {featureImpacts.slice(0, hasNonZeroImpacts ? 8 : 6).map((fi, index) => (
                    <FeatureImpact key={`${fi.feature}-${index}`} {...fi} />
                ))}
            </div>
            
            {!hasNonZeroImpacts && (
                <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-slate-400 hover:text-slate-300 p-2 bg-slate-800 rounded">
                        🔍 Debug: Show raw explanation data
                    </summary>
                    <pre className="text-xs mt-2 bg-slate-900 p-3 rounded overflow-auto max-h-60 border border-slate-700">
                        {JSON.stringify(explanation, null, 2)}
                    </pre>
                </details>
            )}
            
            {/* Add the analyst feedback component */}
            <AnalystFeedback 
                explanation={explanation}
                threatId={threatId}
                existingFeedback={existingFeedback}
                onFeedbackSubmitted={handleFeedbackSubmitted}
            />
        </div>
    );
}