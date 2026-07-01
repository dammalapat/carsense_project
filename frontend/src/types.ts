/**
 * types.ts — Shared type definitions for CarSense frontend.
 *
 * These mirror the backend Pydantic models. Keeping them in sync
 * ensures type safety across the API boundary.
 */

// ── Car ────────────────────────────────────────────────────────────────

export interface Car {
  id: number;
  make: string;
  model: string;
  variant: string;
  year: number;
  segment: string;
  body_type: string;
  price_lakh_min: number;
  price_lakh_max: number;
  fuel_type: string;
  transmission: string;
  engine_cc: number | null;
  power_bhp: number | null;
  torque_nm: number | null;
  mileage_kmpl: number | null;
  range_km: number | null;
  seating: number;
  boot_space_l: number | null;
  ground_clearance_mm: number | null;
  safety_rating: number | null;
  airbags: number | null;
  features: string[];
  pros: string[];
  cons: string[];
  best_for: string[];
  image_url: string | null;
}

// ── Advisor ────────────────────────────────────────────────────────────

export interface UserNeeds {
  budget_min: number;
  budget_max: number;
  primary_use: string;
  family_size: number;
  priorities: string[];
  fuel_preference: string | null;
  transmission_preference: string | null;
  must_haves: string[];
  dealbreakers: string[];
}

export interface DimensionScores {
  value: number;
  safety: number;
  comfort: number;
  performance: number;
  fuel_efficiency: number;
  features: number;
}

export interface CarRecommendation {
  car_id: number;
  match_score: number;
  reasoning: string;
  pros: string[];
  cons: string[];
  scores: DimensionScores;
}

export interface RecommendationResponse {
  recommendations: CarRecommendation[];
  summary: string;
}

export interface CompareRequest {
  car_ids: number[];
  user_needs?: UserNeeds;
}

export interface CompareInsight {
  car_id: number;
  verdict: string;
  strengths_vs_others: string[];
  weaknesses_vs_others: string[];
}

export interface CompareResponse {
  insights: CompareInsight[];
  recommendation: string;
  summary: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
  user_needs?: UserNeeds;
  shortlisted_car_ids: number[];
}

// ── Filter options from API ────────────────────────────────────────────

export interface FilterOptions {
  segment: string[];
  fuel_type: string[];
  body_type: string[];
  transmission: string[];
  price_range: { min: number; max: number };
  seating_options: number[];
}

// ── Wizard step definitions ────────────────────────────────────────────

export type WizardStep = 'budget' | 'usage' | 'priorities' | 'preferences' | 'extras';

export const USAGE_OPTIONS = [
  { value: 'daily_commute', label: 'Daily Commute', desc: 'Office runs, errands, city driving', icon: '🏙️' },
  { value: 'family', label: 'Family Car', desc: 'School drops, weekend trips, groceries', icon: '👨‍👩‍👧‍👦' },
  { value: 'highway_touring', label: 'Highway & Touring', desc: 'Long drives, road trips, intercity', icon: '🛣️' },
  { value: 'enthusiast', label: 'Driving Enthusiast', desc: 'Performance, handling, the thrill', icon: '🏎️' },
  { value: 'city_driving', label: 'City Only', desc: 'Tight parking, traffic, short hops', icon: '🚦' },
  { value: 'off_road', label: 'Off-Road & Adventure', desc: 'Rough terrain, hills, unpaved roads', icon: '⛰️' },
] as const;

export const PRIORITY_OPTIONS = [
  { value: 'safety', label: 'Safety', icon: '🛡️' },
  { value: 'mileage', label: 'Fuel Efficiency', icon: '⛽' },
  { value: 'features', label: 'Features & Tech', icon: '📱' },
  { value: 'comfort', label: 'Comfort & Space', icon: '🛋️' },
  { value: 'performance', label: 'Performance', icon: '💨' },
  { value: 'resale_value', label: 'Resale Value', icon: '📈' },
  { value: 'low_maintenance', label: 'Low Maintenance', icon: '🔧' },
] as const;

export const FUEL_OPTIONS = [
  { value: 'no_preference', label: 'No Preference' },
  { value: 'Petrol', label: 'Petrol' },
  { value: 'Diesel', label: 'Diesel' },
  { value: 'Electric', label: 'Electric' },
  { value: 'Hybrid', label: 'Hybrid' },
] as const;

export const TRANSMISSION_OPTIONS = [
  { value: 'no_preference', label: 'No Preference' },
  { value: 'Automatic', label: 'Automatic' },
  { value: 'Manual', label: 'Manual' },
] as const;

export const MUST_HAVE_OPTIONS = [
  { value: 'sunroof', label: 'Sunroof' },
  { value: 'adas', label: 'ADAS / Safety Tech' },
  { value: '7_seats', label: '7 Seats' },
  { value: '4x4', label: '4x4 / AWD' },
  { value: 'ventilated_seats', label: 'Ventilated Seats' },
  { value: 'connected_car', label: 'Connected Car Tech' },
  { value: 'ev_only', label: 'Electric Only' },
] as const;
