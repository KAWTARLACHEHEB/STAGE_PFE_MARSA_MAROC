import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Instances, Instance, Text, CameraControls, Html } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import { X, ChevronLeft, ChevronRight, Crosshair, Layers, Eye, Box } from 'lucide-react';

// === CONFIGURATION : Couleurs par specialite (alignees sur le dataset) ===
const COLORS = {
  NORMAL:       "#3b82f6",  // DRY STANDARD  -> Bleu
  FRIGO:        "#06b6d4",  // REEFER        -> Cyan
  DANGEREUX:    "#ef4444",  // DANGEREUX IMDG -> Rouge
  CITERNE:      "#f59e0b",  // TANK          -> Ambre
  HORS_GABARIT: "#a855f7",  // OOG / Flat Rack -> Violet
};

// Labels ISO complets pour le panneau de detail
const ISO_LABELS = {
  NORMAL:       'DRY STANDARD',
  FRIGO:        'REEFER',
  DANGEREUX:    'DANGEREUX (IMDG)',
  CITERNE:      'TANK',
  HORS_GABARIT: 'OOG / FLAT RACK',
};

const BOX_W = 2.4;
const BOX_H = 1.1;
const BOX_D = 1.2;

function getSpec(c) {
  return String(c.specialite || c.type || 'NORMAL').toUpperCase().trim();
}

function getColor(spec) {
  const s = String(spec).toUpperCase().trim();
  if (s === 'FRIGO')        return COLORS.FRIGO;
  if (s === 'DANGEREUX')    return COLORS.DANGEREUX;
  if (s === 'HORS_GABARIT') return COLORS.HORS_GABARIT;
  if (s === 'CITERNE')      return COLORS.CITERNE;
  return COLORS.NORMAL;
}


// =====================================================================
// COMPOSANT PRINCIPAL : SPLIT-SCREEN DUAL 3D
// =====================================================================
export default function StackView3D({ zoneName, terminal, onClose, highlightedRef = null }) {
  const [containers, setContainers] = useState([]);
  const [zoneInfo, setZoneInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedAllee, setSelectedAllee] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Charger les conteneurs
        const res = await fetch(`http://127.0.0.1:8000/conteneurs?terminal=${terminal}&zone=${zoneName}`);
        const data = await res.json();
        
        // 2. Charger les infos de la zone (pour max_z)
        const occRes = await fetch(`http://127.0.0.1:8000/occupancy?terminal=${terminal}`);
        const occData = await occRes.json();
        if (occData.zones && occData.zones[zoneName]) {
            setZoneInfo(occData.zones[zoneName]);
        }
        
        setContainers(data);
      } catch (err) {
        console.error("Erreur 3D:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [zoneName, terminal]);

  // Organisation par allée
  const alleeList = useMemo(() => {
    const set = new Set(containers.map(c => String(c.allee).trim()));
    return [...set].sort((a, b) => {
      const na = parseInt(a), nb = parseInt(b);
      if (!isNaN(na) && !isNaN(nb)) return na - nb;
      return a.localeCompare(b);
    });
  }, [containers]);

  // Auto-sélection de l'allée (ou de l'allée du conteneur recherché)
  useEffect(() => {
    if (highlightedRef && containers.length > 0) {
      const target = containers.find(c => 
        c.reference === highlightedRef || String(c.container_id) === String(highlightedRef)
      );
      if (target) {
        setSelectedAllee(String(target.allee).trim());
        return;
      }
    }
    
    if (!selectedAllee && alleeList.length > 0) {
      setSelectedAllee(alleeList[0]);
    }
  }, [alleeList, selectedAllee, highlightedRef, containers]);

  // Navigation
  const alleeIndex = alleeList.indexOf(selectedAllee);
  const navigateAllee = useCallback((dir) => {
    const newIdx = alleeIndex + dir;
    if (newIdx >= 0 && newIdx < alleeList.length) {
      setSelectedAllee(alleeList[newIdx]);
    }
  }, [alleeIndex, alleeList]);

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'ArrowRight') navigateAllee(1);
      if (e.key === 'ArrowLeft') navigateAllee(-1);
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [navigateAllee, onClose]);

  // Données 3D pour la vue globale (tous les conteneurs avec positions)
  const globalData = useMemo(() => {
    const posMap = new Map(); // Pour detecter les doublons de position
    
    return containers.map(c => {
      const a = parseInt(c.allee) || 0;
      let pNum = parseInt(c.pile);
      if (isNaN(pNum)) {
        const uniq = [...new Set(containers.map(x => String(x.pile)))].sort();
        pNum = uniq.indexOf(String(c.pile));
      }
      const niv = parseInt(c.niveau_z) || 1;
      const posX = (a % 20) * 3;
      const posZ = pNum * 2.5;
      const posY = (niv - 1) * BOX_H + BOX_H / 2;

      return {
        ...c,
        pos: [posX, posY, posZ],
        color: getColor(getSpec(c), c),
        alleeStr: String(c.allee).trim(),
      };
    });
  }, [containers]);

  // Données 3D pour la travée sélectionnée
  const detailData = useMemo(() => {
    if (!selectedAllee) return [];
    const filtered = containers.filter(c => String(c.allee).trim() === selectedAllee);
    const pileSet = [...new Set(filtered.map(c => String(c.pile).trim()))].sort((a, b) => {
      const na = parseInt(a), nb = parseInt(b);
      if (!isNaN(na) && !isNaN(nb)) return na - nb;
      return a.localeCompare(b);
    });

    const posMap = new Map();

    return filtered.map(c => {
      const pileStr = String(c.pile).trim();
      const pileIdx = pileSet.indexOf(pileStr);
      const niv = parseInt(c.niveau_z) || 1;
      const posX = pileIdx * 4;
      const posY = (niv - 1) * BOX_H + BOX_H / 2;
      const spec = getSpec(c);

      const isHighlighted = highlightedRef && (
        c.reference === highlightedRef ||
        String(c.container_id) === String(highlightedRef) ||
        spec === String(highlightedRef).toUpperCase()
      );
      return {
        ...c,
        pos: [posX, posY, 0],
        color: getColor(spec, c),
        spec,
        pileStr,
        pileIdx,
        isHighlighted,
      };
    });
  }, [containers, selectedAllee, highlightedRef]);

  // Piles uniques pour les labels au sol (vue détaillée)
  const detailPiles = useMemo(() => {
    if (!selectedAllee) return [];
    const filtered = containers.filter(c => String(c.allee).trim() === selectedAllee);
    const pileSet = [...new Set(filtered.map(c => String(c.pile).trim()))].sort((a, b) => {
      const na = parseInt(a), nb = parseInt(b);
      if (!isNaN(na) && !isNaN(nb)) return na - nb;
      return a.localeCompare(b);
    });
    return pileSet;
  }, [containers, selectedAllee]);

  // Allées uniques pour labels au sol (vue globale)
  const globalAllees = useMemo(() => {
    return [...new Set(containers.map(c => parseInt(c.allee) || 0))].sort((a, b) => a - b);
  }, [containers]);

  const totalInAllee = detailData.length;

  if (loading) {
    return (
      <div className="fixed inset-0 z-[100] bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-[#FF8C00] border-t-transparent rounded-full animate-spin" />
          <p className="text-[#FF8C00] font-black uppercase tracking-widest text-xs">Chargement du Bloc {zoneName}...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] bg-slate-950 flex flex-col overflow-hidden">
      {/* ═══ HEADER ═══ */}
      <div className="h-14 border-b border-slate-800 bg-[#020617] flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <div className="bg-[#FF8C00] p-2 rounded-xl">
            <Layers size={16} className="text-white" />
          </div>
          <h2 className="text-base font-black text-white tracking-tighter uppercase">
            Bloc {zoneName} <span className="text-slate-500 text-sm font-normal ml-2">• {terminal} • {containers.length} UTIs</span>
          </h2>
          {/* Légende */}
          <div className="hidden lg:flex items-center gap-3 ml-4 bg-slate-900/60 px-3 py-1.5 rounded-full border border-slate-800">
            {Object.entries(ISO_LABELS).map(([spec, isoLabel]) => (
              <div key={spec} className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: COLORS[spec] }} />
                <span className="text-[7px] font-black text-slate-500 uppercase">{isoLabel}</span>
              </div>
            ))}
          </div>
        </div>
        <button onClick={onClose} className="bg-slate-900 hover:bg-red-500/20 border border-slate-800 p-2.5 rounded-xl transition-all">
          <X className="text-slate-400 hover:text-red-400" size={16} />
        </button>
      </div>

      {/* ═══ SPLIT SCREEN : DEUX CANVAS 3D ═══ */}
      <div className="flex-1 flex overflow-hidden">

        {/* ▓▓▓ GAUCHE : VUE GLOBALE 3D ▓▓▓ */}
        <div className="w-[45%] border-r-2 border-[#FF8C00]/30 relative">
          {/* Label */}
          <div className="absolute top-3 left-3 z-10 bg-black/70 backdrop-blur-sm border border-slate-700 px-3 py-1.5 rounded-xl flex items-center gap-2">
            <Eye size={12} className="text-[#FF8C00]" />
            <span className="text-[9px] font-black text-white uppercase tracking-widest">Vue Globale 3D</span>
          </div>

          <Canvas dpr={1} gl={{ antialias: false, powerPreference: "high-performance" }}
                  camera={{ position: [30, 40, 30], fov: 50 }}>
            <color attach="background" args={["#020617"]} />
            <fog attach="fog" args={["#020617", 50, 200]} />
            <ambientLight intensity={0.5} />
            <directionalLight position={[20, 30, 10]} intensity={1.2} />

            {/* Sol */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
              <planeGeometry args={[300, 300]} />
              <meshLambertMaterial color="#0a0f1a" />
            </mesh>
            <gridHelper args={[200, 40, "#1e293b", "#0f172a"]} position={[0, -0.49, 0]} />

            {/* Labels Allées au sol */}
            {globalAllees.map((a, i) => (
              <Text key={`ga-${i}`} position={[(a % 20) * 3, -0.4, -5]}
                    rotation={[-Math.PI/2, 0, 0]} fontSize={1} color="#475569">
                {`A${a}`}
              </Text>
            ))}

            {/* Conteneurs : highlight l'allée sélectionnée */}
            <GlobalInstances data={globalData} selectedAllee={selectedAllee} onClickAllee={setSelectedAllee} />

            <CameraControls makeDefault minPolarAngle={0.2} maxPolarAngle={Math.PI / 2.3}
                            smoothTime={0.4} maxDistance={120} />
          </Canvas>
        </div>

        {/* ▓▓▓ DROITE : VUE DÉTAILLÉE 3D ▓▓▓ */}
        <div className="flex-1 flex flex-col relative">
          {/* Navigation Allée */}
          <div className="h-12 border-b border-slate-800 bg-[#020617]/90 flex items-center justify-between px-4 shrink-0 z-10">
            <button onClick={() => navigateAllee(-1)} disabled={alleeIndex <= 0}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-white hover:bg-[#FF8C00] disabled:opacity-20 transition-all text-[10px] font-black uppercase tracking-widest">
              <ChevronLeft size={14} /> Préc.
            </button>
            <div className="text-center">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                Allée {alleeIndex + 1} / {alleeList.length}
              </span>
              <div className="text-sm font-black text-white flex items-center gap-2 justify-center">
                <Crosshair size={14} className="text-[#FF8C00]" />
                Allée {selectedAllee}
                <span className="text-xs text-slate-500 font-normal">({totalInAllee} UTIs, {detailPiles.length} piles)</span>
              </div>
            </div>
            <button onClick={() => navigateAllee(1)} disabled={alleeIndex >= alleeList.length - 1}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-white hover:bg-[#FF8C00] disabled:opacity-20 transition-all text-[10px] font-black uppercase tracking-widest">
              Suiv. <ChevronRight size={14} />
            </button>
          </div>

          {/* Canvas 3D Détail */}
          <div className="flex-1 relative">
            {/* Label */}
            <div className="absolute top-3 left-3 z-10 bg-black/70 backdrop-blur-sm border border-slate-700 px-3 py-1.5 rounded-xl flex items-center gap-2">
              <Box size={12} className="text-[#FF8C00]" />
              <span className="text-[9px] font-black text-white uppercase tracking-widest">Vue Détaillée • Allée {selectedAllee}</span>
            </div>

            {/* ────────── NOUVEAU PANNEAU D'INTERFACE FIXE (SIDEBAR) ────────── */}
            <DetailInterfacePanel data={detailData} />

            <Canvas dpr={1} gl={{ antialias: false, powerPreference: "high-performance" }}
                    camera={{ position: [10, 10, 20], fov: 45 }}>
              <color attach="background" args={["#0a0f1a"]} />
              <ambientLight intensity={0.6} />
              <directionalLight position={[10, 15, 10]} intensity={1.5} />
              <pointLight position={[-5, 8, -5]} intensity={0.4} color="#FF8C00" />

              {/* Sol détaillé */}
              <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
                <planeGeometry args={[200, 200]} />
                <meshLambertMaterial color="#0a0f1a" />
              </mesh>
              <gridHelper args={[100, 20, "#1e293b", "#0f172a"]} position={[0, -0.49, 0]} />

              {/* Labels au sol pour chaque pile */}
              {detailPiles.map((p, i) => (
                <group key={`lbl-${i}`}>
                  <Text position={[i * 4, -0.4, 2.5]}
                        rotation={[-Math.PI/2, 0, 0]} fontSize={0.6} color="#64748b">
                    {`Pile ${p}`}
                  </Text>
                  <Text position={[i * 4, -0.4, 3.5]}
                        rotation={[-Math.PI/2, 0, 0]} fontSize={0.4} color="#334155">
                    {`Al.${selectedAllee} Pi.${p}`}
                  </Text>
                  {/* Ligne verticale indicateur pile */}
                  <mesh position={[i * 4, 0, 1.8]}>
                    <boxGeometry args={[0.05, 0.01, 1.5]} />
                    <meshBasicMaterial color="#334155" />
                  </mesh>
                </group>
              ))}

              {/* Conteneurs de l'allée avec détails */}
              <DetailScene data={detailData} detailPiles={detailPiles} selectedAllee={selectedAllee} highlightedRef={highlightedRef} />

              <EffectComposer disableNormalPass>
                <Bloom luminanceThreshold={1.2} mipmapBlur intensity={1.2} />
              </EffectComposer>
            </Canvas>
          </div>

          {/* Barre de coordonnées */}
          <div className="h-8 border-t border-slate-800 bg-[#020617] flex items-center justify-between px-4 shrink-0">
            <span className="text-[8px] font-black text-slate-600 uppercase tracking-widest">
              {terminal} → Bloc {zoneName} → Allée {selectedAllee}
            </span>
            <span className="text-[8px] font-black text-slate-700 uppercase tracking-widest">
              ← → Naviguer • ESC Fermer
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// =====================================================================
// VUE GLOBALE : Instances groupées avec highlight de l'allée active
// =====================================================================
function GlobalInstances({ data, selectedAllee, onClickAllee }) {
  if (data.length === 0) return null;

  const active = data.filter(c => c.alleeStr === selectedAllee);
  const others = data.filter(c => c.alleeStr !== selectedAllee);

  return (
    <group>
      {/* Conteneurs NON sélectionnés : colorés et bien visibles */}
      {others.length > 0 && (
        <Instances limit={13000}>
          <boxGeometry args={[BOX_W * 0.9, BOX_H * 0.8, BOX_D * 0.9]} />
          <meshLambertMaterial transparent opacity={0.7} color="#ffffff" />
          {others.map((c, i) => (
            <Instance key={i} position={c.pos} color={c.color}
              onClick={(e) => { e.stopPropagation(); onClickAllee(c.alleeStr); }}
            />
          ))}
        </Instances>
      )}

      {/* Conteneurs de l'allée SÉLECTIONNÉE (100% opaques + glow) */}
      {active.length > 0 && (
        <Instances limit={2000}>
          <boxGeometry args={[BOX_W, BOX_H, BOX_D]} />
          <meshLambertMaterial
            color="#ffffff"
            emissive="#FF8C00"
            emissiveIntensity={0.6}
            toneMapped={false}
          />
          {active.map((c, i) => (
            <Instance key={i} position={c.pos} color={c.color} />
          ))}
        </Instances>
      )}

      {/* Indicateur au sol de l'allée sélectionnée */}
      {active.length > 0 && (() => {
        const minZ = Math.min(...active.map(c => c.pos[2]));
        const maxZ = Math.max(...active.map(c => c.pos[2]));
        const avgX = active[0].pos[0];
        const centerZ = (minZ + maxZ) / 2;
        const lenZ = maxZ - minZ + 4;
        return (
          <mesh position={[avgX, -0.45, centerZ]} rotation={[-Math.PI/2, 0, 0]}>
            <planeGeometry args={[3.5, lenZ]} />
            <meshBasicMaterial color="#FF8C00" transparent opacity={0.15} />
          </mesh>
        );
      })()}
    </group>
  );
}

// =====================================================================
// VUE DÉTAILLÉE : Scène complète avec zoom au clic
// =====================================================================
function DetailScene({ data, detailPiles, selectedAllee, highlightedRef }) {
  const [selected, setSelected] = useState(null);
  const controlsRef = useRef();

  // Reset sélection quand on change d'allée OU Auto-sélection au chargement
  useEffect(() => { 
    if (highlightedRef) {
      const idx = data.findIndex(c => c.isHighlighted);
      if (idx !== -1) {
        setSelected(idx);
        return;
      }
    }
    setSelected(null); 
  }, [selectedAllee, highlightedRef, data]);

  // Émettre l'événement de sélection pour l'interface HTML
  useEffect(() => {
    window.dispatchEvent(new CustomEvent('container-selected', { detail: selected }));
  }, [selected]);

  // Caméra : zoom sur conteneur cliqué OU vue globale allée
  useEffect(() => {
    if (!controlsRef.current) return;
    if (selected !== null && data[selected]) {
      const c = data[selected];
      controlsRef.current.setLookAt(
        c.pos[0] + 4, c.pos[1] + 3, c.pos[2] + 5,
        c.pos[0], c.pos[1], c.pos[2],
        true
      );
    } else if (detailPiles.length > 0) {
      const centerX = ((detailPiles.length - 1) * 4) / 2;
      const dist = Math.max(detailPiles.length * 3, 12);
      controlsRef.current.setLookAt(
        centerX + dist * 0.5, dist * 0.4, dist * 0.8,
        centerX, 2, 0,
        true
      );
    }
  }, [selected, detailPiles, data]);

  if (data.length === 0) return null;

  return (
    <group>
      {/* Conteneurs */}
      <Instances limit={2000}>
        <boxGeometry args={[BOX_W, BOX_H - 0.05, BOX_D]} />
        <meshLambertMaterial toneMapped={false} color="#ffffff" />
        {data.map((c, i) => (
          <Instance
            key={c.container_id || i}
            position={c.pos}
            color={selected === i ? "#FF8C00" : (c.isHighlighted ? "#facc15" : c.color)}
            onPointerOver={(e) => { e.stopPropagation(); document.body.style.cursor = 'pointer'; }}
            onPointerOut={(e) => { e.stopPropagation(); document.body.style.cursor = 'default'; }}
            onClick={(e) => { e.stopPropagation(); setSelected(selected === i ? null : i); }}
          />
        ))}
      </Instances>

      {/* Anneau lumineux sous le conteneur sélectionné */}
      {selected !== null && data[selected] && (
        <mesh position={[data[selected].pos[0], -0.45, data[selected].pos[2]]} rotation={[-Math.PI/2, 0, 0]}>
          <ringGeometry args={[1.4, 1.7, 32]} />
          <meshBasicMaterial color="#FF8C00" transparent opacity={0.5} />
        </mesh>
      )}

      {/* Anneaux pour conteneurs spéciaux (highlight) */}
      {data.filter(c => c.isHighlighted).map((c, i) => (
        <mesh key={`hl-${i}`} position={[c.pos[0], -0.45, c.pos[2]]} rotation={[-Math.PI/2, 0, 0]}>
          <ringGeometry args={[1.3, 1.5, 24]} />
          <meshBasicMaterial color="#facc15" transparent opacity={0.5} />
        </mesh>
      ))}

      <CameraControls ref={controlsRef} makeDefault
        minPolarAngle={0.1} maxPolarAngle={Math.PI / 2.2}
        smoothTime={0.4} maxDistance={80}
      />
    </group>
  );
}

// =====================================================================
// INTERFACE : Panneau latéral d'informations (Sidebar Fixe)
// =====================================================================
function DetailInterfacePanel({ data }) {
  // On récupère l'index sélectionné depuis un événement personnalisé ou un état partagé
  // Pour faire simple, on va utiliser un Event Listener global
  const [selectedIndex, setSelectedIndex] = useState(null);

  useEffect(() => {
    const handleSelect = (e) => setSelectedIndex(e.detail);
    window.addEventListener('container-selected', handleSelect);
    return () => window.removeEventListener('container-selected', handleSelect);
  }, []);

  if (selectedIndex === null || !data[selectedIndex]) return null;

  const c = data[selectedIndex];

  return (
    <div className="absolute top-3 right-3 bottom-3 w-72 bg-slate-900/95 border border-[#FF8C00]/50 rounded-2xl shadow-2xl backdrop-blur-xl z-20 flex flex-col overflow-hidden animate-in slide-in-from-right duration-300">
      <div className="p-4 border-b border-slate-800 bg-black/20 flex justify-between items-center">
        <span className="text-[10px] font-black text-[#FF8C00] uppercase tracking-widest">Caractéristiques UTI</span>
        <button onClick={() => setSelectedIndex(null)} className="text-slate-500 hover:text-white transition-colors">
          <X size={14} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* Header Référence */}
        <div>
          <span className="text-[8px] font-black text-slate-500 uppercase tracking-[0.2em]">Reference Conteneur</span>
          <h3 className="text-2xl font-black text-white tracking-tighter">{c.reference}</h3>
        </div>

        {/* Grille de stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
            <span className="text-[8px] font-bold text-slate-500 uppercase block mb-1">Position</span>
            <span className="text-xs font-black text-white tracking-widest">Al.{c.allee} Pi.{c.pile}</span>
          </div>
          <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
            <span className="text-[8px] font-bold text-slate-500 uppercase block mb-1">Niveau</span>
            <span className="text-xs font-black text-white tracking-widest">Niveau {c.niveau_z}</span>
          </div>
          <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
            <span className="text-[8px] font-bold text-slate-500 uppercase block mb-1">Type</span>
            <span className="text-xs font-black text-emerald-400 tracking-widest">{c.spec}</span>
          </div>
          <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800">
            <span className="text-[8px] font-bold text-slate-500 uppercase block mb-1">Poids</span>
            <span className="text-xs font-black text-white tracking-widest">{c.weight || 'N/A'} kg</span>
          </div>
        </div>

        {/* Détails Zone et Nouvelles Règles */}
        <div className="space-y-3 pt-2">
          {/* Nouveau: Flux et Statut (Import/Export) */}
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="text-[9px] font-bold text-slate-500 uppercase">Flux Logistique</span>
            <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-sm ${c.flux === 'EXPORT' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {c.flux || 'IMPORT'}
            </span>
          </div>
          
          {c.flux === 'IMPORT' && c.status_douane && (
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Statut Douane</span>
              <span className="text-[10px] font-black text-white uppercase">{c.status_douane}</span>
            </div>
          )}
          
          {c.flux === 'EXPORT' && c.nom_navire && (
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Navire</span>
              <span className="text-[10px] font-black text-fuchsia-400 uppercase">{c.nom_navire}</span>
            </div>
          )}
          
          {c.flux === 'EXPORT' && c.pod && (
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Port (POD)</span>
              <span className="text-[10px] font-black text-sky-400 uppercase">{c.pod}</span>
            </div>
          )}

          {c.type_iso_detail && (
            <div className="flex flex-col gap-1 border-b border-slate-800 pb-2">
              <span className="text-[9px] font-bold text-slate-500 uppercase">Détail ISO</span>
              <span className="text-[10px] font-black text-[#FF8C00] uppercase italic">{c.type_iso_detail}</span>
            </div>
          )}

          <div className="flex justify-between items-center border-b border-slate-800 pb-2 pt-2">
            <span className="text-[9px] font-bold text-slate-500 uppercase">Terminal</span>
            <span className="text-[10px] font-black text-white uppercase">{c.terminal}</span>
          </div>
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="text-[9px] font-bold text-slate-500 uppercase">Zone de Stockage</span>
            <span className="text-[10px] font-black text-white uppercase">{c.zone}</span>
          </div>
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="text-[9px] font-bold text-slate-500 uppercase">Dimension</span>
            <span className="text-[10px] font-black text-white uppercase">{c.size || '20'}' FT</span>
          </div>
        </div>
      </div>

      <div className="p-4 bg-black/20 text-center">
        <p className="text-[8px] font-bold text-slate-600 uppercase tracking-widest">
          Cliquez sur un autre bloc ou dézoomez
        </p>
      </div>
    </div>
  );
}
