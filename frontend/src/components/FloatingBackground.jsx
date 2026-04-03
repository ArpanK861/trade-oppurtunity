import { useEffect, useState } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadFull } from "tsparticles";

const sectors = [
  "Pharmaceuticals", "Technology", "Agriculture", "Textiles", "Automotive",
  "Chemicals", "Steel", "Electronics", "Gems & Jewellery", "Petroleum",
  "Renewable Energy", "Fintech", "Food Processing", "Defence", "Healthcare",
  "Real Estate", "Banking", "Infrastructure", "Telecom", "E-Commerce"
];

// Generate simple SVG data URIs for each sector to use as particle images
const generateSectorImages = () => {
  return sectors.map((text) => {
    const width = text.length * 10 + 60;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="48">
      <rect x="2" y="2" width="${width - 4}" height="44" rx="22" fill="rgba(255, 255, 255, 0.8)" stroke="rgba(148, 163, 184, 0.6)" stroke-width="2"/>
      <circle cx="24" cy="24" r="5" fill="#3B82F6" />
      <text x="40" y="30" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="900" fill="#0f172a">${text}</text>
    </svg>`;
    return {
      src: `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`,
      width: width,
      height: 48
    };
  });
};

export default function FloatingBackground() {
  const [init, setInit] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadFull(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);

  const particlesOptions = {
    background: {
      color: {
        value: "transparent",
      },
    },
    particles: {
      number: {
        value: 50,
        density: {
          enable: true,
          value_area: 800,
        },
      },
      collisions: {
        enable: true,
      },
      shape: {
        type: "image",
        options: {
          image: generateSectorImages(),
        },
      },
      opacity: {
        value: 0.22,
      },
      size: {
        value: { min: 40, max: 70 },
      },
      move: {
        enable: true,
        speed: { min: 0.6, max: 1.2 },
        direction: "none",
        random: true,
        straight: false,
        outModes: {
          default: "bounce",
        },
      },
    },
    interactivity: {
      events: {
        onHover: { enable: false },
        onClick: { enable: false },
        onDiv: {
          enable: false,
          selectors: "#hero-area",
          mode: "repulse"
        }
      },
      modes: {
        repulse: {
          distance: 50,
          factor: 100
        }
      }
    },
    detectRetina: true,
  };

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-[-1]">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-50 opacity-50" />
      {init && (
        <Particles
          id="tsparticles"
          options={particlesOptions}
          className="w-full h-full"
        />
      )}
    </div>
  );
}
