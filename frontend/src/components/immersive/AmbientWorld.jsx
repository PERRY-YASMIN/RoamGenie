import { useEffect, useRef, useState } from "react";
import ImmersiveScene from "./ImmersiveScene";
import { getEnvironment } from "./environmentConfig";

export default function AmbientWorld({ showScene = true }) {
  const [soundOn, setSoundOn] = useState(false);
  const [activeEnv, setActiveEnv] = useState(() => getEnvironment());
  const audioRef = useRef(null);

  useEffect(() => {
    function handleEnvChange(e) {
      if (e.detail) {
        setActiveEnv(getEnvironment(e.detail));
      }
    }
    window.addEventListener("roamgenie:environment-change", handleEnvChange);
    return () => {
      window.removeEventListener("roamgenie:environment-change", handleEnvChange);
      audioRef.current?.pause();
    };
  }, []);

  async function toggleSound() {
    const audio = audioRef.current;
    if (!audio) return;
    if (soundOn) {
      audio.pause();
      audio.currentTime = 0;
      setSoundOn(false);
      return;
    }
    try {
      await audio.play();
      setSoundOn(true);
    } catch {
      setSoundOn(false);
    }
  }

  return (
    <>
      {showScene && (
        <div className="global-world" aria-hidden="true">
          <ImmersiveScene environment={activeEnv} />
        </div>
      )}
      <audio className="ambient-audio" ref={audioRef} src="/kargil-peaceful-wind.mp3" loop preload="auto" />
      <button
        className={`sound-control ${soundOn ? "is-on" : ""}`}
        type="button"
        onClick={toggleSound}
        aria-pressed={soundOn}
        aria-label={soundOn ? "Mute ambient soundscape" : "Unmute ambient soundscape"}
        title={soundOn ? "Mute soundscape" : "Unmute soundscape"}
      >
        <span className={`speaker-icon ${soundOn ? "" : "is-muted"}`} aria-hidden="true">
          <i />
          <b />
        </span>
      </button>
    </>
  );
}
