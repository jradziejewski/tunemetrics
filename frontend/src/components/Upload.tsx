import { useState } from "react";
import { analyzeAudio } from "../services/api";
import type { AnalysisResponse } from "../types";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;

    try {
      setLoading(true);
      setError(null);

      const data = await analyzeAudio(file);
      setResult(data);
    } catch (err) {
      console.log(err);
      setError("Failed to analyze audio");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Results</h3>
          <p>BPM: {result.tempoBpm}</p>

          {result.keyDetection && (
            <p>
              Key: {result.keyDetection.note} {result.keyDetection.key} (
              {result.keyDetection.confidence})
            </p>
          )}

          <p>
            Chromagram: {result.chromagram.pitchClasses.join(", ")}...{" "}
            {result.chromagram.meanEnergy}
          </p>
        </div>
      )}
    </div>
  );
}
