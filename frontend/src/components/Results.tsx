/**
 * Results.tsx — Recommendation results view.
 *
 * This is where the buyer gets their answer. Each car card shows:
 * - Match score with color coding
 * - AI-generated reasoning
 * - Radar chart of dimension scores
 * - Expandable pros/cons
 * - Add-to-compare toggle
 *
 * Plus: a floating compare bar and chat drawer.
 */

import { useState, useMemo } from 'react';
import {
  Loader2, AlertCircle, ChevronDown, ChevronUp,
  GitCompareArrows, MessageCircle, X, Star,
  Fuel, Gauge, Shield, Users, Box
} from 'lucide-react';
import type { CarRecommendation, Car, UserNeeds } from '../types';
import RadarChart from './RadarChart';
import CompareDrawer from './CompareDrawer';
import ChatPanel from './ChatPanel';

interface ResultsProps {
  loading: boolean;
  error: string | null;
  recommendations: CarRecommendation[];
  carDetails: Record<number, Car>;
  summary: string;
  userNeeds: UserNeeds | null;
  sessionId: string;
  onRetry: () => void;
}

function scoreColor(score: number): string {
  if (score >= 75) return 'bg-emerald-100 text-emerald-700 ring-emerald-200';
  if (score >= 55) return 'bg-amber-100 text-amber-700 ring-amber-200';
  return 'bg-red-100 text-red-600 ring-red-200';
}

function formatPrice(min: number, max: number): string {
  if (min === max) return `₹${min}L`;
  return `₹${min}–${max}L`;
}

export default function Results({
  loading, error, recommendations, carDetails, summary,
  userNeeds, sessionId, onRetry,
}: ResultsProps) {
  const [expandedCard, setExpandedCard] = useState<number | null>(null);
  const [compareIds, setCompareIds] = useState<Set<number>>(new Set());
  const [showCompare, setShowCompare] = useState(false);
  const [showChat, setShowChat] = useState(false);

  const compareCars = useMemo(() =>
    Array.from(compareIds).map((id) => carDetails[id]).filter(Boolean),
    [compareIds, carDetails]
  );

  const toggleCompare = (carId: number) => {
    setCompareIds((prev) => {
      const next = new Set(prev);
      if (next.has(carId)) {
        next.delete(carId);
      } else if (next.size < 4) {
        next.add(carId);
      }
      return next;
    });
  };

  // ── Loading state ──────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 px-4 text-center fade-in">
        <div className="w-16 h-16 rounded-2xl bg-brand-100 flex items-center justify-center mb-6">
          <Loader2 size={32} className="text-brand-600 animate-spin" />
        </div>
        <h2 className="font-display text-xl font-semibold text-surface-800 mb-2">
          Analyzing your needs...
        </h2>
        <p className="text-surface-500 max-w-sm">
          Our AI is matching your lifestyle against 30+ cars.
          This takes a few seconds.
        </p>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-24 px-4 text-center fade-in">
        <div className="w-16 h-16 rounded-2xl bg-red-100 flex items-center justify-center mb-6">
          <AlertCircle size={32} className="text-red-500" />
        </div>
        <h2 className="font-display text-xl font-semibold text-surface-800 mb-2">
          Something went wrong
        </h2>
        <p className="text-surface-500 max-w-sm mb-6">{error}</p>
        <button onClick={onRetry} className="btn-primary">
          Try again
        </button>
      </div>
    );
  }

  // ── Empty state ────────────────────────────────────────────────────
  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 px-4 text-center fade-in">
        <h2 className="font-display text-xl font-semibold text-surface-800 mb-2">
          No matches found
        </h2>
        <p className="text-surface-500 max-w-sm mb-6">
          Try widening your budget or relaxing some must-haves.
        </p>
        <button onClick={onRetry} className="btn-primary">
          Adjust preferences
        </button>
      </div>
    );
  }

  // ── Main results ───────────────────────────────────────────────────
  return (
    <div className="max-w-4xl mx-auto px-4 py-6 sm:py-10 pb-32">
      {/* Summary */}
      <div className="mb-8 fade-in">
        <h2 className="font-display text-2xl sm:text-3xl font-bold text-surface-800 mb-2">
          Your top matches
        </h2>
        <p className="text-surface-600">{summary}</p>
      </div>

      {/* Recommendation cards */}
      <div className="space-y-4">
        {recommendations.map((rec, index) => {
          const car = carDetails[rec.car_id];
          if (!car) return null;

          const isExpanded = expandedCard === rec.car_id;
          const isInCompare = compareIds.has(rec.car_id);

          return (
            <div
              key={rec.car_id}
              className="card overflow-hidden slide-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Card header */}
              <div className="p-5 sm:p-6">
                <div className="flex items-start gap-4">
                  {/* Match score */}
                  <div className={`score-badge ring-2 shrink-0 ${scoreColor(rec.match_score)}`}>
                    {rec.match_score}
                  </div>

                  {/* Car info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="font-display font-semibold text-lg text-surface-800 leading-tight">
                          {car.make} {car.model}
                        </h3>
                        <p className="text-sm text-surface-500 mt-0.5">{car.variant}</p>
                      </div>
                      <span className="font-display font-semibold text-brand-700 whitespace-nowrap">
                        {formatPrice(car.price_lakh_min, car.price_lakh_max)}
                      </span>
                    </div>

                    {/* Quick specs */}
                    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-sm text-surface-600">
                      {car.fuel_type !== 'Electric' && car.mileage_kmpl && (
                        <span className="flex items-center gap-1">
                          <Fuel size={14} className="text-surface-400" />
                          {car.mileage_kmpl} km/l
                        </span>
                      )}
                      {car.fuel_type === 'Electric' && car.range_km && (
                        <span className="flex items-center gap-1">
                          <Fuel size={14} className="text-surface-400" />
                          {car.range_km} km range
                        </span>
                      )}
                      {car.power_bhp && (
                        <span className="flex items-center gap-1">
                          <Gauge size={14} className="text-surface-400" />
                          {car.power_bhp} bhp
                        </span>
                      )}
                      {car.safety_rating && (
                        <span className="flex items-center gap-1">
                          <Shield size={14} className="text-surface-400" />
                          {car.safety_rating}★ safety
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Users size={14} className="text-surface-400" />
                        {car.seating} seats
                      </span>
                      {car.boot_space_l && (
                        <span className="flex items-center gap-1">
                          <Box size={14} className="text-surface-400" />
                          {car.boot_space_l}L boot
                        </span>
                      )}
                    </div>

                    {/* AI reasoning */}
                    <p className="mt-3 text-sm text-surface-700 leading-relaxed">
                      {rec.reasoning}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 mt-4 ml-16">
                  <button
                    onClick={() => setExpandedCard(isExpanded ? null : rec.car_id)}
                    className="btn-ghost text-sm"
                  >
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    {isExpanded ? 'Less' : 'More details'}
                  </button>
                  <button
                    onClick={() => toggleCompare(rec.car_id)}
                    className={`btn-ghost text-sm ${isInCompare ? 'text-brand-600 bg-brand-50' : ''}`}
                  >
                    <GitCompareArrows size={16} />
                    {isInCompare ? 'In compare' : 'Compare'}
                  </button>
                </div>
              </div>

              {/* Expanded details */}
              {isExpanded && (
                <div className="border-t border-surface-200 p-5 sm:p-6 bg-surface-50 fade-in">
                  <div className="grid sm:grid-cols-2 gap-6">
                    {/* Radar chart */}
                    <div className="flex flex-col items-center">
                      <h4 className="text-sm font-medium text-surface-600 mb-3">Score breakdown</h4>
                      <RadarChart scores={rec.scores} />
                    </div>

                    {/* Pros & Cons */}
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-emerald-700 mb-2">
                          What works for you
                        </h4>
                        <ul className="space-y-1.5">
                          {rec.pros.map((pro, i) => (
                            <li key={i} className="text-sm text-surface-700 flex gap-2">
                              <span className="text-emerald-500 shrink-0">+</span>
                              {pro}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-amber-700 mb-2">
                          Watch out for
                        </h4>
                        <ul className="space-y-1.5">
                          {rec.cons.map((con, i) => (
                            <li key={i} className="text-sm text-surface-700 flex gap-2">
                              <span className="text-amber-500 shrink-0">–</span>
                              {con}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Features list */}
                      <div>
                        <h4 className="text-sm font-medium text-surface-600 mb-2">Key features</h4>
                        <div className="flex flex-wrap gap-1.5">
                          {car.features.slice(0, 6).map((f) => (
                            <span
                              key={f}
                              className="px-2.5 py-1 rounded-md bg-surface-200 text-surface-600 text-xs font-medium"
                            >
                              {f}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Floating Compare Bar ──────────────────────────────────────── */}
      {compareIds.size >= 2 && (
        <div className="fixed bottom-0 left-0 right-0 bg-surface-0 border-t border-surface-200 shadow-lg z-40 fade-in">
          <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-surface-600">
              <GitCompareArrows size={18} className="text-brand-600" />
              <span className="font-medium">{compareIds.size} cars selected</span>
              <span className="text-surface-400">
                ({compareCars.map((c) => `${c.make} ${c.model}`).join(', ')})
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCompareIds(new Set())}
                className="btn-ghost text-sm"
              >
                Clear
              </button>
              <button
                onClick={() => setShowCompare(true)}
                className="btn-primary text-sm"
              >
                Compare now
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Chat FAB ──────────────────────────────────────────────────── */}
      <button
        onClick={() => setShowChat(true)}
        className="fixed bottom-20 right-4 sm:bottom-6 sm:right-6 w-14 h-14 rounded-full bg-brand-600 text-white shadow-lg shadow-brand-600/30 flex items-center justify-center hover:bg-brand-700 transition-colors z-30"
        title="Ask the AI advisor"
      >
        <MessageCircle size={24} />
      </button>

      {/* ── Compare Drawer ────────────────────────────────────────────── */}
      {showCompare && (
        <CompareDrawer
          cars={compareCars}
          recommendations={recommendations}
          userNeeds={userNeeds}
          onClose={() => setShowCompare(false)}
        />
      )}

      {/* ── Chat Panel ────────────────────────────────────────────────── */}
      {showChat && (
        <ChatPanel
          userNeeds={userNeeds}
          shortlistedCarIds={Array.from(compareIds)}
          onClose={() => setShowChat(false)}
        />
      )}
    </div>
  );
}
