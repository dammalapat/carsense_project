/**
 * RadarChart.tsx — SVG radar chart for car scoring dimensions.
 *
 * This is the "signature" visual of CarSense. Instead of showing
 * raw numbers, we visualize how a car scores on dimensions the
 * buyer cares about. Pure SVG, no dependencies.
 *
 * 6 axes: Value, Safety, Comfort, Performance, Fuel Efficiency, Features
 */

import type { DimensionScores } from '../types';

interface RadarChartProps {
  scores: DimensionScores;
  size?: number;
  color?: string;
}

const DIMENSIONS: { key: keyof DimensionScores; label: string }[] = [
  { key: 'value', label: 'Value' },
  { key: 'safety', label: 'Safety' },
  { key: 'comfort', label: 'Comfort' },
  { key: 'performance', label: 'Power' },
  { key: 'fuel_efficiency', label: 'Efficiency' },
  { key: 'features', label: 'Features' },
];

export default function RadarChart({ scores, size = 180, color = '#4263eb' }: RadarChartProps) {
  const cx = size / 2;
  const cy = size / 2;
  const maxR = size * 0.38;
  const n = DIMENSIONS.length;
  const angleStep = (Math.PI * 2) / n;

  // Convert a score (0-100) to a point on the radar
  const scoreToPoint = (score: number, index: number): [number, number] => {
    const angle = angleStep * index - Math.PI / 2; // start from top
    const r = (score / 100) * maxR;
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
  };

  // Build the polygon path for the scores
  const points = DIMENSIONS.map((dim, i) => scoreToPoint(scores[dim.key], i));
  const polygonPath = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0]},${p[1]}`).join(' ') + 'Z';

  // Grid circles
  const gridLevels = [25, 50, 75, 100];

  return (
    <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} className="select-none">
      {/* Grid circles */}
      {gridLevels.map((level) => (
        <circle
          key={level}
          cx={cx}
          cy={cy}
          r={(level / 100) * maxR}
          fill="none"
          stroke="#e9ecef"
          strokeWidth={1}
        />
      ))}

      {/* Axis lines + labels */}
      {DIMENSIONS.map((dim, i) => {
        const angle = angleStep * i - Math.PI / 2;
        const endX = cx + maxR * Math.cos(angle);
        const endY = cy + maxR * Math.sin(angle);
        const labelR = maxR + 16;
        const lx = cx + labelR * Math.cos(angle);
        const ly = cy + labelR * Math.sin(angle);

        return (
          <g key={dim.key}>
            <line
              x1={cx}
              y1={cy}
              x2={endX}
              y2={endY}
              stroke="#dee2e6"
              strokeWidth={1}
            />
            <text
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-surface-500"
              fontSize={9}
              fontWeight={500}
              fontFamily="Inter, system-ui, sans-serif"
            >
              {dim.label}
            </text>
          </g>
        );
      })}

      {/* Score polygon */}
      <path
        d={polygonPath}
        fill={color}
        fillOpacity={0.15}
        stroke={color}
        strokeWidth={2}
        strokeLinejoin="round"
        className="radar-polygon"
      />

      {/* Score dots */}
      {points.map((p, i) => (
        <circle
          key={i}
          cx={p[0]}
          cy={p[1]}
          r={3.5}
          fill={color}
          stroke="white"
          strokeWidth={1.5}
        />
      ))}
    </svg>
  );
}
