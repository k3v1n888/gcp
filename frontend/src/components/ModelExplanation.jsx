import React from 'react';

const FeatureImpact = ({ feature, value, impact }) => {
    const isPushingHigher = impact > 0;
    const color = isPushingHigher ? 'text-red-400' : 'text-green-400';
    const arrow = isPushingHigher ? '↑' : '↓';

    // Helper function to safely format numeric values
    const formatValue = (val) => {
        if (val === null || val === undefined) return 'N/A';
        if (typeof val === 'number') {
            if (isNaN(val) || !isFinite(val)) return '0';
            return val.toFixed(4);
        }
        return String(val);
    };

    return (
        <div className="flex justify-between items-center text-sm p-2 bg-slate-800 rounded">
            <span>{feature}: <span className="font-semibold">{formatValue(value)}</span></span>
            <span className={`${color} font-bold`}>{arrow} {formatValue(Math.abs(impact))}</span>
        </div>
    );
};

export default function ModelExplanation({ explanation }) {
    if (!explanation || !explanation.shap_values || !explanation.features) {
        return <p className="text-slate-400">Explanation data not available for this prediction.</p>;
    }

    // Helper function to safely handle numeric values
    const safeNumber = (val) => {
        if (val === null || val === undefined || isNaN(val) || !isFinite(val)) {
            return 0;
        }
        return val;
    };

    // Safely get base value
    const baseValue = safeNumber(explanation.base_value);

    // A simple way to pair features with their SHAP values for display
    const featureImpacts = Object.keys(explanation.features).map((key, index) => {
        const shapValue = explanation.shap_values[0] ? safeNumber(explanation.shap_values[0][index]) : 0;
        return {
            feature: key,
            value: explanation.features[key],
            impact: shapValue
        };
    }).sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));

    return (
        <div className="space-y-2">
            <p className="text-slate-400 text-sm mb-4">
                The model's base prediction value was {baseValue.toFixed(4)}.
                The following features had the largest impact on this prediction, either pushing the risk score higher (red arrow) or lower (green arrow).
            </p>
            {featureImpacts.slice(0, 5).map(fi => (
                <FeatureImpact key={fi.feature} {...fi} />
            ))}
        </div>
    );
}