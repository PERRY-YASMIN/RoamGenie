import { useEffect, useState } from "react";

const PARTICLES = Array.from({ length: 64 }, (_, index) => ({
  left: `${(index * 37) % 108 - 4}%`,
  delay: `${(index % 13) * -1.65}s`,
  duration: `${12 + (index % 7) * 1.8}s`,
  size: `${4 + (index % 5) * 1.6}px`,
  depth: `${0.38 + (index % 6) * 0.12}`,
  sway: `${18 + (index % 6) * 7}vw`,
  spin: `${index % 2 ? 1 : -1}`,
  rise: `${(index % 4) * 7}vh`,
}));

export default function ImmersiveScene({ environment, scrollProgress = 0 }) {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const query = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!query) return undefined;
    const update = () => setReducedMotion(query.matches);
    update();
    query.addEventListener?.("change", update);
    return () => query.removeEventListener?.("change", update);
  }, []);

  return (
    <div
      className={`immersive-scene environment-${environment.key} terrain-${environment.terrain}`}
      style={{
        "--scene-progress": reducedMotion ? 0 : scrollProgress,
        "--scene-image": `url("/fuji-sakura-dawn.jpg"), url("${environment.image}")`,
      }}
      aria-hidden="true"
    >
      <div className="scene-sky" />
      <div className="scene-clouds" />
      <div className="scene-mountain" />
      <div className="scene-lake" />
      <div className="scene-hills" />
      <div className="scene-branch scene-branch-left" />
      <div className="scene-branch scene-branch-right" />
      <div className="scene-mist" />
      <div className="scene-wind-streams">
        <i /><i /><i /><i /><i />
      </div>
      <div className="scene-petals">
        {PARTICLES.map((petal, index) => (
          <i
            key={index}
            style={{
              "--petal-left": petal.left,
              "--petal-delay": petal.delay,
              "--petal-duration": petal.duration,
              "--petal-size": petal.size,
              "--petal-depth": petal.depth,
              "--petal-sway": petal.sway,
              "--petal-spin": petal.spin,
              "--petal-rise": petal.rise,
            }}
          />
        ))}
      </div>
      <div className="scene-vignette" />
    </div>
  );
}