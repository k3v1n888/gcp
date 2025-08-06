import React from 'react';

const FeatureImpact = ({ feature, value, impact }) => {
    const isPushingHigher = impact > 0;
    const color = isPushingHigher ? 'text-red-400' : 'text-green-400';
    const arrow = isPushingHigher ? '↑' : '↓';
    const absImpact = Math.abs(impact);

    // Helper function to safely format numeric values
    const formatValue = (val) => {
        if (val === null || val === undefined) return 'N/A';
        if (typeof val === 'number') {
            if (isNaN(val) || !isFinite(val)) return '0';
            // Show appropriate precision based on magnitude
            if (absImpact < 0.001 && absImpact > 0) {
                return val.toExponential(2);
            } else if (absImpact < 1) {
                return val.toFixed(4);
            } else {
                return val.toFixed(2);
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

    return (
        <div className="flex justify-between items-center text-sm p-3 bg-slate-800 rounded-lg border border-slate-700">
            <span className="flex-1">
                <span className="text-slate-300 font-medium">{feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span> 
                <span className="font-semibold ml-2 text-slate-100">{formatFeatureValue(value)}</span>
            </span>
            <span className={`${color} font-bold ml-4 min-w-[100px] text-right`}>
                {arrow} {formatValue(absImpact)}
            </span>
        </div>
    );
};

export default function ModelExplanation({ explanation }) {
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

    // Handle different possible structures of explanation data
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
    } else if (explanation.feature_importance && explanation.features) {
        // Alternative structure with feature_importance
        featureImpacts = Object.entries(explanation.feature_importance).map(([feature, impact]) => ({
            feature: feature,
            value: explanation.features[feature] || 'N/A',
            impact: safeNumber(impact)
        }));
    }

    // Sort by absolute impact value (highest first)
    featureImpacts.sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

    // Check if we have meaningful impacts
    const hasNonZeroImpacts = featureImpacts.some(fi => Math.abs(fi.impact) > 0.0001);
    const maxImpact = featureImpacts.length > 0 ? Math.abs(featureImpacts[0].impact) : 0;

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

    return (
        <div className="space-y-3">
            <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                <p className="text-slate-300 text-sm">
                    <span className="font-semibold">Model Base Prediction:</span>{' '}
                    <span className="font-mono text-slate-100">{baseValue.toFixed(4)}</span>
                </p>
                {hasNonZeroImpacts ? (
                    <p className="text-slate-400 text-sm mt-2">
                        The features below show how much each factor influenced the final risk assessment, 
                        either increasing (🔴) or decreasing (🟢) the threat score.
                    </p>
                ) : (
                    <p className="text-yellow-400 text-sm mt-2">
                        ⚠️ All feature impacts are near zero. This may indicate the model is using default predictions 
                        or there's an issue with the explanation generation.
                    </p>
                )}
            </div>
            
            <div className="space-y-2">
                {featureImpacts.slice(0, hasNonZeroImpacts ? 6 : 8).map((fi, index) => (
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
        </div>
    );
}