/**
 * Wizard.tsx — Multi-step needs discovery flow.
 *
 * Product design decision: We ask about LIFESTYLE, not specs. A confused
 * buyer doesn't know they want a 1.5L turbo — they know they need
 * "something for highway overtakes." The AI translates lifestyle to specs.
 *
 * 5 steps: Budget → Usage → Priorities → Preferences → Extras
 * Each step is a single focused question with tappable options.
 */

import { useState, useCallback } from 'react';
import { ArrowRight, ArrowLeft, Sparkles } from 'lucide-react';
import type { UserNeeds, WizardStep } from '../types';
import {
  USAGE_OPTIONS, PRIORITY_OPTIONS,
  FUEL_OPTIONS, TRANSMISSION_OPTIONS, MUST_HAVE_OPTIONS,
} from '../types';

interface WizardProps {
  onComplete: (needs: UserNeeds) => void;
  initialNeeds: UserNeeds | null;
}

const STEPS: WizardStep[] = ['budget', 'usage', 'priorities', 'preferences', 'extras'];

const BUDGET_PRESETS = [
  { min: 3, max: 8, label: '₹3–8L', desc: 'Entry segment' },
  { min: 8, max: 15, label: '₹8–15L', desc: 'Popular segment' },
  { min: 15, max: 25, label: '₹15–25L', desc: 'Mid-premium' },
  { min: 25, max: 55, label: '₹25L+', desc: 'Premium' },
];

export default function Wizard({ onComplete, initialNeeds }: WizardProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const step = STEPS[stepIndex];

  // Form state
  const [budgetMin, setBudgetMin] = useState(initialNeeds?.budget_min ?? 8);
  const [budgetMax, setBudgetMax] = useState(initialNeeds?.budget_max ?? 15);
  const [customBudget, setCustomBudget] = useState(false);
  const [primaryUse, setPrimaryUse] = useState(initialNeeds?.primary_use ?? '');
  const [familySize, setFamilySize] = useState(initialNeeds?.family_size ?? 4);
  const [priorities, setPriorities] = useState<string[]>(initialNeeds?.priorities ?? []);
  const [fuelPref, setFuelPref] = useState(initialNeeds?.fuel_preference ?? 'no_preference');
  const [transPref, setTransPref] = useState(initialNeeds?.transmission_preference ?? 'no_preference');
  const [mustHaves, setMustHaves] = useState<string[]>(initialNeeds?.must_haves ?? []);

  const canProceed = useCallback((): boolean => {
    switch (step) {
      case 'budget': return budgetMin > 0 && budgetMax > budgetMin;
      case 'usage': return primaryUse !== '';
      case 'priorities': return priorities.length >= 2;
      case 'preferences': return true; // optional
      case 'extras': return true; // optional
      default: return false;
    }
  }, [step, budgetMin, budgetMax, primaryUse, priorities]);

  const handleNext = useCallback(() => {
    if (stepIndex < STEPS.length - 1) {
      setStepIndex(stepIndex + 1);
    } else {
      // Submit
      onComplete({
        budget_min: budgetMin,
        budget_max: budgetMax,
        primary_use: primaryUse,
        family_size: familySize,
        priorities,
        fuel_preference: fuelPref === 'no_preference' ? null : fuelPref,
        transmission_preference: transPref === 'no_preference' ? null : transPref,
        must_haves: mustHaves,
        dealbreakers: [],
      });
    }
  }, [stepIndex, budgetMin, budgetMax, primaryUse, familySize, priorities, fuelPref, transPref, mustHaves, onComplete]);

  const handleBack = () => {
    if (stepIndex > 0) setStepIndex(stepIndex - 1);
  };

  const togglePriority = (val: string) => {
    setPriorities((prev) =>
      prev.includes(val) ? prev.filter((p) => p !== val) : [...prev, val]
    );
  };

  const toggleMustHave = (val: string) => {
    setMustHaves((prev) =>
      prev.includes(val) ? prev.filter((m) => m !== val) : [...prev, val]
    );
  };

  const isLastStep = stepIndex === STEPS.length - 1;

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 sm:py-12">
      {/* Step indicators */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {STEPS.map((_, i) => (
          <div
            key={i}
            className={`step-dot ${
              i === stepIndex ? 'step-dot-active' :
              i < stepIndex ? 'step-dot-complete' : ''
            }`}
          />
        ))}
      </div>

      {/* Step content */}
      <div className="fade-in" key={step}>
        {/* ── Budget ────────────────────────────────────────────────── */}
        {step === 'budget' && (
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-surface-800 mb-2">
              What's your budget?
            </h2>
            <p className="text-surface-500 mb-8">
              Pick a range. We'll show cars slightly above too — negotiation room.
            </p>

            <div className="grid grid-cols-2 gap-3 mb-6">
              {BUDGET_PRESETS.map((preset) => (
                <button
                  key={preset.label}
                  onClick={() => {
                    setBudgetMin(preset.min);
                    setBudgetMax(preset.max);
                    setCustomBudget(false);
                  }}
                  className={`chip text-left ${
                    !customBudget && budgetMin === preset.min && budgetMax === preset.max
                      ? 'chip-selected'
                      : ''
                  }`}
                >
                  <div className="font-display font-semibold text-lg">{preset.label}</div>
                  <div className="text-sm text-surface-500">{preset.desc}</div>
                </button>
              ))}
            </div>

            <button
              onClick={() => setCustomBudget(!customBudget)}
              className="text-sm text-brand-600 hover:text-brand-700 font-medium"
            >
              {customBudget ? 'Use presets' : 'Set custom range'}
            </button>

            {customBudget && (
              <div className="flex gap-4 mt-4 fade-in">
                <div className="flex-1">
                  <label className="text-sm text-surface-600 font-medium mb-1 block">
                    Min (₹ Lakhs)
                  </label>
                  <input
                    type="number"
                    value={budgetMin}
                    onChange={(e) => setBudgetMin(Number(e.target.value))}
                    className="input-field"
                    min={1}
                    max={100}
                  />
                </div>
                <div className="flex-1">
                  <label className="text-sm text-surface-600 font-medium mb-1 block">
                    Max (₹ Lakhs)
                  </label>
                  <input
                    type="number"
                    value={budgetMax}
                    onChange={(e) => setBudgetMax(Number(e.target.value))}
                    className="input-field"
                    min={budgetMin + 1}
                    max={150}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Usage ─────────────────────────────────────────────────── */}
        {step === 'usage' && (
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-surface-800 mb-2">
              What will you mostly use it for?
            </h2>
            <p className="text-surface-500 mb-8">
              Pick the one that best describes your typical week.
            </p>

            <div className="grid gap-3">
              {USAGE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setPrimaryUse(opt.value)}
                  className={`chip flex items-center gap-4 text-left ${
                    primaryUse === opt.value ? 'chip-selected' : ''
                  }`}
                >
                  <span className="text-2xl">{opt.icon}</span>
                  <div>
                    <div className="font-medium">{opt.label}</div>
                    <div className="text-sm text-surface-500">{opt.desc}</div>
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-6">
              <label className="text-sm text-surface-600 font-medium mb-2 block">
                How many people usually ride? ({familySize})
              </label>
              <input
                type="range"
                min={1}
                max={8}
                value={familySize}
                onChange={(e) => setFamilySize(Number(e.target.value))}
                className="w-full accent-brand-600"
              />
              <div className="flex justify-between text-xs text-surface-400 mt-1">
                <span>Just me</span>
                <span>Full family</span>
              </div>
            </div>
          </div>
        )}

        {/* ── Priorities ────────────────────────────────────────────── */}
        {step === 'priorities' && (
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-surface-800 mb-2">
              What matters most to you?
            </h2>
            <p className="text-surface-500 mb-8">
              Pick at least 2. Order matters — tap your top priority first.
            </p>

            <div className="grid grid-cols-2 gap-3">
              {PRIORITY_OPTIONS.map((opt) => {
                const idx = priorities.indexOf(opt.value);
                const isSelected = idx !== -1;
                return (
                  <button
                    key={opt.value}
                    onClick={() => togglePriority(opt.value)}
                    className={`chip relative text-center py-4 ${
                      isSelected ? 'chip-selected' : ''
                    }`}
                  >
                    {isSelected && (
                      <span className="absolute top-2 right-2 w-5 h-5 rounded-full bg-brand-500 text-white text-xs font-bold flex items-center justify-center">
                        {idx + 1}
                      </span>
                    )}
                    <span className="text-2xl block mb-1">{opt.icon}</span>
                    <span className="text-sm font-medium">{opt.label}</span>
                  </button>
                );
              })}
            </div>

            {priorities.length > 0 && (
              <p className="mt-4 text-sm text-surface-500">
                Your ranking:{' '}
                {priorities.map((p, i) => (
                  <span key={p}>
                    <span className="font-medium text-surface-700">
                      {PRIORITY_OPTIONS.find((o) => o.value === p)?.label}
                    </span>
                    {i < priorities.length - 1 ? ' → ' : ''}
                  </span>
                ))}
              </p>
            )}
          </div>
        )}

        {/* ── Preferences ──────────────────────────────────────────── */}
        {step === 'preferences' && (
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-surface-800 mb-2">
              Any preferences?
            </h2>
            <p className="text-surface-500 mb-8">
              Optional — skip if you're open to anything.
            </p>

            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium text-surface-700 mb-3 block">
                  Fuel type
                </label>
                <div className="flex flex-wrap gap-2">
                  {FUEL_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setFuelPref(opt.value)}
                      className={`chip text-sm ${
                        fuelPref === opt.value ? 'chip-selected' : ''
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-surface-700 mb-3 block">
                  Transmission
                </label>
                <div className="flex flex-wrap gap-2">
                  {TRANSMISSION_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setTransPref(opt.value)}
                      className={`chip text-sm ${
                        transPref === opt.value ? 'chip-selected' : ''
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Extras ────────────────────────────────────────────────── */}
        {step === 'extras' && (
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-bold text-surface-800 mb-2">
              Any must-haves?
            </h2>
            <p className="text-surface-500 mb-8">
              Features you won't compromise on. Skip if flexible.
            </p>

            <div className="flex flex-wrap gap-2">
              {MUST_HAVE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => toggleMustHave(opt.value)}
                  className={`chip text-sm ${
                    mustHaves.includes(opt.value) ? 'chip-selected' : ''
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            {mustHaves.length > 0 && (
              <p className="mt-4 text-sm text-surface-500">
                Must-haves: {mustHaves.map((m) =>
                  MUST_HAVE_OPTIONS.find((o) => o.value === m)?.label
                ).join(', ')}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-10 pt-6 border-t border-surface-200">
        <button
          onClick={handleBack}
          disabled={stepIndex === 0}
          className={`btn-ghost ${stepIndex === 0 ? 'opacity-0 pointer-events-none' : ''}`}
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <button
          onClick={handleNext}
          disabled={!canProceed()}
          className={`btn-primary ${!canProceed() ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isLastStep ? (
            <>
              <Sparkles size={18} />
              Find my cars
            </>
          ) : (
            <>
              Next
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
