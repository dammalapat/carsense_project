/**
 * api.ts — Typed API client for CarSense backend.
 *
 * All API calls go through this module. In development, Vite proxies
 * /api/* to the FastAPI backend. In production, set VITE_API_URL.
 */

import type {
  Car, UserNeeds, RecommendationResponse,
  CompareRequest, CompareResponse,
  ChatMessage, FilterOptions,
} from './types';

const BASE = import.meta.env.VITE_API_URL || '';

// ---------------------------------------------------------------------------
// Generic fetch wrapper with error handling
// ---------------------------------------------------------------------------

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Car endpoints
// ---------------------------------------------------------------------------

export async function fetchCars(filters?: Record<string, string | number>): Promise<Car[]> {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        params.append(k, String(v));
      }
    });
  }
  const qs = params.toString();
  return request<Car[]>(`/api/cars${qs ? `?${qs}` : ''}`);
}

export async function fetchCar(id: number): Promise<Car> {
  return request<Car>(`/api/cars/${id}`);
}

export async function fetchFilterOptions(): Promise<FilterOptions> {
  return request<FilterOptions>('/api/filters');
}

// ---------------------------------------------------------------------------
// Advisor endpoints
// ---------------------------------------------------------------------------

export async function getRecommendations(needs: UserNeeds): Promise<RecommendationResponse> {
  return request<RecommendationResponse>('/api/advisor/recommend', {
    method: 'POST',
    body: JSON.stringify(needs),
  });
}

export async function compareCars(req: CompareRequest): Promise<CompareResponse> {
  return request<CompareResponse>('/api/advisor/compare', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function chatWithAdvisor(
  message: string,
  history: ChatMessage[],
  userNeeds?: UserNeeds,
  shortlistedCarIds: number[] = [],
): Promise<{ reply: string }> {
  return request<{ reply: string }>('/api/advisor/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      history,
      user_needs: userNeeds,
      shortlisted_car_ids: shortlistedCarIds,
    }),
  });
}

// ---------------------------------------------------------------------------
// Shortlist endpoints
// ---------------------------------------------------------------------------

export async function addToShortlist(sessionId: string, carId: number): Promise<void> {
  await request('/api/shortlist', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, car_id: carId }),
  });
}

export async function removeFromShortlist(sessionId: string, carId: number): Promise<void> {
  await request(`/api/shortlist/${sessionId}/${carId}`, { method: 'DELETE' });
}

export async function fetchShortlist(sessionId: string): Promise<Car[]> {
  return request<Car[]>(`/api/shortlist/${sessionId}`);
}
