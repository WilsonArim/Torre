import React from "react";

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
}

export default function Sparkline({
  data,
  width = 100,
  height = 30,
  color = "#3b82f6",
}: SparklineProps) {
  if (!data || data.length === 0) {
    return (
      <svg width={width} height={height} className="opacity-50">
        <rect
          width={width}
          height={height}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="1"
        />
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dy=".3em"
          fontSize="10"
          fill="#9ca3af"
        >
          No data
        </text>
      </svg>
    );
  }

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height}>
      <polyline fill="none" stroke={color} strokeWidth="2" points={points} />
    </svg>
  );
}
