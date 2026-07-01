/**
 * CompareDrawer.tsx — Side-by-side car comparison with AI insights.
 *
 * Renders as a full-screen overlay. Shows specs comparison AND
 * AI-generated insights about what actually matters in the comparison.
 */

import { useState, useEffect } from 'react';
import { X, Loader2, Sparkles } from 'lucide-react';
import type { Car, CarRecommendation, UserNeeds, CompareResponse } from '../types';
import { compareCars } from '../api';
import RadarChart from './RadarChart';

interface CompareDrawerProps {
  cars: Car[];
  recommendations: CarRecommendation[];
  userNeeds: UserNeeds | null;
  onClose: () => void;
}

const COMPARE_COLORS = ['#4263eb', '#12b886', '#fa5252', '#fd7e14'];

export default function CompareDrawer({
  cars, recommendations, userNeeds, onClose,
}: CompareDrawerProps) {
  const [aiInsights, setAiInsights] = useState<CompareResponse | null>(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  // Fetch AI comparison on mount
  useEffect(() => {
    const fetchInsights = async () => {
      setLoadingInsights(true);
      try {
        const response = await compareCars({
          car_ids: cars.map((c) => c.id),
          user_needs: userNeeds ?? undefined,
        });
        setAiInsights(response);
      } catch (e) {
        console.error('Compare failed:', e);
      } finally {
        setLoadingInsights(false);
      }
    };
    fetchInsights();
  }, [cars, userNeeds]);

  const getRecForCar = (carId: number) =>
    recommendations.find((r) => r.car_id === carId);

  return (
    <div className="fixed inset-0 z-50 bg-surface-900/50 backdrop-blur-sm flex items-end sm:items-center justify-center">
      <div className="bg-surface-0 w-full sm:max-w-5xl sm:rounded-2xl max-h-[90vh] overflow-y-auto shadow-2xl fade-in">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-surface-0 border-b border-surface-200 px-5 py-4 flex items-center justify-between">
          <h2 className="font-display font-bold text-lg text-surface-800">
            Compare {cars.length} cars
          </h2>
          <button
            onClick={onClose}
            className="btn-ghost p-2 -mr-2"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-5 sm:p-6 space-y-8">
          {/* ── AI Insights ─────────────────────────────────────────── */}
          <div className="bg-brand-50 rounded-xl p-5 border border-brand-100">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={18} className="text-brand-600" />
              <h3 className="font-display font-semibold text-brand-800">AI Comparison</h3>
            </div>

            {loadingInsights ? (
              <div className="flex items-center gap-2 text-brand-600">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-sm">Analyzing differences...</span>
              </div>
            ) : aiInsights ? (
              <div className="space-y-4">
                <p className="text-sm text-brand-900 font-medium">
                  {aiInsights.recommendation}
                </p>
                <p className="text-sm text-brand-700">{aiInsights.summary}</p>

                <div className="grid sm:grid-cols-2 gap-3 mt-4">
                  {aiInsights.insights.map((insight) => {
                    const car = cars.find((c) => c.id === insight.car_id);
                    if (!car) return null;
                    return (
                      <div key={insight.car_id} className="bg-surface-0 rounded-lg p-4 border border-brand-100">
                        <h4 className="font-semibold text-sm text-surface-800 mb-1">
                          {car.make} {car.model}
                        </h4>
                        <p className="text-xs text-surface-600 mb-3 italic">
                          {insight.verdict}
                        </p>
                        <div className="space-y-2">
                          {insight.strengths_vs_others.map((s, i) => (
                            <p key={`s${i}`} className="text-xs text-emerald-700 flex gap-1.5">
                              <span className="shrink-0">+</span> {s}
                            </p>
                          ))}
                          {insight.weaknesses_vs_others.map((w, i) => (
                            <p key={`w${i}`} className="text-xs text-amber-700 flex gap-1.5">
                              <span className="shrink-0">–</span> {w}
                            </p>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p className="text-sm text-brand-700">
                AI comparison unavailable. See the spec comparison below.
              </p>
            )}
          </div>

          {/* ── Radar Charts ────────────────────────────────────────── */}
          <div>
            <h3 className="font-display font-semibold text-surface-800 mb-4">
              Score breakdown
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {cars.map((car, i) => {
                const rec = getRecForCar(car.id);
                return (
                  <div key={car.id} className="flex flex-col items-center">
                    <h4 className="text-sm font-medium text-surface-700 mb-2 text-center">
                      {car.make} {car.model}
                    </h4>
                    {rec && (
                      <RadarChart
                        scores={rec.scores}
                        size={150}
                        color={COMPARE_COLORS[i]}
                      />
                    )}
                    {rec && (
                      <span
                        className="mt-2 text-lg font-display font-bold"
                        style={{ color: COMPARE_COLORS[i] }}
                      >
                        {rec.match_score}% match
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── Spec Table ──────────────────────────────────────────── */}
          <div>
            <h3 className="font-display font-semibold text-surface-800 mb-4">
              Specifications
            </h3>
            <div className="overflow-x-auto -mx-5 sm:mx-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-200">
                    <th className="text-left py-3 px-4 text-surface-500 font-medium w-32">Spec</th>
                    {cars.map((car) => (
                      <th key={car.id} className="text-left py-3 px-4 font-semibold text-surface-800">
                        {car.make} {car.model}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-100">
                  {([
                    ['Price', (c: Car) => `₹${c.price_lakh_min}–${c.price_lakh_max}L`],
                    ['Fuel', (c: Car) => c.fuel_type],
                    ['Transmission', (c: Car) => c.transmission],
                    ['Power', (c: Car) => c.power_bhp ? `${c.power_bhp} bhp` : '—'],
                    ['Torque', (c: Car) => c.torque_nm ? `${c.torque_nm} Nm` : '—'],
                    ['Mileage', (c: Car) => c.mileage_kmpl ? `${c.mileage_kmpl} km/l` : c.range_km ? `${c.range_km} km range` : '—'],
                    ['Safety', (c: Car) => c.safety_rating ? `${c.safety_rating}★ (${c.airbags} airbags)` : '—'],
                    ['Seating', (c: Car) => `${c.seating} seats`],
                    ['Boot', (c: Car) => c.boot_space_l ? `${c.boot_space_l}L` : '—'],
                    ['Ground Clearance', (c: Car) => c.ground_clearance_mm ? `${c.ground_clearance_mm}mm` : '—'],
                    ['Segment', (c: Car) => c.segment],
                  ] as [string, (c: Car) => string][]).map(([label, fn]) => (
                    <tr key={label} className="hover:bg-surface-50">
                      <td className="py-2.5 px-4 text-surface-500 font-medium">{label}</td>
                      {cars.map((car) => (
                        <td key={car.id} className="py-2.5 px-4 text-surface-700">
                          {fn(car)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
