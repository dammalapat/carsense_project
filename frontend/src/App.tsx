/**
 * App.tsx — Root component and state orchestrator for CarSense.
 *
 * Architecture: We use a simple state-lifting pattern instead of Redux/Zustand.
 * The app has 3 phases — Landing → Wizard → Results — and state flows downward.
 * This is intentional: for a focused flow like this, a state library adds
 * complexity without adding value.
 */

import { useState, useCallback, useEffect } from 'react';
import type { UserNeeds, CarRecommendation, RecommendationResponse, Car } from './types';
import { getRecommendations, fetchCar } from './api';

import Landing from './components/Landing';
import Wizard from './components/Wizard';
import Results from './components/Results';
import Header from './components/Header';

type Phase = 'landing' | 'wizard' | 'results';

// Generate a stable session ID for shortlisting
function getSessionId(): string {
  let id = sessionStorage.getItem('carsense_session');
  if (!id) {
    id = `cs_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    sessionStorage.setItem('carsense_session', id);
  }
  return id;
}

export default function App() {
  const [phase, setPhase] = useState<Phase>('landing');
  const [userNeeds, setUserNeeds] = useState<UserNeeds | null>(null);
  const [recommendations, setRecommendations] = useState<CarRecommendation[]>([]);
  const [recSummary, setRecSummary] = useState('');
  const [carDetails, setCarDetails] = useState<Record<number, Car>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(getSessionId);

  // Fetch full car details for recommended car IDs
  const loadCarDetails = useCallback(async (recs: CarRecommendation[]) => {
    const details: Record<number, Car> = {};
    await Promise.all(
      recs.map(async (rec) => {
        try {
          details[rec.car_id] = await fetchCar(rec.car_id);
        } catch (e) {
          console.error(`Failed to load car ${rec.car_id}:`, e);
        }
      })
    );
    setCarDetails(details);
  }, []);

  // Handle wizard completion → fire AI recommendation
  const handleWizardComplete = useCallback(async (needs: UserNeeds) => {
    setUserNeeds(needs);
    setLoading(true);
    setError(null);
    setPhase('results');

    try {
      const response: RecommendationResponse = await getRecommendations(needs);
      setRecommendations(response.recommendations);
      setRecSummary(response.summary);
      await loadCarDetails(response.recommendations);
    } catch (e) {
      console.error('Recommendation failed:', e);
      setError('Something went wrong getting recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [loadCarDetails]);

  // Reset to beginning
  const handleRestart = useCallback(() => {
    setPhase('landing');
    setUserNeeds(null);
    setRecommendations([]);
    setCarDetails({});
    setRecSummary('');
    setError(null);
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        phase={phase}
        onRestart={handleRestart}
        onBack={() => {
          if (phase === 'results') setPhase('wizard');
          else if (phase === 'wizard') setPhase('landing');
        }}
      />

      <main className="flex-1">
        {phase === 'landing' && (
          <Landing onStart={() => setPhase('wizard')} />
        )}

        {phase === 'wizard' && (
          <Wizard
            onComplete={handleWizardComplete}
            initialNeeds={userNeeds}
          />
        )}

        {phase === 'results' && (
          <Results
            loading={loading}
            error={error}
            recommendations={recommendations}
            carDetails={carDetails}
            summary={recSummary}
            userNeeds={userNeeds}
            sessionId={sessionId}
            onRetry={() => userNeeds && handleWizardComplete(userNeeds)}
          />
        )}
      </main>
    </div>
  );
}
